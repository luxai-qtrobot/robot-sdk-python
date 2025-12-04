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
from luxai.magpie.discovery import ZconfDiscovery, NodeInfo  # adjust path if needed

from .transport import Transport, SupportsPreallocation, TransportsMeta, UnsupportedAPIError


def _parse_tcp_endpoint(endpoint: str) -> tuple[str, int]:
    if not endpoint.startswith("tcp://"):
        raise ValueError(f"Unsupported endpoint scheme: {endpoint!r}")
    host_port = endpoint[len("tcp://") :]
    if ":" not in host_port:
        raise ValueError(f"Endpoint must be tcp://host:port, got {endpoint!r}")
    host, port_str = host_port.rsplit(":", 1)
    return host, int(port_str)



class ZmqTransport(Transport, SupportsPreallocation):
    """
    ZMQ-based Transport implementation.

    Responsibilities:
      - Understand the 'zmq' entry inside the 'transports' dict for each
        service/stream.
      - Resolve endpoints (including wildcard host and optional node_id via
        Zeroconf).
      - Manage ZMQRpcRequester / ZMQSubscriber / ZMQPublisher instances.

    Robot never deals with endpoints, node_id, or Zeroconf directly.
    """

    _DEFAULT_QUEUE_SIZE = 10                # used when neither user nor IDL specify queue size
    _zconf: ZconfDiscovery | None = None    # a singleton instance of ZconfDiscovery

    @classmethod
    def _get_discovery(cls) -> ZconfDiscovery:
        if cls._zconf is None:
            cls._zconf = ZconfDiscovery()
        return cls._zconf

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        node_id: str | None = None,
        discovery_timeout: float = 5.0,
    ) -> None:
        """
        Args:
            endpoint: Optional default RPC endpoint, e.g. "tcp://192.168.3.173:50557".
            node_id: Optional Zeroconf node_id to resolve the default endpoint.
            discovery_timeout: Used only if node_id is provided.
        """
        if endpoint is None and node_id is None:
            raise ValueError("ZmqTransport requires either 'endpoint' or 'node_id'.")

        if endpoint is not None:
            # Use given endpoint as default RPC endpoint
            self._default_rpc_endpoint = endpoint
            host, _ = _parse_tcp_endpoint(endpoint)
            self._default_host = host
        else:
            # Resolve via Zeroconf
            disc = self._get_discovery()
            info: Optional[NodeInfo] = disc.resolve_node(node_id, timeout=discovery_timeout)
            if info is None:
                raise RuntimeError(f"ZmqTransport: node_id={node_id!r} not found via ZconfDiscovery.")
            ip = disc.pick_best_ip(info)
            if not ip:
                raise RuntimeError(
                    f"ZmqTransport: node_id={node_id!r} has no usable IPs: {info.ips}"
                )
            # Use the node's advertised port as default RPC endpoint
            self._default_rpc_endpoint = f"tcp://{ip}:{info.port}"
            self._default_host = ip

        # (service_name, endpoint) -> ZMQRpcRequester
        self._requesters: Dict[Tuple[str, str], ZMQRpcRequester] = {}
        self._stream_resources: list[object] = []   

        self._lock_global = threading.Lock()
        self._closed = False

        Logger.debug(
            f"ZmqTransport: default RPC endpoint is {self._default_rpc_endpoint}"
        )

    def _get_or_create_requester(self, service_name: str, endpoint: str) -> RpcRequester:
        """Return cached ZMQRpcRequester per (service_name, endpoint)."""
        key = (service_name, endpoint)
        with self._lock_global:
            requester = self._requesters.get(key)
            if requester is not None:
                return requester

            requester = ZMQRpcRequester(
                endpoint=endpoint,
                name=f"RpcRequester:{service_name}",
            )
            self._requesters[key] = requester            

            Logger.debug(
                f"ZmqTransport: created ZMQRpcRequester for {service_name} at {endpoint}"
            )
            return requester

    # ------------------------------------------------------------------
    # RPCs
    # ------------------------------------------------------------------
    def get_requester(self, service_name: str, transports: TransportsMeta | None) -> RpcRequester:
        if self._closed:
            raise RuntimeError("ZmqTransport is closed")

        if transports is None:
            endpoint = self._default_rpc_endpoint
        else:
            zmq_info = transports.get("zmq")
            if not zmq_info:
                raise UnsupportedAPIError( f"Service {service_name!r} is not available over ZMQ.")
            endpoint = self._resolve_endpoint_from_info(zmq_info)

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
            raise RuntimeError("ZmqTransport is closed")

        zmq_info = transports.get("zmq")
        if not zmq_info:
            raise UnsupportedAPIError(f"Stream {topic!r} is not available over ZMQ.")

        endpoint = self._resolve_endpoint_from_info(zmq_info)
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
            f"ZmqTransport: created ZMQSubscriber for topic={topic!r} at {endpoint}, "
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
            raise RuntimeError("ZmqTransport is closed")

        zmq_info = transports.get("zmq")
        if not zmq_info:
            raise UnsupportedAPIError(
                f"Stream {topic!r} is not writable over ZMQ."
            )

        endpoint = self._resolve_endpoint_from_info(zmq_info)
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
            f"ZmqTransport: created ZMQPublisher for {topic!r} at {endpoint}, "
            f"queue_size={qsize}, delivery={delivery}, bind={bind}"            
        )
        self._stream_resources.append(pub)
        return pub

    # ------------------------------------------------------------------
    # Preallocation
    # ------------------------------------------------------------------
    def preallocate_requesters(
        self,
        rpc_routes: Dict[str, Dict[str, Any]],
    ) -> None:
        """
        Pre-create requesters for all RPC routes that have a 'zmq' transport.
        rpc_routes: service_name -> { "service_name", "transports", ... }
        """
        if self._closed:
            return

        for service_name, route in rpc_routes.items():
            transports = route.get("transports") or {}            
            try:
                # endpoint = self._resolve_endpoint_from_info(zmq_info)
                self.get_requester(service_name, transports)
            except Exception as e:
                Logger.warning( f"ZmqTransport: failed to preallocate requester for {service_name} at zmq transport: {e}")


    # ------------------------------------------------------------------
    # Endpoint resolution helper
    # ------------------------------------------------------------------
    def _resolve_endpoint_from_info(self, zmq_info: Dict[str, Any]) -> str:
        """
        Resolve endpoint from a 'zmq' transport info dict.

        Fields:
          - endpoint: e.g. "tcp://*:50557" or "tcp://1.2.3.4:50557"
          - node_id: optional, if the stream/RPC lives on another node
        """
        endpoint = zmq_info.get("endpoint") or self._default_rpc_endpoint
        node_id = zmq_info.get("node_id")

        if not endpoint.startswith("tcp://"):
            return endpoint  # we don't try to "fix" non-tcp URIs

        host_port = endpoint[len("tcp://") :]
        if ":" not in host_port:
            return endpoint

        host, port_str = host_port.rsplit(":", 1)

        if host != "*":
            return endpoint  # already concrete

        # host == "*" → need to substitute a real IP
        if node_id:
            disc = self._get_discovery()
            info = disc.resolve_node(node_id, timeout=3.0)
            if info is None:
                Logger.warning(
                    f"ZmqTransport: could not resolve node_id={node_id}, "
                    f"using default host {self._default_host!r}."
                )
                chosen_host = self._default_host
            else:
                ip = disc.pick_best_ip(info)
                if not ip:
                    Logger.warning(
                        f"ZmqTransport: node_id={node_id} has no usable IPs, "
                        f"using default host {self._default_host!r}."
                    )
                    chosen_host = self._default_host
                else:
                    chosen_host = ip
        else:
            chosen_host = self._default_host

        return f"tcp://{chosen_host}:{port_str}"


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
                        f"ZmqTransport: closed ZMQRpcRequester for {key[0]} at {key[1]}"
                    )
                except Exception as e:
                    Logger.warning(
                        f"ZmqTransport: error closing requester {key}: {e}"
                    )
            self._requesters.clear()

        self._closed = True
