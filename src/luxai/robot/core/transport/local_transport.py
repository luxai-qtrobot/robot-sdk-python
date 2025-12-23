# src/luxai/robot/core/zmq_transport.py
from __future__ import annotations

import threading
from typing import Any, Dict, Tuple, Optional

from luxai.magpie.utils import Logger
from luxai.magpie.transport import RpcRequester
from luxai.magpie.transport import StreamReader
from luxai.magpie.transport import StreamWriter
from luxai.magpie.transport import ZMQRpcRequester
from luxai.magpie.transport import ZMQSubscriber
from luxai.magpie.transport import ZMQPublisher

from .transport import Transport,TransportsMeta, UnsupportedAPIError


class LocalTransport(Transport):
    """
    Local-based Transport implementation using inproc:// ZMQ endpoints.

    Responsibilities:
    - Manage ZMQRpcRequesters and ZMQSubscriber/ZMQPublisher instances      
    - Provide get_requester(), get_stream_reader(), get_stream_writer() methods.
    """

    _DEFAULT_QUEUE_SIZE = 10                # used when neither user nor IDL specify queue size

    def __init__(self) -> None:
        """
        Args:
            no  args
        """

        # endpoint -> ZMQRpcRequester
        self._requesters: Dict[str, ZMQRpcRequester] = {}
        self._stream_resources: list[object] = []   

        self._lock_global = threading.Lock()
        self._closed = False


    def _get_or_create_requester(self, service_name: str, endpoint: str) -> RpcRequester:
        """Return cached ZMQRpcRequester per (service_name, endpoint)."""
        # key = (service_name, endpoint)
        key = endpoint
        with self._lock_global:            
            requester = self._requesters.get(key)
            if requester is not None:
                return requester

            requester = ZMQRpcRequester(
                endpoint=endpoint,
                name=f"RpcRequester:{endpoint}",
            )
            self._requesters[key] = requester            

            Logger.debug(
                f"LocalTransport: created ZMQRpcRequester for {service_name} at {endpoint}"
            )
            return requester

    # ------------------------------------------------------------------
    # RPCs
    # ------------------------------------------------------------------
    def get_requester(self, service_name: str, transports: TransportsMeta | None) -> RpcRequester:
        if self._closed:
            raise RuntimeError("LocalTransport is closed")

        if transports is None:
            raise UnsupportedAPIError(f" No transport info for Service {service_name!r}.")

        endpoint = transports.get("zmq", {}).get("endpoint")
        if not endpoint:
            raise UnsupportedAPIError(f"Service {service_name!r} is not available over local ZMQ.")

        return self._get_or_create_requester(service_name, endpoint)


    # ------------------------------------------------------------------
    # Streams
    # ------------------------------------------------------------------
    def get_stream_reader(
        self,
        topic: str,
        transports: TransportsMeta,
        queue_size: int | None = None,
    ) -> StreamReader:
        """
        Create a ZMQSubscriber for the given topic based on the 'zmq' entry.

        Queue size precedence:
          1) user-provided queue_size (if not None)
          2) zmq_info["queue_size"] from SYSTEM_DESCRIPTION (if present)
          3) DEFAULT_QUEUE_SIZE
        """
        if self._closed:
            raise RuntimeError("LocalTransport is closed")

        zmq_info = transports.get("zmq", {})
        endpoint = zmq_info.get("endpoint")
        if not endpoint:
            raise UnsupportedAPIError(f"Stream {topic!r} is not available over local ZMQ.")
        
        delivery = str(zmq_info.get("delivery", "reliable"))
        bind = bool(zmq_info.get("bind", False))

        if queue_size is not None:
            qsize = int(queue_size)
        else:
            qsize = int(zmq_info.get("queue_size", self._DEFAULT_QUEUE_SIZE))

        sub = ZMQSubscriber(
            endpoint=endpoint,
            topic=topic,
            queue_size=qsize,
            bind=bind,
            delivery=delivery,
        )

        Logger.debug(
            f"LocalTransport: created ZMQSubscriber for topic={topic!r} at {endpoint}, "
            f"queue_size={qsize}, delivery={delivery}, bind={bind}"
        )
        self._stream_resources.append(sub)
        return sub

    def get_stream_writer(
        self,
        topic: str,
        transports: TransportsMeta,
        queue_size: int | None = None,
    ) -> StreamWriter:
        """
        Create a ZMQPublisher for the given stream, based on the 'zmq' entry.

        Queue size precedence:
          1) user-provided queue_size (if not None)
          2) zmq_info["queue_size"] from SYSTEM_DESCRIPTION (if present)
          3) self._DEFAULT_QUEUE_SIZE
        """
        if self._closed:
            raise RuntimeError("LocalTransport is closed")

        zmq_info = transports.get("zmq", {})
        endpoint = zmq_info.get("endpoint")
        if not endpoint:
            raise UnsupportedAPIError(f"Stream {topic!r} is not available over local ZMQ.")

        bind = bool(zmq_info.get("bind", False))
        delivery = str(zmq_info.get("delivery", "reliable"))

        if queue_size is not None:
            qsize = int(queue_size)
        else:
            qsize = int(zmq_info.get("queue_size", self._DEFAULT_QUEUE_SIZE))

        pub = ZMQPublisher(
            endpoint=endpoint,
            queue_size=qsize,
            bind=bind,
            delivery=delivery,
        )

        Logger.debug(
            f"LocalTransport: created ZMQPublisher for {topic!r} at {endpoint}, "
            f"queue_size={qsize}, delivery={delivery}, bind={bind}"            
        )
        self._stream_resources.append(pub)
        return pub


    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def close(self) -> None:
        if self._closed:
            return        

        for streamer in self._stream_resources:
            try:
                streamer.close()
            except Exception:
                pass            
        self._stream_resources.clear()        

        with self._lock_global:
            for key, requester in list(self._requesters.items()):
                try:
                    requester.close()
                    Logger.debug(
                        f"LocalTransport: closed ZMQRpcRequester for {key}"
                    )
                except Exception as e:
                    Logger.warning(
                        f"LocalTransport: error closing requester {key}: {e}"
                    )
            self._requesters.clear()

        self._closed = True
