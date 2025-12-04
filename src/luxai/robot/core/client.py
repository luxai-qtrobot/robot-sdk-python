# src/luxai/robot/core/client.py
from __future__ import annotations

import threading

from typing import Any, Dict, Optional

from luxai.magpie.utils.logger import Logger
from luxai.magpie.transport.stream_reader import StreamReader
from luxai.magpie.transport.stream_writer import StreamWriter

from .actions import ActionHandle
from .transport import Transport, SupportsPreallocation, UnsupportedAPIError, ZmqTransport

from .config import ( QTROBOT_CORE_APIS, SDK_VERSION, SYSTEM_DESCRIBE_SERVICE)


class Robot:
    """
    High-level SDK client for controlling a robot.

    Transport-agnostic:
      - Robot never looks at "zmq", "mqtt", endpoints, node_id, etc.
      - It only stores the 'transports' blocks from SYSTEM_DESCRIPTION and
        forwards them to the Transport object.
    """

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------
    @classmethod
    def connect_zmq(
        cls,
        *,
        endpoint: str | None = None,
        node_id: str | None = None,
        connect_timeout: float = 5.0,
        default_rpc_timeout: float | None = None,
    ) -> Robot:
        """
        Create a Robot client using ZMQ/magpie transport.

        Either:
            robot = Robot.connect_zmq(endpoint="tcp://192.168.3.10:50557")

        Or:
            robot = Robot.connect_zmq(node_id="QTRD000320")
        """
        transport = ZmqTransport(
            endpoint=endpoint,
            node_id=node_id,
            discovery_timeout=connect_timeout,
        )
        return cls(transport=transport, default_rpc_timeout=default_rpc_timeout)

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(
        self,
        transport: Transport,
        *,
        default_rpc_timeout: float | None = None,
    ) -> None:
        """
        Low-level constructor; most users should use 'connect_*' helpers.

        Args:
            transport: A concrete Transport instance.
            default_rpc_timeout: Default RPC timeout for actions (seconds).
        """
        self._transport = transport
        self._default_rpc_timeout = float(default_rpc_timeout) if default_rpc_timeout is not None else None

        # Robot capability info (may stay None if handshake fails)
        self._robot_type: str | None = None
        self._robot_version: str | None = None
        self._min_sdk: str | None = None
        self._max_sdk: str | None = None

        # Routing maps built from SYSTEM_DESCRIPTION
        # service_name -> { "service_name", "transports", "deprecated", "experimental" }
        self._rpc_routes: Dict[str, Dict[str, Any]] = {}
        # topic -> { "topic", "direction", "frame_type", "transports", "deprecated", "experimental" }
        self._stream_routes: Dict[str, Dict[str, Any]] = {}        

        # requeters are usually shared among multiple apis and need protection
        self._rpc_locks: Dict[str, threading.Lock] = {}

        # ---- Handshake with robot ----
        self._handshake_with_robot()

        # ---- Optional preallocation of RPC requesters ----
        if isinstance(self._transport, SupportsPreallocation):
            if self._rpc_routes:
                self._transport.preallocate_requesters(self._rpc_routes)

    def close(self) -> None:
        """Close the underlying transport and free resources."""
        self._transport.close()
        self._rpc_locks.clear()


    # ------------------------------------------------------------------
    # Stream helpers (used by generated stream APIs)
    # ------------------------------------------------------------------
    def get_stream_reader(
        self,
        topic: str,
        *,
        queue_size: int | None = None,
    ) -> StreamReader:
        """
        Create a StreamReader for a given topic via the current Transport.

        This is the entry point that stream-related APIs (e.g.
        robot.motors.stream.open_joints_reader()) should call.

        Raises:
            UnsupportedAPIError if the topic is not known to this robot,
            or if the stream direction does not allow reading.
        """
        route = self._stream_routes.get(topic)
        if route is None:
            raise UnsupportedAPIError(f"Stream topic {topic!r} is not supported by this robot.")

        direction = route.get("direction")
        if direction not in ("out", None):
            # "out" means robot -> SDK; anything else is not readable here
            raise UnsupportedAPIError(f"Stream topic {topic!r} is not readable (direction={direction!r}).")

        transports_meta = route.get("transports") or {}
        if not transports_meta:
            raise UnsupportedAPIError(f"Stream topic {topic!r} has no transports configured.")

        reader =  self._transport.get_stream_reader(
            topic=topic,
            transports=transports_meta,
            queue_size=queue_size,
        )        
        return reader


    def get_stream_writer(
        self,
        topic: str,
        *,
        queue_size: int | None = None,
    ) -> StreamWriter:
        """
        Create a StreamWriter for a given topic via the current Transport.

        This is the entry point that stream-related APIs (e.g.
        robot.motors.stream.open_head_position_writer()) should call.

        Raises:
            UnsupportedAPIError if the topic is not known to this robot,
            or if the stream direction does not allow writing.
        """
        route = self._stream_routes.get(topic)
        if route is None:
            raise UnsupportedAPIError(f"Stream topic {topic!r} is not supported by this robot.")

        direction = route.get("direction")
        if direction not in ("in", None):
            # "in" means SDK -> robot; anything else is not writable here
            raise UnsupportedAPIError(f"Stream topic {topic!r} is not writable (direction={direction!r}).")

        transports_meta = route.get("transports") or {}
        if not transports_meta:
            raise UnsupportedAPIError(f"Stream topic {topic!r} has no transports configured.")

        writer = self._transport.get_stream_writer(
            topic=topic,
            transports=transports_meta,
            queue_size=queue_size,
        )        
        return writer


    # ------------------------------------------------------------------
    # Internal RPC helper used by ActionHandle
    # ------------------------------------------------------------------
    def rpc_call(
        self,
        service_name: str,
        args: Dict[str, Any],
        timeout: float | None,
    ) -> Dict[str, Any]:
        """
        Internal helper to perform a single RPC call via the current Transport.

        Uses _rpc_routes to find the 'transports' block for this service.
        If there is no route for the given service_name, this API is considered
        unsupported by the robot.
        """
        route = self._rpc_routes.get(service_name)
        if route is None:
            raise UnsupportedAPIError(f"RPC service {service_name!r} is not supported by this robot.")

        transports_meta = route.get("transports") or {}
        if not transports_meta:
            # The description knows about the service_name but did not provide
            # any transports; treat as unsupported.
            raise UnsupportedAPIError(f"RPC service {service_name!r} has no transports configured.")

        lock = self._rpc_locks.setdefault(service_name, threading.Lock())
        requester = self._transport.get_requester(service_name, transports_meta)
        rpc_req = {"name": service_name, "args": args}
        with lock:
            return requester.call(rpc_req, timeout=timeout)        
            

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
        """
        Central place where all auto-generated RPC APIs ultimately end up.
        """
        effective_timeout = timeout if timeout is not None else self._default_rpc_timeout

        handle = ActionHandle(
            service_name=service_name,
            args=args,
            timeout=effective_timeout,
            cancel_service_name=cancel_service_name,
            rpc_call=self.rpc_call,
        )
        if blocking:
            handle.wait()
        return handle


    # ------------------------------------------------------------------
    # Handshake: SYSTEM_DESCRIBE_SERVICE + route building
    # ------------------------------------------------------------------
    def _handshake_with_robot(self) -> None:
        """
        Fetch SYSTEM_DESCRIPTION from the robot and build:
          - rpc routes (services)
          - stream routes (topics)
          - compatibility warnings
        """
        try:
            requester = self._transport.get_requester(SYSTEM_DESCRIBE_SERVICE, None)
            rpc_req = {"name": SYSTEM_DESCRIBE_SERVICE, "args": {"sdk_version": SDK_VERSION}}            
            raw = requester.call(rpc_req, timeout=5.0)        

        except Exception as e:
            Logger.debug(f"Robot: system describe RPC failed: {e}")
            return

        if not isinstance(raw, dict) or not raw.get("status"):
            Logger.warning("Robot: system describe returned invalid payload or status=False.")
            return

        desc: Dict[str, Any] = raw.get("response") or {}
        self._apply_system_description(desc)


    def _apply_system_description(self, desc: Dict[str, Any]) -> None:
        """
        Apply SYSTEM_DESCRIPTION payload from the robot.
        Expected format:
            {
                "robot_type": "qtrobot-v3",
                "robot_version": "1.2.3",
                "min_sdk": "0.5.0",
                "max_sdk": "0.9.0",

                "rpc": {
                    "/qt_robot/speech/say": {
                        "transports": { "zmq": { ... } },
                        "deprecated": False,
                        "experimental": False,
                    },
                    ...
                },

                "stream": {
                    "/qt_robot/joints/state": {
                        "direction": "out",
                        "frame_type": "Frame",
                        "transports": { "zmq": { ... } },
                        "deprecated": False,
                        "experimental": False,
                    },
                    ...
                },
            }
        """
        # --- identity & compatibility ---
        self._robot_type = desc.get("robot_type")
        self._robot_version = desc.get("robot_version")
        self._min_sdk = desc.get("min_sdk")
        self._max_sdk = desc.get("max_sdk")

        sdk_v = self._parse_version(SDK_VERSION)
        if self._min_sdk:
            if sdk_v < self._parse_version(self._min_sdk):
                Logger.warning(
                    f"Robot SDK {SDK_VERSION} is older than robot's "
                    f"minimum supported SDK {self._min_sdk}."
                )
        if self._max_sdk:
            if sdk_v > self._parse_version(self._max_sdk):
                Logger.warning(
                    f"Robot SDK {SDK_VERSION} is newer than robot's "
                    f"maximum tested SDK {self._max_sdk}."
                )

        # --- RPC routes ---
        self._rpc_routes.clear()
        rpc_services = desc.get("rpc", {})
        for service_name, meta in rpc_services.items():
            transports_meta = meta.get("transports") or {}

            self._rpc_routes[service_name] = {
                "service_name": service_name,
                "transports": transports_meta,
                "deprecated": bool(meta.get("deprecated", False)),
                "experimental": bool(meta.get("experimental", False)),
            }

        # --- Stream routes ---
        self._stream_routes.clear()
        streams = desc.get("stream", {})
        for topic, meta in streams.items():
            transports_meta = meta.get("transports") or {}

            self._stream_routes[topic] = {
                "topic": topic,
                "direction": meta.get("direction"),
                "frame_type": meta.get("frame_type"),
                "transports": transports_meta,
                "deprecated": bool(meta.get("deprecated", False)),
                "experimental": bool(meta.get("experimental", False)),
            }

        Logger.debug(
            f"Robot: system description applied. "
            f"{len(self._rpc_routes)} RPC services, "
            f"{len(self._stream_routes)} streams."
        )

    # ------------------------------------------------------------------
    # Version parser (same as before)
    # ------------------------------------------------------------------
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
from .api_factory import attach_core_apis  # noqa: E402

attach_core_apis(Robot, QTROBOT_CORE_APIS)
