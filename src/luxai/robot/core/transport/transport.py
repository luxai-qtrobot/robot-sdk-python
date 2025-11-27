# src/luxai/robot/core/transport.py
from __future__ import annotations

from typing import Any, Callable, Dict, Protocol

Message = Dict[str, Any]
Callback = Callable[[Message], None]


class Transport(Protocol):
    """
    Abstract messaging transport used by Robot.

    This is intentionally aligned with magpie:
    - call_rpc: request/response services
    - publish: one-way commands
    - subscribe/unsubscribe: streaming data
    """

    def call_rpc(
        self,
        service_name: str,
        args: Message,
        timeout: float | None = None,
    ) -> Message:
        """
        Call a robot service via RPC.

        Raises:
            RuntimeError, TimeoutError, or other transport-level exceptions.
        """
        ...

    def publish(self, topic: str, message: Message) -> None:
        """Publish a one-way message to a topic."""
        ...

    def subscribe(self, topic: str, callback: Callback) -> None:
        """Subscribe to a topic; callback is called for each received message."""
        ...

    def unsubscribe(self, topic: str, callback: Callback | None = None) -> None:
        """Remove a subscription."""
        ...

    def close(self) -> None:
        """Close underlying resources."""
        ...

# Optional interface — only ZMQ implements this.
class SupportsPreallocation(Protocol):
    def preallocate_requesters(self, service_names: list[str]) -> None:
        ...

