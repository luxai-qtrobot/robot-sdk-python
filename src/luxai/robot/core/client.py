# src/luxai/robot/core/client.py
from __future__ import annotations

import threading
from typing import Any, Dict, Tuple, TypeVar

from luxai.magpie.frames import Frame
from luxai.magpie.utils.logger import Logger
from luxai.magpie.transport.stream_reader import StreamReader
from luxai.magpie.transport.stream_writer import StreamWriter

from .actions import ActionHandle, ActionError
from .transport import Transport, SupportsPreallocation, UnsupportedAPIError, ZmqTransport, LocalTransport, MqttTransport, WebRTCTransport
from .config import ( QTROBOT_APIS, SDK_VERSION, SYSTEM_DESCRIBE_SERVICE)
from .typed_stream import TypedStreamReader, TypedStreamWriter
from .plugins import PLUGIN_REGISTRY, RobotPlugin

F = TypeVar("F", bound="Frame")

class Robot:
    """
    High-level SDK client for controlling a robot.

    Transport-agnostic:
      - Robot never looks at "zmq", "mqtt", endpoints, robot_id, etc.
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
        robot_id: str | None = None,
        connect_timeout: float = 5.0,
        default_rpc_timeout: float | None = None,
    ) -> Robot:
        """
        Create and return a :class:`Robot` client using the ZMQ/Magpie transport layer.

        This method establishes a communication channel to a robot either by:
        * Direct connection to a known ZMQ endpoint (e.g. ``tcp://<ip>:<port>``), or
        * Automatic endpoint discovery using the robot's ``robot_id``.

        Exactly one of ``endpoint`` or ``robot_id`` must be provided.  
        On success, a fully initialized :class:`Robot` object is returned and ready
        for issuing RPC commands or performing stream apis.

        Parameters
        ----------
        endpoint:
            Explicit ZMQ endpoint to connect to (e.g. ``"tcp://192.168.3.10:50557"``).
            If provided, discovery is skipped.

        robot_id:
            Robot hardware ID used for endpoint discovery. Mutually exclusive with
            ``endpoint``. If set, a discovery request is performed within
            ``connect_timeout``.

        connect_timeout:
            Maximum number of seconds to wait during endpoint discovery when
            ``robot_id`` is used.

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
            If neither or both of ``endpoint`` and ``robot_id`` are provided.
        TimeoutError
            If endpoint discovery using ``robot_id`` does not resolve before
            ``connect_timeout`` expires.

        Examples
        --------
        Connect directly to a known robot endpoint:

        >>> robot = Robot.connect_zmq(endpoint="tcp://192.168.3.10:50557")

        Connect using a hardware ``robot_id`` and automatic discovery:

        >>> robot = Robot.connect_zmq(robot_id="QTRD000320")

        Override default RPC timeout:

        >>> robot = Robot.connect_zmq(
        ...     endpoint="tcp://192.168.3.10:50557",
        ...     default_rpc_timeout=2.0,
        ... )
        """
        transport = ZmqTransport(
            endpoint=endpoint,
            node_id=robot_id,
            discovery_timeout=connect_timeout,
        )
        return cls(transport=transport, connect_timeout=connect_timeout, default_rpc_timeout=default_rpc_timeout)

    @classmethod
    def connect_mqtt(
        cls,
        uri: str,
        robot_id: str,
        *,
        options=None,
        connect_timeout: float = 10.0,
        default_rpc_timeout: float | None = None,
    ) -> "Robot":
        """
        Create and return a :class:`Robot` client using the MQTT transport layer.

        Connects to the robot via an MQTT broker and the
        ``qtrobot-service-hub-gateway-mqtt``, which bridges the robot's ZMQ RPC
        and stream APIs to MQTT topics.

        Mutually exclusive with :meth:`connect_zmq` — each :class:`Robot` instance
        uses exactly one transport.

        Parameters
        ----------
        uri:
            MQTT broker URI. Supported schemes:
            ``mqtt://``, ``mqtts://``, ``ws://``, ``wss://``.
            Examples: ``"mqtt://192.168.1.100:1883"``,
            ``"wss://broker.example.com:8884/mqtt"``.

        robot_id:
            Robot serial number (e.g. ``"QTRD000320"``). Used to address the
            correct robot on a shared MQTT broker.

        options:
            Optional :class:`luxai.robot.mqtt.MqttOptions` for advanced settings
            (TLS, authentication, session, reconnect, LWT).

        connect_timeout:
            End-to-end timeout (seconds) for the full connection sequence:
            broker TCP handshake + gateway descriptor RPC (including MQTT ACK).
            Increase this for cloud or high-latency brokers.

        default_rpc_timeout:
            Optional override for the default timeout applied to RPC calls.

        Returns
        -------
        Robot
            A connected and ready-to-use Robot client wrapping an
            :class:`MqttTransport`.

        Raises
        ------
        RuntimeError
            If the MQTT broker connection fails or the robot descriptor cannot
            be fetched.
        ImportError
            If ``paho-mqtt`` is not installed (install via
            ``pip install luxai-robot[mqtt]``).

        Examples
        --------
        Connect to a robot over MQTT:

        >>> robot = Robot.connect_mqtt("mqtt://192.168.1.100:1883", "QTRD000320")

        Connect with TLS and authentication:

        >>> from luxai.robot import MqttOptions, MqttTlsOptions, MqttAuthOptions
        >>> options = MqttOptions(
        ...     tls=MqttTlsOptions(ca_file="/path/to/ca.crt"),
        ...     auth=MqttAuthOptions(mode="username_password",
        ...                          username="user", password="pass"),
        ... )
        >>> robot = Robot.connect_mqtt("mqtts://broker:8883", "QTRD000320",
        ...                            options=options)
        """
        try:
            from luxai.magpie.transport.mqtt import MqttConnection
        except ImportError as e:
            raise ImportError(
                "MQTT transport requires paho-mqtt. "
                "Install via: pip install luxai-robot[mqtt]"
            ) from e

        conn = MqttConnection(uri, options=options)
        try:
            connected = conn.connect(timeout=connect_timeout)
        except Exception as e:
            raise RuntimeError(
                f"Robot: failed to connect to MQTT broker at {uri!r}: {e}"
            ) from e
        if not connected:
            raise RuntimeError(
                f"Robot: failed to connect to MQTT broker at {uri!r} "
                f"within {connect_timeout}s."
            )

        transport = MqttTransport(conn, robot_id, connect_timeout=connect_timeout)
        try:
            return cls(transport=transport, connect_timeout=connect_timeout, default_rpc_timeout=default_rpc_timeout)
        except Exception:
            transport.close()
            raise

    @classmethod
    def connect_webrtc_mqtt(
        cls,
        broker_url: str,
        robot_id: str,
        *,
        mqtt_options=None,
        webrtc_options=None,
        reconnect: bool = False,
        connect_timeout: float = 15.0,
        default_rpc_timeout: float | None = None,
    ) -> "Robot":
        """
        Create and return a :class:`Robot` client using a WebRTC transport with
        MQTT as the signaling channel.

        The MQTT broker is used only for the WebRTC handshake (SDP offer/answer
        and ICE candidates).  Once the peer connection is established all traffic
        — RPCs and streams — flows directly over the P2P WebRTC data channel or
        media tracks.

        Parameters
        ----------
        broker_url:
            MQTT broker URI used for WebRTC signaling, e.g.
            ``"mqtt://broker.hivemq.com:1883"`` or ``"mqtts://10.0.0.1:8883"``.

        robot_id:
            Robot serial number (e.g. ``"QTRD000320"``).  Used as the WebRTC
            session identifier so both peers rendezvous on the same channel.

        mqtt_options:
            Optional :class:`luxai.robot.MqttOptions` for the signaling broker
            (TLS, authentication, reconnect, etc.).

        webrtc_options:
            Optional :class:`luxai.robot.WebRTCOptions` for the WebRTC peer
            connection (STUN/TURN servers, codec preferences, etc.).

        reconnect:
            Automatically re-establish the WebRTC connection if it drops.

        connect_timeout:
            End-to-end timeout (seconds) covering broker connection, role
            negotiation, and the full WebRTC handshake.

        default_rpc_timeout:
            Optional override for the default RPC call timeout.

        Returns
        -------
        Robot
            A connected and ready-to-use Robot client wrapping a
            :class:`WebRTCTransport`.

        Raises
        ------
        ImportError
            If ``aiortc`` is not installed
            (``pip install luxai-robot[webrtc]``).
        RuntimeError
            If the WebRTC handshake does not complete within *connect_timeout*.

        Examples
        --------
        >>> robot = Robot.connect_webrtc_mqtt("mqtt://broker:1883", "QTRD000320")

        With TLS signaling and custom STUN/TURN:

        >>> from luxai.robot import MqttOptions, MqttTlsOptions, WebRTCOptions
        >>> robot = Robot.connect_webrtc_mqtt(
        ...     "mqtts://10.231.0.2:8883",
        ...     "QTRD000320",
        ...     mqtt_options=MqttOptions(tls=MqttTlsOptions(ca_file="/path/to/ca.crt")),
        ...     webrtc_options=WebRTCOptions(stun_servers=["stun:stun.l.google.com:19302"]),
        ... )
        """
        try:
            from luxai.magpie.transport.webrtc import WebRTCConnection
        except ImportError as e:
            raise ImportError(
                "WebRTC transport requires aiortc. "
                "Install via: pip install luxai-robot[webrtc]"
            ) from e

        conn = WebRTCConnection.with_mqtt(
            broker_url,
            session_id=robot_id,
            timeout=connect_timeout,
            mqtt_options=mqtt_options,
            reconnect=reconnect,
            options=webrtc_options,
        )
        if not conn.connect(timeout=connect_timeout):
            conn.disconnect()
            raise RuntimeError(
                f"Robot: WebRTC handshake timed out after {connect_timeout}s. "
                "Check that the robot is reachable and uses the same robot_id."
            )

        transport = WebRTCTransport(conn, signaling_params={
            "type": "mqtt",
            "broker_url": broker_url,
            "mqtt_options": mqtt_options,
            "webrtc_options": webrtc_options,
            "reconnect": reconnect,
            "connect_timeout": connect_timeout,
        })
        try:
            return cls(transport=transport, connect_timeout=connect_timeout, default_rpc_timeout=default_rpc_timeout)
        except Exception:
            transport.close()
            raise

    @classmethod
    def connect_webrtc_zmq(
        cls,
        endpoint: str,
        robot_id: str,
        *,
        bind: bool = False,
        webrtc_options=None,
        reconnect: bool = False,
        connect_timeout: float = 15.0,
        default_rpc_timeout: float | None = None,
    ) -> "Robot":
        """
        Create and return a :class:`Robot` client using a WebRTC transport with
        ZMQ PAIR socket as the (broker-less) signaling channel.

        Suitable for LAN / local use where no MQTT broker is available.  One
        peer must bind (``bind=True``) and the other must connect
        (``bind=False``, the default).

        Parameters
        ----------
        endpoint:
            ZMQ endpoint for signaling, e.g. ``"tcp://192.168.1.10:5555"``.
            Use ``"tcp://*:5555"`` when binding.

        robot_id:
            Robot serial number (e.g. ``"QTRD000320"``).  Used as the WebRTC
            session identifier.

        bind:
            ``True`` → bind the ZMQ socket (robot side);
            ``False`` → connect (operator side, default).

        webrtc_options:
            Optional :class:`luxai.robot.WebRTCOptions` for the WebRTC peer
            connection (STUN/TURN servers, codec preferences, etc.).

        reconnect:
            Automatically re-establish the WebRTC connection if it drops.

        connect_timeout:
            End-to-end timeout (seconds) for role negotiation and the full
            WebRTC handshake.

        default_rpc_timeout:
            Optional override for the default RPC call timeout.

        Returns
        -------
        Robot
            A connected and ready-to-use Robot client wrapping a
            :class:`WebRTCTransport`.

        Raises
        ------
        ImportError
            If ``aiortc`` is not installed
            (``pip install luxai-robot[webrtc]``).
        RuntimeError
            If the WebRTC handshake does not complete within *connect_timeout*.

        Examples
        --------
        Connect from the operator side (robot binds on port 5555):

        >>> robot = Robot.connect_webrtc_zmq("tcp://192.168.1.10:5555", "QTRD000320")
        """
        try:
            from luxai.magpie.transport.webrtc import WebRTCConnection
        except ImportError as e:
            raise ImportError(
                "WebRTC transport requires aiortc. "
                "Install via: pip install luxai-robot[webrtc]"
            ) from e

        conn = WebRTCConnection.with_zmq(
            endpoint,
            session_id=robot_id,
            bind=bind,
            reconnect=reconnect,
            options=webrtc_options,
        )
        if not conn.connect(timeout=connect_timeout):
            conn.disconnect()
            raise RuntimeError(
                f"Robot: WebRTC handshake timed out after {connect_timeout}s. "
                "Check that the robot is reachable and uses the same robot_id."
            )

        transport = WebRTCTransport(conn, signaling_params={
            "type": "zmq",
            "endpoint": endpoint,
            "bind": bind,
            "webrtc_options": webrtc_options,
            "reconnect": reconnect,
            "connect_timeout": connect_timeout,
        })
        try:
            return cls(transport=transport, connect_timeout=connect_timeout, default_rpc_timeout=default_rpc_timeout)
        except Exception:
            transport.close()
            raise

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(
        self,
        transport: Transport,
        *,
        connect_timeout: float = 5.0,
        default_rpc_timeout: float | None = None,
    ) -> None:
        """
        Low-level constructor; most users should use 'connect_*' helpers.

        Args:
            transport: A concrete Transport instance.
            connect_timeout: Timeout for the initial handshake RPC (seconds).
            default_rpc_timeout: Default RPC timeout for actions (seconds).
        """
        self._robot_transport = transport
        self._default_rpc_timeout = float(default_rpc_timeout) if default_rpc_timeout is not None else None

        # Robot capability info (may stay None if handshake fails)
        self._robot_type: str | None = None
        self._robot_id: str | None = None
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
        self._handshake_with_robot(timeout=connect_timeout)

        # ---- Optional preallocation of RPC requesters ----
        if isinstance(self._robot_transport, SupportsPreallocation):
            if self._rpc_routes:
                rpc_routes: Dict[str, Dict[str, Any]] = {
                    route: data
                    for route, (_transport, data) in self._rpc_routes.items()
                }    
                self._robot_transport.preallocate_requesters(rpc_routes)
     
        
    
    # ------------------------------------------------------------------
    # Read-only properties
    # ------------------------------------------------------------------

    @property
    def robot_id(self) -> str | None:
        """Unique robot identifier as reported by the robot (e.g. ``"QTRD000320"``), or ``None`` if not yet known."""
        return self._robot_id

    @property
    def robot_type(self) -> str | None:
        """Robot model/type string returned by the robot descriptor, or ``None`` if not yet known."""
        return self._robot_type

    @property
    def sdk_version(self) -> str | None:
        """Robot-side SDK version string, or ``None`` if not yet known."""
        return self._sdk_version

    @property
    def min_sdk(self) -> str | None:
        """Minimum client SDK version required by the robot, or ``None`` if not reported."""
        return self._min_sdk

    @property
    def max_sdk(self) -> str | None:
        """Maximum client SDK version supported by the robot, or ``None`` if not reported."""
        return self._max_sdk

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
    def enable_plugin_mqtt(self, name: str, node_id: str) -> None:
        """
        Enable a remote plugin over MQTT, reusing the robot's broker connection.

        The ``node_id`` must match the plugin's ZMQ node identifier (e.g.
        ``"qtrobot-realsense-driver"``), which the MQTT gateway uses as the
        plugin's topic namespace.

        Requires the robot to be connected via :meth:`connect_mqtt`.

        Examples:
            robot.enable_plugin_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")
        """
        from .transport.mqtt_transport import MqttTransport as _MqttTransport

        if not isinstance(self._robot_transport, _MqttTransport):
            raise RuntimeError(
                "enable_plugin_mqtt() requires the robot to be connected via connect_mqtt()."
            )

        transport = _MqttTransport(
            connection=self._robot_transport.connection,
            robot_id=node_id,
            connect_timeout=self._robot_transport._connect_timeout,
            owns_connection=False,
        )
        self.enable_plugin(name, transport)

    def enable_plugin_zmq(self, name: str,
                          robot_id: str | None = None,
                          endpoint: str | None = None) -> None:
        """
        Enable a remote plugin by name (string) over ZMQ transport.

        Examples:
            robot.enable_plugin("realsense-driver") # lets discovery find the it
            robot.enable_plugin("realsense-driver", endpoint="tcp://192.168.3.152:50655")
        """
        transport = ZmqTransport(
            endpoint=endpoint,
            node_id=robot_id,
            discovery_timeout=5.0,
        )
        self.enable_plugin(name, transport)


    def enable_plugin_webrtc_mqtt(
        self,
        name: str,
        node_id: str,
        *,
        broker_url: str | None = None,
        mqtt_options=None,
        webrtc_options=None,
        reconnect: bool | None = None,
        connect_timeout: float | None = None,
    ) -> None:
        """
        Enable a remote plugin over a dedicated WebRTC connection, using MQTT
        as the signaling channel.

        Each plugin gets its own independent WebRTC peer connection — with its
        own data channel and media tracks — so plugin video/audio streams do not
        conflict with the robot peer's tracks.

        When called on a robot connected via :meth:`connect_webrtc_mqtt`, all
        signaling parameters (``broker_url``, ``mqtt_options``, ``webrtc_options``,
        ``reconnect``, ``connect_timeout``) default to the values used for the
        robot connection. Override any of them to target a different broker or
        use different options for the plugin peer.

        Args:
            name:           Plugin name as registered in the plugin registry
                            (e.g. ``"realsense-driver"``).
            node_id:        Plugin's ZMQ node identifier, used as the WebRTC
                            session ID for signaling (e.g. ``"qtrobot-realsense-driver"``).
            broker_url:     MQTT broker URI for WebRTC signaling. Defaults to the
                            robot's broker if connected via connect_webrtc_mqtt().
            mqtt_options:   Signaling broker options (TLS, auth, etc.). Defaults to
                            the robot's mqtt_options.
            webrtc_options: WebRTC peer options (STUN/TURN, codecs). Defaults to
                            the robot's webrtc_options.
            reconnect:      Automatically re-establish if the connection drops.
                            Defaults to the robot's reconnect setting.
            connect_timeout: End-to-end timeout (seconds). Defaults to the robot's
                             connect_timeout.

        Examples:
            # Reuse robot's broker and settings automatically
            robot.enable_plugin_webrtc_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")

            # Or target a different broker for the plugin
            robot.enable_plugin_webrtc_mqtt(
                "realsense-driver",
                node_id="qtrobot-realsense-driver",
                broker_url="mqtt://other-broker:1883",
            )
        """
        try:
            from luxai.magpie.transport.webrtc import WebRTCConnection
        except ImportError as e:
            raise ImportError(
                "WebRTC transport requires aiortc. "
                "Install via: pip install luxai-robot[webrtc]"
            ) from e

        if not isinstance(self._robot_transport, WebRTCTransport):
            raise RuntimeError(
                "enable_plugin_webrtc_mqtt() requires the robot to be connected via "
                "connect_webrtc_mqtt() or connect_webrtc_zmq(). "
                "Alternatively, use enable_plugin(name, WebRTCTransport(...)) directly."
            )

        params = self._robot_transport._signaling_params
        _broker_url   = broker_url      if broker_url      is not None else params.get("broker_url")
        _mqtt_options = mqtt_options    if mqtt_options     is not None else params.get("mqtt_options")
        _webrtc_opts  = webrtc_options  if webrtc_options   is not None else params.get("webrtc_options")
        _reconnect    = reconnect       if reconnect        is not None else params.get("reconnect", False)
        _timeout      = connect_timeout if connect_timeout  is not None else params.get("connect_timeout", 15.0)

        if not _broker_url:
            raise RuntimeError(
                "broker_url is required when the robot is not connected via connect_webrtc_mqtt()."
            )

        conn = WebRTCConnection.with_mqtt(
            _broker_url,
            session_id=node_id,
            timeout=_timeout,
            mqtt_options=_mqtt_options,
            reconnect=_reconnect,
            options=_webrtc_opts,
        )
        if not conn.connect(timeout=_timeout):
            conn.disconnect()
            raise RuntimeError(
                f"Robot: WebRTC handshake for plugin {node_id!r} timed out after {_timeout}s."
            )
        transport = WebRTCTransport(conn)
        try:
            self.enable_plugin(name, transport)
        except Exception:
            transport.close()
            raise

    def enable_plugin_webrtc_zmq(
        self,
        name: str,
        node_id: str,
        *,
        endpoint: str | None = None,
        bind: bool | None = None,
        webrtc_options=None,
        reconnect: bool | None = None,
        connect_timeout: float | None = None,
    ) -> None:
        """
        Enable a remote plugin over a dedicated WebRTC connection, using ZMQ
        as the (broker-less) signaling channel.

        When called on a robot connected via :meth:`connect_webrtc_zmq`, all
        signaling parameters default to the values used for the robot connection.
        Override any of them to target a different endpoint or use different options.

        Args:
            name:           Plugin name as registered in the plugin registry
                            (e.g. ``"realsense-driver"``).
            node_id:        Plugin's ZMQ node identifier, used as the WebRTC
                            session ID for signaling (e.g. ``"qtrobot-realsense-driver"``).
            endpoint:       ZMQ signaling endpoint. Defaults to the robot's endpoint
                            if connected via connect_webrtc_zmq().
            bind:           ``True`` → bind; ``False`` → connect. Defaults to the
                            robot's bind setting.
            webrtc_options: WebRTC peer options. Defaults to the robot's webrtc_options.
            reconnect:      Auto-reconnect on drop. Defaults to the robot's setting.
            connect_timeout: End-to-end timeout. Defaults to the robot's connect_timeout.

        Examples:
            # Reuse robot's ZMQ signaling settings
            robot.enable_plugin_webrtc_zmq("realsense-driver", node_id="qtrobot-realsense-driver")

            # Or use a different endpoint for the plugin
            robot.enable_plugin_webrtc_zmq(
                "realsense-driver",
                node_id="qtrobot-realsense-driver",
                endpoint="tcp://192.168.1.10:5556",
            )
        """
        try:
            from luxai.magpie.transport.webrtc import WebRTCConnection
        except ImportError as e:
            raise ImportError(
                "WebRTC transport requires aiortc. "
                "Install via: pip install luxai-robot[webrtc]"
            ) from e

        if not isinstance(self._robot_transport, WebRTCTransport):
            raise RuntimeError(
                "enable_plugin_webrtc_zmq() requires the robot to be connected via "
                "connect_webrtc_zmq() or connect_webrtc_mqtt(). "
                "Alternatively, use enable_plugin(name, WebRTCTransport(...)) directly."
            )

        params = self._robot_transport._signaling_params
        _endpoint    = endpoint        if endpoint        is not None else params.get("endpoint")
        _bind        = bind            if bind            is not None else params.get("bind", False)
        _webrtc_opts = webrtc_options  if webrtc_options  is not None else params.get("webrtc_options")
        _reconnect   = reconnect       if reconnect       is not None else params.get("reconnect", False)
        _timeout     = connect_timeout if connect_timeout is not None else params.get("connect_timeout", 15.0)

        if not _endpoint:
            raise RuntimeError(
                "endpoint is required when the robot is not connected via connect_webrtc_zmq()."
            )

        conn = WebRTCConnection.with_zmq(
            _endpoint,
            session_id=node_id,
            bind=_bind,
            reconnect=_reconnect,
            options=_webrtc_opts,
        )
        if not conn.connect(timeout=_timeout):
            conn.disconnect()
            raise RuntimeError(
                f"Robot: WebRTC handshake for plugin {node_id!r} timed out after {_timeout}s."
            )
        transport = WebRTCTransport(conn)
        try:
            self.enable_plugin(name, transport)
        except Exception:
            transport.close()
            raise

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
    def _handshake_with_robot(self, timeout: float = 5.0) -> None:
        """
        Fetch SYSTEM_DESCRIPTION from the robot and build:
          - rpc routes (services)
          - stream routes (topics)
          - compatibility warnings
        """
        try:
            requester = self._robot_transport.get_requester(SYSTEM_DESCRIBE_SERVICE, None)
            rpc_req = {"name": SYSTEM_DESCRIBE_SERVICE, "args": {"sdk_version": SDK_VERSION}}
            raw = requester.call(rpc_req, timeout=timeout)

        except Exception as e:            
            raise RuntimeError(f"Robot: system describe RPC failed: {e}")            

        if not isinstance(raw, dict) or not raw.get("status"):
            raise RuntimeError("Robot: system describe returned invalid payload or status=False.")            

        desc: Dict[str, Any] = raw.get("response") or {}
        self._apply_system_description(desc)


    def _apply_system_description(self, desc: Dict[str, Any]) -> None:
        """
        Apply SYSTEM_DESCRIPTION payload from the robot.
        Expected format:
            {
                "robot_type": "qtrobot-v3",
                "robot_id": "QTRD000123",
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
        self._robot_id = desc.get("robot_id")
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
