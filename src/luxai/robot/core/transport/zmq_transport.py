# src/luxai/robot/core/zmq_transport.py
from __future__ import annotations

import threading
from typing import Any, Dict, Tuple

from luxai.magpie.utils.logger import Logger
from luxai.magpie.transport.zmq.zmq_publisher import ZMQPublisher
from luxai.magpie.transport.zmq.zmq_subscriber import ZMQSubscriber
from luxai.magpie.transport.zmq.zmq_rpc_requester import ZMQRpcRequester

from .transport import Message, Callback, Transport


class ZmqTransport(Transport):
    """
    ZeroMQ-based Transport implementation for Robot SDK.

    Layout (by convention):
      - data_endpoint: robot publishes telemetry / streams (e.g. joints, audio)
      - cmd_endpoint:  SDK publishes commands / streams to robot
      - rpc_endpoint:  RPC services (request/response)
    """

    def __init__(
        self,
        host: str = "192.168.100.1",
        *,
        data_port: int = 50555,
        cmd_port: int = 50556,
        rpc_port: int = 50557,
        rpc_timeout: float = 60.0,
        pub_queue_size: int = 10,
    ) -> None:
        self._host = host
        self._data_endpoint = f"tcp://{host}:{data_port}"
        self._cmd_endpoint = f"tcp://{host}:{cmd_port}"
        self._rpc_endpoint = f"tcp://{host}:{rpc_port}"
        self._rpc_timeout = float(rpc_timeout)

        # One shared publisher for all command topics
        self._publisher = ZMQPublisher(
            endpoint=self._cmd_endpoint,
            bind=False,
            queue_size=pub_queue_size,
        )

        # One ZMQRpcRequester per service_name, each with its own lock
        self._requesters: Dict[str, ZMQRpcRequester] = {}
        self._locks: Dict[str, threading.Lock] = {}

        # One ZMQSubscriber per subscription (topic, callback)
        # key: (topic, callback) -> (subscriber, thread, stop_event)
        self._subscriptions: Dict[Tuple[str, Callback], Tuple[ZMQSubscriber, threading.Thread, threading.Event]] = {}

        Logger.debug(
            f"ZmqTransport connected to host={host} "
            f"(data={self._data_endpoint}, cmd={self._cmd_endpoint}, rpc={self._rpc_endpoint})"
        )

    # ------------------------------------------------------------------
    # RPC
    # ------------------------------------------------------------------
    def preallocate_requesters(self, service_names: list[str]) -> None:
        """
        Optional preallocation of ZMQRpcRequester instances for known services.
        Also allocates a per-service lock for concurrency safety.
        """
        for name in service_names:
            if name in self._requesters:
                continue
            self._requesters[name] = ZMQRpcRequester(
                endpoint=self._rpc_endpoint,
                name=f"RpcRequester:{name}",
            )
            self._locks[name] = threading.Lock()

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
        requester = self._requesters.get(service_name)
        if requester is None:
            requester = ZMQRpcRequester(
                endpoint=self._rpc_endpoint,
                name=f"RpcRequester:{service_name}",
            )
            self._requesters[service_name] = requester
            self._locks[service_name] = threading.Lock()

        lock = self._locks[service_name]
        rpc_req = {"name": service_name, "args": args or {}}
        eff_timeout = timeout if timeout is not None else self._rpc_timeout

        Logger.debug(f"ZmqTransport.call_rpc: {service_name} (timeout={eff_timeout})")
        with lock:
            return requester.call(rpc_req, timeout=eff_timeout)

    # ------------------------------------------------------------------
    # Publish (SDK -> robot)
    # ------------------------------------------------------------------
    def publish(self, topic: str, message: Message) -> None:
        """
        Publish a one-way message to a topic via the shared ZMQPublisher.
        """
        Logger.debug(f"ZmqTransport.publish: topic={topic}")
        self._publisher.write(message, topic)

    # ------------------------------------------------------------------
    # Subscribe / Unsubscribe (robot -> SDK), callback-based
    # ------------------------------------------------------------------
    def subscribe(self, topic: str, callback: Callback) -> None:
        """
        Subscribe to a topic; callback will be invoked with the decoded message dict.

        Internally, this:
          - creates one ZMQSubscriber for the given topic
          - starts a background thread that calls .read() in a loop
          - dispatches messages to the callback
        """
        key = (topic, callback)
        if key in self._subscriptions:
            Logger.debug(f"ZmqTransport.subscribe: already subscribed to {topic} with {callback}")
            return

        subscriber = ZMQSubscriber(
            endpoint=self._data_endpoint,
            topic=topic,
            bind=False,
            queue_size=10,
            delivery="reliable",
        )
        stop_event = threading.Event()

        def _worker() -> None:
            Logger.debug(f"ZmqTransport subscriber worker started for topic={topic}")
            try:
                while not stop_event.is_set():
                    item = subscriber.read(timeout=0.5)
                    if item is None:
                        continue
                    data, _topic = item  # ZMQSubscriber.read() returns (payload, topic_str)
                    try:
                        callback(data)
                    except Exception as e:
                        Logger.warning(f"ZmqTransport.subscribe: callback error for topic={topic}: {e}")
            finally:
                Logger.debug(f"ZmqTransport subscriber worker exiting for topic={topic}")

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

        self._subscriptions[key] = (subscriber, thread, stop_event)
        Logger.debug(f"ZmqTransport.subscribe: subscribed to {topic} with callback={callback}")

    def unsubscribe(self, topic: str, callback: Callback | None = None) -> None:
        """
        Remove a subscription.

        If callback is None, this removes all subscriptions for the topic.
        Otherwise, it removes only the (topic, callback) pair.
        """
        if callback is not None:
            key = (topic, callback)
            entry = self._subscriptions.pop(key, None)
            if entry is None:
                return
            subscriber, thread, stop_event = entry
            stop_event.set()
            subscriber.close()  # StreamReader.close() → ZMQSubscriber._transport_close()
            Logger.debug(f"ZmqTransport.unsubscribe: unsubscribed from {topic} for callback={callback}")
            return

        # Remove all subscriptions for this topic
        to_remove = [k for k in self._subscriptions.keys() if k[0] == topic]
        for key in to_remove:
            subscriber, thread, stop_event = self._subscriptions.pop(key)
            stop_event.set()
            subscriber.close()
            Logger.debug(f"ZmqTransport.unsubscribe: unsubscribed from {topic} for callback={key[1]}")

    # ------------------------------------------------------------------
    # Reader / Writer factory
    # ------------------------------------------------------------------
    class _TopicWriter:
        """
        Simple wrapper that binds a topic to the shared ZMQPublisher,
        exposing a .write(message) method for SDK stream APIs.
        """

        def __init__(self, publisher: ZMQPublisher, topic: str) -> None:
            self._publisher = publisher
            self._topic = topic

        def write(self, message: Message) -> None:
            self._publisher.write(message, self._topic)

    def make_reader(self, topic: str, *, queue_size: int = 1) -> ZMQSubscriber:
        """
        Create and return a ZMQSubscriber for the given topic.

        The caller is responsible for calling .read(timeout) and .close().
        """
        Logger.debug(f"ZmqTransport.make_reader: topic={topic}, queue_size={queue_size}")
        return ZMQSubscriber(
            endpoint=self._data_endpoint,
            topic=topic,
            bind=False,
            queue_size=queue_size,
            delivery="reliable",
        )

    def make_writer(self, topic: str, *, queue_size: int = 1) -> _TopicWriter:
        """
        Create and return a simple writer bound to a topic.

        Note:
            queue_size is currently ignored because we use one shared ZMQPublisher
            configured at transport construction time.
        """
        Logger.debug(f"ZmqTransport.make_writer: topic={topic}, queue_size={queue_size}")
        return ZmqTransport._TopicWriter(self._publisher, topic)

    # ------------------------------------------------------------------
    # Close
    # ------------------------------------------------------------------
    def close(self) -> None:
        """
        Close all underlying resources: subscriptions, requesters, publisher.
        """
        Logger.debug("ZmqTransport.close: closing transport")

        # Stop subscribers
        for key, (subscriber, thread, stop_event) in list(self._subscriptions.items()):
            stop_event.set()
            subscriber.close()
        self._subscriptions.clear()

        # Close requesters
        for name, requester in list(self._requesters.items()):
            try:
                requester.close()
            except Exception:
                pass
        self._requesters.clear()
        self._locks.clear()

        # Close publisher
        try:
            self._publisher.close()
        except Exception:
            pass

        Logger.debug("ZmqTransport.close: done")
