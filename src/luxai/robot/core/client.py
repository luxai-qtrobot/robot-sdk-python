# src/luxai/robot/core/client.py
from __future__ import annotations

import threading
from typing import Any, Dict, Tuple, TypeVar

from luxai.magpie.frames import Frame
from luxai.magpie.utils.logger import Logger
from luxai.magpie.transport.stream_reader import StreamReader
from luxai.magpie.transport.stream_writer import StreamWriter

from .actions import ActionHandle, ActionError
from .transport import Transport, SupportsPreallocation, UnsupportedAPIError, ZmqTransport, LocalTransport
from .config import ( QTROBOT_APIS, SDK_VERSION, SYSTEM_DESCRIBE_SERVICE)
from .typed_stream import TypedStreamReader, TypedStreamWriter
from .plugins import PLUGIN_REGISTRY, RobotPlugin

F = TypeVar("F", bound="Frame")

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
        Create and return a :class:`Robot` client using the ZMQ/Magpie transport layer.

        This method establishes a communication channel to a robot either by:
        * Direct connection to a known ZMQ endpoint (e.g. ``tcp://<ip>:<port>``), or
        * Automatic endpoint discovery using the robot's ``node_id``.

        Exactly one of ``endpoint`` or ``node_id`` must be provided.  
        On success, a fully initialized :class:`Robot` object is returned and ready
        for issuing RPC commands or performing stream apis.

        Parameters
        ----------
        endpoint:
            Explicit ZMQ endpoint to connect to (e.g. ``"tcp://192.168.3.10:50557"``).
            If provided, discovery is skipped.

        node_id:
            Robot hardware ID used for endpoint discovery. Mutually exclusive with
            ``endpoint``. If set, a discovery request is performed within
            ``connect_timeout``.

        connect_timeout:
            Maximum number of seconds to wait during endpoint discovery when
            ``node_id`` is used.

        default_rpc_timeout:
            Optional override for the default timeout applied to RPC calls
            issued by the resulting :class:`Robot` instance.

        Returns
        -------
        Robot
            A connected and ready-to-use Robot client wrapping a :class:`ZmqTransport`.

        Raises
        ------
        ValueError
            If neither or both of ``endpoint`` and ``node_id`` are provided.
        TimeoutError
            If endpoint discovery using ``node_id`` does not resolve before
            ``connect_timeout`` expires.

        Examples
        --------
        Connect directly to a known robot endpoint:

        >>> robot = Robot.connect_zmq(endpoint="tcp://192.168.3.10:50557")

        Connect using a hardware ``node_id`` and automatic discovery:

        >>> robot = Robot.connect_zmq(node_id="QTRD000320")

        Override default RPC timeout:

        >>> robot = Robot.connect_zmq(
        ...     endpoint="tcp://192.168.3.10:50557",
        ...     default_rpc_timeout=2.0,
        ... )
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
        self._robot_transport = transport
        self._default_rpc_timeout = float(default_rpc_timeout) if default_rpc_timeout is not None else None

        # Robot capability info (may stay None if handshake fails)
        self._robot_type: str | None = None
        self._robot_serial: str | None = None
        self._sdk_version: str | None = None
        self._min_sdk: str | None = None
        self._max_sdk: str | None = None

        # Routing maps built from SYSTEM_DESCRIPTION
        # service_name -> { (transport instance, "service_name", "transports", "deprecated", "experimental") }
        self._rpc_routes: Dict[str, Tuple[Transport, Dict[str, Any]]] = {}
        # topic -> { (transport instance, "topic", "direction", "frame_type", "transports", "deprecated", "experimental") }
        self._stream_routes: Dict[str, Tuple[Transport, Dict[str, Any]]] = {}

        # requeters are usually shared among multiple apis and need protection
        self._rpc_locks: Dict[str, threading.Lock] = {}

        # active plugin instances
        self._plugins: Dict[str, RobotPlugin] = {} 

        # ---- Handshake with robot to get the correct routes for apis----
        self._handshake_with_robot()

        # ---- Optional preallocation of RPC requesters ----
        if isinstance(self._robot_transport, SupportsPreallocation):
            if self._rpc_routes:
                rpc_routes: Dict[str, Dict[str, Any]] = {
                    route: data
                    for route, (_transport, data) in self._rpc_routes.items()
                }    
                self._robot_transport.preallocate_requesters(rpc_routes)
     
        
    
    def close(self) -> None:
        """Close the underlying transport and free resources."""
        # Stop plugins
        for plugin in list(self._plugins.values()):
            try:
                plugin.stop()
            except Exception:
                pass
        self._plugins.clear()

        self._robot_transport.close()
        self._rpc_locks.clear()


    # ------------------------------------------------------------------
    # Stream helpers (used by generated stream APIs)
    # ------------------------------------------------------------------
    def get_stream_reader(
        self,
        topic: str,
        *,
        queue_size: int | None = None,
        frame_type: type[F]
    ) -> TypedStreamReader[F]:
        """
        Create a StreamReader for a given topic via the current Transport.

        This is the entry point that stream-related APIs (e.g.
        robot.motors.stream.open_joints_reader()) should call.

        Raises:
            UnsupportedAPIError if the topic is not known to this robot,
            or if the stream direction does not allow reading.
        """
        item = self._stream_routes.get(topic)
        if item is None:
            raise UnsupportedAPIError(f"Stream topic {topic!r} is not supported by this robot.")

        transporter, route = item
        direction = route.get("direction")
        if direction not in ("out", None):
            # "out" means robot -> SDK; anything else is not readable here
            raise UnsupportedAPIError(f"Stream topic {topic!r} is not readable (direction={direction!r}).")

        transports_meta = route.get("transports") or {}
        if not transports_meta:
            raise UnsupportedAPIError(f"Stream topic {topic!r} has no transports configured.")

        stream_reader = transporter.get_stream_reader(
            topic=topic,
            transports=transports_meta,
            queue_size=queue_size,
        ) 

        typed_reader: TypedStreamReader[F] = TypedStreamReader(
            stream_reader=stream_reader,
            frame_type=frame_type
        )
        return typed_reader


    def get_stream_writer(
        self,
        topic: str,
        *,
        queue_size: int | None = None,
    ) -> TypedStreamWriter[Frame]:
        """
        Create a StreamWriter for a given topic via the current Transport.

        This is the entry point that stream-related APIs (e.g.
        robot.motors.stream.open_head_position_writer()) should call.

        Raises:
            UnsupportedAPIError if the topic is not known to this robot,
            or if the stream direction does not allow writing.
        """
        item = self._stream_routes.get(topic)
        if item is None:
            raise UnsupportedAPIError(f"Stream topic {topic!r} is not supported by this robot.")

        transporter, route = item
        direction = route.get("direction")
        if direction not in ("in", None):
            # "in" means SDK -> robot; anything else is not writable here
            raise UnsupportedAPIError(f"Stream topic {topic!r} is not writable (direction={direction!r}).")

        transports_meta = route.get("transports") or {}
        if not transports_meta:
            raise UnsupportedAPIError(f"Stream topic {topic!r} has no transports configured.")

        stream_writer = transporter.get_stream_writer(
            topic=topic,
            transports=transports_meta,
            queue_size=queue_size,
        )      
        typed_writer: TypedStreamWriter[Frame] = TypedStreamWriter(
            stream_writer=stream_writer,
            topic=topic            
        )

        return typed_writer


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
        item = self._rpc_routes.get(service_name)
        if item is None:
            raise UnsupportedAPIError(f"RPC service {service_name!r} is not supported by this robot.")

        transporter, route = item
        transports_meta = route.get("transports") or {}
        if not transports_meta:
            # The description knows about the service_name but did not provide
            # any transports; treat as unsupported.
            raise UnsupportedAPIError(f"RPC service {service_name!r} has no transports configured.")

        lock = self._rpc_locks.setdefault(service_name, threading.Lock())
        requester = transporter.get_requester(service_name, transports_meta)
        rpc_req = {"name": service_name, "args": args}
        with lock:
            return requester.call(rpc_req, timeout=timeout)        
            

    # ---------------------------------------------------------
    def enable_plugin(self, name: str, transport: Transport) -> None:
        """
        Enable a plugin by name (string) using a  transport.

        Examples:
            robot.enable_plugin("azure-asr", transport=LocalTransport())       

        """

        if name not in PLUGIN_REGISTRY:
            raise ValueError(f"Unknown plugin {name}. Did you spell it correctly?")

        # Case 1: user passed string
        plugin_cls = PLUGIN_REGISTRY.get(name)
        if plugin_cls is None:
            raise RuntimeError(
                f"Plugin {name} is not installed.\n"
                f"Install via: pip install luxai-robot[{name}]"
            )

        if name in self._plugins:
            # ignore double enable
            return
        
        # Instantiate + start the plugin
        plugin = plugin_cls()
        plugin.start(self, transport)

        # Track it for cleanup
        self._plugins[name] = plugin


    # ---------------------------------------------------------
    def enable_plugin_zmq(self, name: str, 
                          node_id: str | None = None,
                          endpoint: str | None = None) -> None:
        """
        Enable a remote plugin by name (string) over ZMQ transport.

        Examples:
            robot.enable_plugin("realsense-driver") # lets discovery find the it
            robot.enable_plugin("realsense-driver", endpoint="tcp://192.168.3.152:50655")
        """
        transport = ZmqTransport(
            endpoint=endpoint,
            node_id=node_id,
            discovery_timeout=5.0,
        )
        self.enable_plugin(name, transport)


    def enable_plugin_local(self, name: str) -> None:
        """
        Enable a local plugin by name (string) over Local transport.

        Examples:
            robot.enable_plugin("asr-azure")
        """
        transport = LocalTransport()
        self.enable_plugin(name, transport)


    # ---------------------------------------------------------
    def disable_plugin(self, name: str) -> None:
        """
        Disable (stop + remove) a previously enabled plugin.
        """
        plugin = self._plugins.pop(name, None)
        if plugin is None:
            return

        try:
            plugin.stop()
        except Exception:
            pass
    


    def __enter__(self):
        # Optionally assert it’s not already closed
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    
    # ------------------------------------------------------------------
    # Internal helpers used by auto-generated RPC APIs
    # ------------------------------------------------------------------
    def _call_rpc_sync(
        self,
        service_name: str,
        args: Dict[str, Any],
        timeout: float | None = None,
    ) -> Any:
        """
        Execute an RPC call on the calling thread and return the unwrapped value.

        Used by the synchronous (blocking) API variant generated for every RPC.
        Raises ActionError if the robot reports failure.
        """
        effective_timeout = timeout if timeout is not None else self._default_rpc_timeout
        raw = self.rpc_call(service_name, args, timeout=effective_timeout)
        if not raw.get("status", False):
            raise ActionError(
                f"Robot reported failure for {service_name!r}: {raw.get('response')!r}"
            )
        return raw.get("response")

    def _start_action(
        self,
        service_name: str,
        args: Dict[str, Any],
        *,
        cancel_service_name: str | None = None,
        timeout: float | None = None,
    ) -> ActionHandle:
        """
        Start an RPC call on a background thread and return an ActionHandle.

        Used by the async (_async) API variant for long-running / cancellable RPCs.
        """
        effective_timeout = timeout if timeout is not None else self._default_rpc_timeout
        return ActionHandle(
            service_name=service_name,
            args=args,
            timeout=effective_timeout,
            cancel_service_name=cancel_service_name,
            rpc_call=self.rpc_call,
        )


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
            requester = self._robot_transport.get_requester(SYSTEM_DESCRIBE_SERVICE, None)
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
                "robot_serial": "QTRD000123",
                "sdk_version": "1.2.3",
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
        self._robot_serial = desc.get("robot_serial")
        self._sdk_version = desc.get("sdk_version")
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
        self._setup_rpc_routes(self._robot_transport, desc.get("rpc", {}))

        # --- Stream routes ---
        self._stream_routes.clear()
        self._setup_stream_routes(self._robot_transport, desc.get("stream", {}))

        Logger.debug(
            f"Robot: system description applied. "
            f"{len(self._rpc_routes)} RPC services, "
            f"{len(self._stream_routes)} streams."
        )


    def _setup_rpc_routes(self, transporter: Transport, rpc_services: Dict[str, Dict[str, Any]]) -> None:
        for service_name, meta in rpc_services.items():
            transports_meta = meta.get("transports") or {}
            self._rpc_routes[service_name] = (      
                transporter, 
                {
                    "service_name": service_name,
                    "transports": transports_meta,
                    "deprecated": bool(meta.get("deprecated", False)),
                    "experimental": bool(meta.get("experimental", False)),
                },
            )   


    def _setup_stream_routes(self, transporter: Transport, streams: Dict[str, Dict[str, Any]]) -> None:
        for topic, meta in streams.items():
            transports_meta = meta.get("transports") or {}
            self._stream_routes[topic] = (
                transporter, 
                {
                    "topic": topic,
                    "direction": meta.get("direction"),
                    "frame_type": meta.get("frame_type"),
                    "transports": transports_meta,
                    "deprecated": bool(meta.get("deprecated", False)),
                    "experimental": bool(meta.get("experimental", False)),
                },
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

attach_core_apis(Robot, QTROBOT_APIS)
