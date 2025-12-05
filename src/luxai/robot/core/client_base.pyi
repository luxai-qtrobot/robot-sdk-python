from __future__ import annotations

from typing import Any, Dict, TypeVar, Callable
from luxai.robot.core.transport import Transport
from luxai.robot.core.actions import ActionHandle
from luxai.robot.core.frames import *
from luxai.magpie.frames import *
from .typed_stream import TypedStreamReader, TypedStreamWriter


F = TypeVar("F", bound="Frame")


class StreamSubscription:
    """Handle for an active stream subscription."""

    def cancel(self) -> None:
        """Unsubscribe from the stream."""
        ...
        

class Robot:
    """Type stub for Robot client (manual core methods)."""

    @classmethod
    def connect_zmq(
        cls,
        *,
        endpoint: str | None = None,
        node_id: str | None = None,
        connect_timeout: float = 5.0,
        default_rpc_timeout: float | None = None,
    ) -> Robot:
        ...

    def __init__(
        self,
        transport: Transport,
        *,
        default_rpc_timeout: float | None = None,
    ) -> None:
        ...

    
    def close(self) -> None:
        ...

    def get_stream_reader(
        self,
        topic: str,
        *,
        queue_size: int | None = None,
        frame_type: type[F]
    ) -> TypedStreamReader[F]:
        ...

    def get_stream_writer(
        self,
        topic: str,
        *,
        queue_size: int | None = None,
    ) -> TypedStreamWriter[F]: 
        ...

    def rpc_call(
        self,
        service_name: str,
        args: Dict[str, Any],
        timeout: float | None,
    ) -> Dict[str, Any]:
        ...

    # --- AUTO-GENERATED ROBOT NAMESPACES ---
