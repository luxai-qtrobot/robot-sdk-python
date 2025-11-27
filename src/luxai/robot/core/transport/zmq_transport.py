
# src/luxai/robot/core/transport/zmq_transport.py
from __future__ import annotations
from typing import Any, Dict, Callable, List
import threading


from luxai.magpie.transport import ZMQPublisher
from luxai.magpie.transport import ZMQSubscriber
from luxai.magpie.transport import ZMQRpcRequester
from luxai.magpie.utils import Logger

from .transport import Transport, Callback, Message

class ZmqTransport(Transport):
    """
    ZMQ-based transport for Robot using magpie.

    - One ZMQPublisher for commands / control topics
    - One ZMQSubscriber for robot data
    - One ZMQRpcRequester per service_name, reused and guarded by a lock
    """

    def __init__(
        self,
        host: str,
        *,
        data_port: int = 50555,
        cmd_port: int = 50556,
        rpc_port: int = 50557,
    ) -> None:
        endpoint_data = f"tcp://{host}:{data_port}"
        endpoint_cmd = f"tcp://{host}:{cmd_port}"
        self._rpc_endpoint = f"tcp://{host}:{rpc_port}"

        # Publisher for commands / control topics
        self._publisher = ZMQPublisher(
            endpoint=endpoint_cmd,
            bind=False,
            queue_size=10,
        )

        # Subscriber for incoming robot data
        self._subscriber = ZMQSubscriber(
            endpoint=endpoint_data,
            topic=[],   # topics will be added dynamically
            bind=False,
        )

        self._subscriptions: dict[str, list[Callback]] = {}
        self._subscriber_started = False

        # Per-service requesters and locks
        self._requesters: dict[str, ZMQRpcRequester] = {}
        self._locks: dict[str, "threading.Lock"] = {}


    # Preallocate RPC requesters
    # ----------------------------------------------------
    def preallocate_requesters(self, service_names: list[str]) -> None:
        """
        Pre-create ZMQRpcRequester for each known service_name.
        Useful to remove first-call latency.
        """
        for name in service_names:
            if name not in self._requesters:
                self._requesters[name] = ZMQRpcRequester(
                    endpoint=self._rpc_endpoint,
                    name=f"RpcRequester:{name}"
                )
                self._locks[name] = threading.Lock()

    # ---------------- RPC ----------------
    def call_rpc(
        self,
        service_name: str,
        args: Message,
        timeout: float | None = None,
    ) -> Message:
        """
        Reuse a dedicated ZMQRpcRequester per service_name.
        Each requester is guarded by its own lock to avoid concurrent calls
        on the same requester.
        """
        import threading
        requester = self._requesters.get(service_name)
        if requester is None:
            requester = ZMQRpcRequester(
                endpoint=self._rpc_endpoint,
                name=f"RpcRequester:{service_name}",
            )
            self._requesters[service_name] = requester
            self._locks[service_name] = threading.Lock()

        lock = self._locks[service_name]
        rpc_req = {"name": service_name, "args": args}
        with lock:
            return requester.call(rpc_req, timeout=timeout)

    # ---------------- PUB/SUB ----------------
    def publish(self, topic: str, message: Message) -> None:
        self._publisher.write(message, topic)

    def subscribe(self, topic: str, callback: Callback) -> None:
        """
        Register a callback for a topic and make sure the underlying
        ZMQSubscriber is configured and running.
        """
        self._subscriptions.setdefault(topic, []).append(callback)

        # Tell magpie subscriber to subscribe to that topic
        self._subscriber.add_topic(topic)

        # Start reader loop lazily
        if not self._subscriber_started:
            self._start_subscriber_loop()

    def unsubscribe(self, topic: str, callback: Callback | None = None) -> None:
        callbacks = self._subscriptions.get(topic)
        if not callbacks:
            return

        if callback is None:
            callbacks.clear()
        else:
            try:
                callbacks.remove(callback)
            except ValueError:
                pass

        # Optional: if callbacks list is empty, you could remove topic from subscriber
        # if not callbacks:
        #     self._subscriber.remove_topic(topic)

    def _start_subscriber_loop(self) -> None:
        """
        Start a background thread to read from ZMQSubscriber and
        dispatch messages to registered callbacks.
        """
        import threading

        def _loop():
            Logger.info("ZmqTransport: subscriber loop started")
            while True:
                msg = self._subscriber.read()
                if msg is None:
                    continue
                data, topic = msg
                for cb in self._subscriptions.get(topic, []):
                    try:
                        cb(data)
                    except Exception as e:
                        Logger.warning(
                            f"ZmqTransport: callback error for {topic}: {e}"
                        )

        t = threading.Thread(target=_loop, daemon=True)
        t.start()
        self._subscriber_started = True

    def close(self) -> None:
        try:
            self._publisher.close()
        except Exception:
            pass
        try:
            self._subscriber.close()
        except Exception:
            pass
        for requester in self._requesters.values():
            try:
                requester.close()
            except Exception:
                pass
