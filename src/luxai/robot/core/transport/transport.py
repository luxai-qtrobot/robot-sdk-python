# src/luxai/robot/core/transport.py
from __future__ import annotations

from typing import Any, Dict, Protocol, runtime_checkable

from luxai.magpie.transport import RpcRequester
from luxai.magpie.transport import StreamReader
from luxai.magpie.transport import StreamWriter


TransportsMeta = Dict[str, Dict[str, Any]]  # e.g. {"zmq": {...}, "mqtt": {...}}


class UnsupportedAPIError(RuntimeError):
    """
    Raised when an RPC or stream is not supported by this robot/transport.

    Used for:
      - APIs that are not present in the robot's description.
      - APIs that exist, but are not available over the current transport
        (e.g. no 'zmq' entry for ZmqTransport).
    """
    pass


@runtime_checkable
class Transport(Protocol):
    """
    Abstract transport used by Robot.

    This is intentionally thin and aligned with magpie primitives:
      - RpcRequester  : request/response services
      - StreamReader  : incoming streams (robot -> SDK)
      - StreamWriter  : outgoing streams (SDK -> robot)

    Robot stays transport-agnostic and just forwards the 'transports' block
    from SYSTEM_DESCRIPTION. Each concrete Transport implementation decides
    how to interpret that structure (e.g. 'zmq', 'mqtt', etc.).
    """

    def get_requester(
        self,
        service_name: str,
        transports: TransportsMeta | None,
    ) -> RpcRequester:
        """
        Return a transport-specific requester for this RPC.

        - service_name: "/qt_robot/speech/say"
        - transports: transport block from SYSTEM_DESCRIPTION for this service,
                      or None for the initial SYSTEM_DESCRIBE_SERVICE etc.

        Raises:
            UnsupportedAPIError if this RPC is not available over this transport.
        """
        ...


    def get_stream_reader(
        self,
        topic: str,
        transports: TransportsMeta,
        queue_size: int | None = None,
    ) -> StreamReader:
        """
        Create a StreamReader for a given topic.

        - topic: logical topic name (e.g. "/qt_robot/joints/state")
        - transports: the 'transports' dict for this stream
        - queue_size: optional user override; if None, the transport may use
          a value from transports meta or its own default.

        Implementations may raise UnsupportedAPIError if this stream is not
        available over the current transport.
        """
        ...

    def get_stream_writer(
        self,
        topic: str,
        transports: TransportsMeta,
        queue_size: int | None = None,
    ) -> StreamWriter:
        """
        Create a StreamWriter for a given topic.

        Implementations may raise UnsupportedAPIError if this stream is not
        writable over the current transport.
        """
        ...

    def close(self) -> None:
        """Close underlying resources (sockets, clients, etc.)."""
        ...


@runtime_checkable
class SupportsPreallocation(Protocol):
    """
    Optional interface for transports that can pre-create RPC requesters
    based on the robot's RPC routes.
    """

    def preallocate_requesters(
        self,
        rpc_routes: Dict[str, Dict[str, Any]],
    ) -> None:
        """
        rpc_routes:
          service_name -> {
              "service_name": str,
              "transports": { ... },
              "deprecated": bool,
              "experimental": bool,
          }
        """
        ...
