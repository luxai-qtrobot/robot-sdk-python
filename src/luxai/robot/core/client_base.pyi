from __future__ import annotations

from typing import Any, Dict
from luxai.robot.core.transport import Transport
from luxai.robot.core.actions import ActionHandle
from luxai.magpie.transport import StreamReader, StreamWriter


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

    def get_stream_reader(self, topic: str, *, queue_size: int | None = None) -> StreamReader:
        ...

    def get_stream_writer(self, topic: str, *, queue_size: int | None = None) -> StreamWriter:
        ...

    def rpc_call(
        self,
        service_name: str,
        args: Dict[str, Any],
        timeout: float | None,
    ) -> Dict[str, Any]:
        ...

    # --- AUTO-GENERATED ROBOT NAMESPACES ---
