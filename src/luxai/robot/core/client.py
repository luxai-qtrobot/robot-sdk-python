# src/luxai/robot/core/client.py
from __future__ import annotations

from typing import Any, Dict, Sequence

from luxai.magpie.utils import Logger


from .actions import ActionHandle
from .transport.transport import Transport
from .transport.zmq_transport import ZmqTransport
from .config import QTROBOT_CORE_APIS, SDK_VERSION, SYSTEM_DESCRIBE_SERVICE


class Robot:
    """
    High-level SDK client for controlling Robot.

    Transport-agnostic: uses a Transport implementation internally (ZMQ today,
    MQTT/Ably/etc in the future).
    """

    def __init__(self, transport: Transport, *, default_timeout: float = None) -> None:
        """
        Low-level constructor; most users should use 'connect_*' helpers.

        Args:
            transport: A concrete Transport instance.
            default_timeout: Default RPC timeout for actions (seconds).
        """
        self._transport = transport
        self._default_timeout = float(default_timeout)

        # Robot capability info (may stay None if handshake fails)
        self._robot_type: str | None = None
        self._robot_version: str | None = None
        self._supported_apis: set[str] | None = None
        self._deprecated_apis: set[str] | None = None
        self._supported_services: set[str] | None = None
        self._deprecated_services: set[str] | None = None
        self._supported_subscribers: set[str] | None = None
        self._supported_publishers: set[str] | None = None


        # Preallocate RPC requesters if the transport supports it
        try:
            from .config import QTROBOT_CORE_APIS
            service_names = []
            for spec in QTROBOT_CORE_APIS.values():
                service_names.append(spec["service_name"])
                if spec.get("cancel_service_name"):
                    service_names.append(spec["cancel_service_name"])

            self._transport.preallocate_requesters(service_names)

        except (ImportError, AttributeError):
            # Transport does NOT implement preallocation — this is OK (MQTT, Ably, etc.)
            pass

        # ---- Optional handshake with robot ----
        self._handshake_with_robot()


    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------
    @classmethod
    def connect_zmq(
        cls,
        host: str,
        *,
        data_port: int = 50555,
        cmd_port: int = 50556,
        rpc_port: int = 50557,
        default_timeout: float = None,
    ) -> "Robot":
        """
        Create a Robot client using ZMQ/magpie transport.

        Example:
            robot = Robot.connect_zmq("192.168.3.10")
        """
        transport = ZmqTransport(
            host=host,
            data_port=data_port,
            cmd_port=cmd_port,
            rpc_port=rpc_port,
        )
        return cls(transport=transport, default_timeout=default_timeout)

    def close(self) -> None:
        """Close the underlying transport and free resources."""
        self._transport.close()

    # ------------------------------------------------------------------
    # Low-level generic calls (escape hatch)
    # ------------------------------------------------------------------
    def call_rpc(
        self,
        service_name: str,
        args: Dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Dict[str, Any]:
        """
        Generic RPC escape hatch.

        Normally you should prefer the typed convenience methods, but this
        can be useful for experimentation or advanced use.
        """
        if args is None:
            args = {}
        return self._transport.call_rpc(service_name, args, timeout=timeout)

    def publish(self, topic: str, message: Dict[str, Any]) -> None:
        """Generic publish escape hatch."""
        self._transport.publish(topic, message)

    # ------------------------------------------------------------------
    # Internal helper for starting actions
    # ------------------------------------------------------------------
    def _start_action(
        self,
        service_name: str,
        args: Dict[str, Any],
        *,
        cancel_service_name: str | None = None,
        timeout: float | None = None,
        blocking: bool = False,
    ) -> ActionHandle:
        handle = ActionHandle(
            transport=self._transport,
            service_name=service_name,
            args=args,
            timeout=timeout or self._default_timeout,
            cancel_service_name=cancel_service_name,
        )
        if blocking:
            handle.wait()
        return handle


    def _handshake_with_robot(self) -> None:
        """Internal capability negotiation with robot."""
        try:
            raw = self._transport.call_rpc(
                SYSTEM_DESCRIBE_SERVICE,
                args={"sdk_version": SDK_VERSION},
                timeout=5.0,
            )
            if not raw.get("status"):                
                Logger.warning(
                    "QTrobot: system describe returned status=False; "
                    "capability information may be incomplete."
                )
                return

            info = raw.get("response") or {}
            
            # Basic info
            self._robot_type = info.get("robot_type")
            self._robot_version = info.get("robot_version")

            # ---- Version compatibility (min_sdk / max_sdk) ----
            min_sdk = info.get("min_sdk")
            max_sdk = info.get("max_sdk")

            sdk_v = self._parse_version(SDK_VERSION)            
            if min_sdk:
                if sdk_v < self._parse_version(min_sdk):
                    Logger.warning(
                        f"QTrobot SDK {SDK_VERSION} is older than robot's "
                        f"minimum supported SDK {min_sdk}."
                    )
            if max_sdk:
                if sdk_v > self._parse_version(max_sdk):
                    Logger.warning(
                        f"QTrobot SDK {SDK_VERSION} is newer than robot's "
                        f"maximum tested SDK {max_sdk}."
                    )

            # ---- Services → API names mapping ----
            supported_services = info.get("supported_services")
            if supported_services:
                self._supported_services = set(supported_services)
                self._supported_apis = {
                    api_name
                    for api_name, spec in QTROBOT_CORE_APIS.items()
                    if spec.get("service_name") in self._supported_services
                }

            deprecated_services = info.get("deprecated_services")
            if deprecated_services:
                self._deprecated_services = set(deprecated_services)
                self._deprecated_apis = {
                    api_name
                    for api_name, spec in QTROBOT_CORE_APIS.items()
                    if spec.get("service_name") in self._deprecated_services
                }

            # ---- Topics (for future use) ----
            supported_sub = info.get("supported_subscribers")
            if supported_sub:
                self._supported_subscribers = set(supported_sub)

            supported_pub = info.get("supported_publishers")
            if supported_pub:
                self._supported_publishers = set(supported_pub)

        except Exception as e:            
            Logger.debug(f"QTrobot: system describe not available: {e}")


    def _parse_version(self, v: str) -> tuple[int, int, int]:
        parts = v.split(".")
        parts = (parts + ["0", "0", "0"])[:3]
        try:
            return tuple(int(p) for p in parts)  # type: ignore[return-value]
        except ValueError:
            return (0, 0, 0)

# ----------------------------------------------------------------------
# Attach auto-generated APIs
# ----------------------------------------------------------------------
from .config import QTROBOT_CORE_APIS
from .api_factory import attach_core_apis

attach_core_apis(Robot, QTROBOT_CORE_APIS)
