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
            if raw.get("status"):
                info = raw.get("response") or {}

                self._robot_type = info.get("robot_type")
                self._robot_version = info.get("robot_version")

                supported = info.get("supported_apis")
                if supported:
                    self._supported_apis = set(supported)

                deprecated = info.get("deprecated_apis")
                if deprecated:
                    self._deprecated_apis = set(deprecated)

                min_sdk = info.get("min_sdk")
                max_sdk = info.get("max_sdk")
                if min_sdk and SDK_VERSION < min_sdk:
                    Logger.warning(
                        f"Robot SDK {SDK_VERSION} is older than robot's "
                        f"minimum supported SDK {min_sdk}."
                    )
                if max_sdk and SDK_VERSION > max_sdk:
                    Logger.warning(
                        f"Robot SDK {SDK_VERSION} is newer than robot's "
                        f"maximum tested SDK {max_sdk}."
                    )
            else:
                Logger.warning(
                    "Robot: system describe returned status=False; "
                    "capability information may be incomplete."
                )

        except Exception as e:
            Logger.debug(f"Robot: system describe not available: {e}")


# ----------------------------------------------------------------------
# Attach auto-generated APIs
# ----------------------------------------------------------------------
from .config import QTROBOT_CORE_APIS
from .api_factory import attach_core_apis

attach_core_apis(Robot, QTROBOT_CORE_APIS)
