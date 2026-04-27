from __future__ import annotations

from typing import Any, Dict, TypeVar, Callable, List
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
        ...

    @classmethod
    def connect_mqtt(
        cls,
        uri: str,
        robot_id: str,
        *,
        options: Any | None = None,
        connect_timeout: float = 10.0,
        default_rpc_timeout: float | None = None,
    ) -> Robot:
        """
        Create and return a :class:`Robot` client using the MQTT transport layer.

        Connects to the robot via an MQTT broker and the
        ``qtrobot-service-hub-gateway-mqtt`` bridge, which exposes the robot's
        ZMQ RPC and stream APIs over MQTT topics.

        Mutually exclusive with :meth:`connect_zmq` — each :class:`Robot` instance
        uses exactly one transport.

        Parameters
        ----------
        uri:
            MQTT broker URI. Supported schemes:
            ``mqtt://``, ``mqtts://``, ``ws://``, ``wss://``.
            Examples: ``"mqtt://10.231.0.2:1883"``,
            ``"wss://broker.example.com:8884/mqtt"``.

        robot_id:
            Robot serial number (e.g. ``"QTRD000320"``). Used to address the
            correct robot on a shared MQTT broker.

        options:
            Optional :class:`luxai.robot.MqttOptions` for advanced settings
            (TLS, authentication, session, reconnect, LWT).
            Requires ``pip install luxai-robot[mqtt]``.

        connect_timeout:
            Maximum seconds to wait for the MQTT broker connection.

        default_rpc_timeout:
            Optional override for the default timeout applied to RPC calls
            issued by the resulting :class:`Robot` instance.

        Returns
        -------
        Robot
            A connected and ready-to-use Robot client wrapping an
            :class:`~luxai.robot.core.transport.MqttTransport`.

        Raises
        ------
        RuntimeError
            If the MQTT broker connection fails or the robot descriptor cannot
            be fetched.
        ImportError
            If ``paho-mqtt`` is not installed
            (install via ``pip install luxai-robot[mqtt]``).

        Examples
        --------
        Connect to a robot over plain MQTT:

        >>> robot = Robot.connect_mqtt("mqtt://10.231.0.2:1883", "QTRD000320")

        Connect with mutual TLS (mTLS):

        >>> from luxai.robot import MqttOptions, MqttTlsOptions, MqttAuthOptions
        >>> options = MqttOptions(
        ...     tls=MqttTlsOptions(
        ...         ca_file="/path/to/ca.crt",
        ...         cert_file="/path/to/client.crt",
        ...         key_file="/path/to/client.key",
        ...     ),
        ...     auth=MqttAuthOptions(mode="mtls"),
        ... )
        >>> robot = Robot.connect_mqtt("mqtts://10.231.0.2:8883", "QTRD000320",
        ...                            options=options)
        """
        ...

    @classmethod
    def connect_webrtc_mqtt(
        cls,
        broker_url: str,
        robot_id: str,
        *,
        mqtt_options: Any | None = None,
        webrtc_options: Any | None = None,
        reconnect: bool = False,
        connect_timeout: float = 15.0,
        default_rpc_timeout: float | None = None,
    ) -> Robot:
        """
        Create and return a :class:`Robot` client using a WebRTC transport with
        MQTT as the signaling channel.

        The MQTT broker is used **only** for the WebRTC handshake (SDP offer/answer
        and ICE candidates). Once the peer connection is established, all traffic
        — RPCs and streams — flows directly over the P2P WebRTC data channel or
        native media tracks.

        Mutually exclusive with :meth:`connect_zmq` and :meth:`connect_mqtt` —
        each :class:`Robot` instance uses exactly one transport.

        Parameters
        ----------
        broker_url:
            MQTT broker URI used for WebRTC signaling, e.g.
            ``"mqtt://10.231.0.2:1883"`` or ``"mqtts://broker.example.com:8883"``.

        robot_id:
            Robot identifier (e.g. ``"QTRD000320"``). Used as the WebRTC session
            ID so both peers rendezvous on the same signaling channel.

        mqtt_options:
            Optional :class:`luxai.robot.MqttOptions` for the signaling broker
            (TLS, authentication, reconnect policy, etc.).

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
        Basic connection over a local broker:

        >>> robot = Robot.connect_webrtc_mqtt("mqtt://10.231.0.2:1883", "QTRD000320")

        With mTLS signaling and STUN/TURN for NAT traversal:

        >>> from luxai.robot import MqttOptions, MqttTlsOptions, WebRTCOptions, WebRTCTurnServer
        >>> robot = Robot.connect_webrtc_mqtt(
        ...     "mqtts://10.231.0.2:8883",
        ...     "QTRD000320",
        ...     mqtt_options=MqttOptions(
        ...         tls=MqttTlsOptions(ca_file="/path/to/ca.crt"),
        ...     ),
        ...     webrtc_options=WebRTCOptions(
        ...         stun_servers=["stun:stun.l.google.com:19302"],
        ...         turn_servers=[WebRTCTurnServer(url="turn:turn.example.com:3478",
        ...                                        username="user", credential="pass")],
        ...     ),
        ... )
        """
        ...

    @classmethod
    def connect_webrtc_zmq(
        cls,
        endpoint: str,
        robot_id: str,
        *,
        bind: bool = False,
        webrtc_options: Any | None = None,
        reconnect: bool = False,
        connect_timeout: float = 15.0,
        default_rpc_timeout: float | None = None,
    ) -> Robot:
        """
        Create and return a :class:`Robot` client using a WebRTC transport with
        a ZMQ PAIR socket as the (broker-less) signaling channel.

        Suitable for LAN / local use where no MQTT broker is available. One peer
        must bind (``bind=True``) and the other must connect (``bind=False``,
        the default).

        Mutually exclusive with :meth:`connect_zmq` and :meth:`connect_mqtt` —
        each :class:`Robot` instance uses exactly one transport.

        Parameters
        ----------
        endpoint:
            ZMQ endpoint for signaling, e.g. ``"tcp://192.168.1.10:5555"``.
            Use ``"tcp://*:5555"`` when binding.

        robot_id:
            Robot identifier (e.g. ``"QTRD000320"``). Used as the WebRTC
            session ID.

        bind:
            ``True`` → bind the ZMQ socket (typically the robot side);
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
        ...

    def __init__(
        self,
        transport: Transport,
        *,
        connect_timeout: float = 5.0,
        default_rpc_timeout: float | None = None,
    ) -> None:
        ...

    
    @property
    def robot_id(self) -> str | None:
        """Unique robot identifier as reported by the robot (e.g. ``"QTRD000320"``), or ``None`` if not yet known."""
        ...

    @property
    def robot_type(self) -> str | None:
        """Robot model/type string returned by the robot descriptor, or ``None`` if not yet known."""
        ...

    @property
    def sdk_version(self) -> str | None:
        """Robot-side SDK version string, or ``None`` if not yet known."""
        ...

    @property
    def min_sdk(self) -> str | None:
        """Minimum client SDK version required by the robot, or ``None`` if not reported."""
        ...

    @property
    def max_sdk(self) -> str | None:
        """Maximum client SDK version supported by the robot, or ``None`` if not reported."""
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

    def enable_plugin(self, name: str, transport: Transport) -> None:
        """
        Enable a plugin by name (string) using a transport.

        Examples:
            robot.enable_plugin("azure-asr", transport=LocalTransport())            

        """
        ...

    def enable_plugin_local(self, name: str) -> None:
        """
        Enable a local plugin by name (string) over Local transport.

        Examples:
            robot.enable_plugin("asr-azure")
        """
        ...

    def enable_plugin_zmq(
        self,
        name: str,
        node_id: str | None = None,
        endpoint: str | None = None,
    ) -> None:
        """
        Enable a remote plugin by name over ZMQ transport.

        Args:
            name:      Plugin name as registered in the plugin registry (e.g. ``"realsense-driver"``).
            node_id:  ZMQ node identifier of the plugin (e.g. ``"qtrobot-realsense-driver"``).
                       Used for Zeroconf-based discovery. Omit if passing ``endpoint`` directly.
            endpoint:  Direct ZMQ endpoint of the plugin (e.g. ``"tcp://192.168.3.152:50750"``).

        Examples:        
            robot.enable_plugin_zmq("realsense-driver", node_id="qtrobot-realsense-driver")
            robot.enable_plugin_zmq("realsense-driver", endpoint="tcp://192.168.3.152:50750")
        """
        ...

    def enable_plugin_mqtt(self, name: str, node_id: str) -> None:
        """
        Enable a remote plugin over MQTT, reusing the robot's broker connection.

        The ``node_id`` must match the plugin's ZMQ node identifier (e.g.
        ``"qtrobot-realsense-driver"``), which the MQTT gateway uses as the
        plugin's topic namespace.

        Requires the robot to be connected via :meth:`connect_mqtt`.

        Args:
            name:    Plugin name as registered in the plugin registry (e.g. ``"realsense-driver"``).
            node_id: Plugin's ZMQ node identifier, used by the MQTT gateway as the topic namespace
                     (e.g. ``"qtrobot-realsense-driver"``).

        Examples:
            robot.enable_plugin_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")
        """
        ...

    def enable_plugin_webrtc_mqtt(
        self,
        name: str,
        node_id: str,
        *,
        broker_url: str | None = None,
        mqtt_options: Any | None = None,
        webrtc_options: Any | None = None,
        reconnect: bool | None = None,
        connect_timeout: float | None = None,
    ) -> None:
        """
        Enable a remote plugin over a dedicated WebRTC peer connection, using
        MQTT as the signaling channel.

        Each plugin gets its own independent WebRTC peer — with its own data
        channel and media tracks — so plugin video/audio streams do not conflict
        with the robot peer's tracks.

        Args:
            name:           Plugin name as registered in the plugin registry
                            (e.g. ``"realsense-driver"``).
            node_id:        Plugin's ZMQ node identifier, used as the WebRTC
                            session ID for signaling
                            (e.g. ``"qtrobot-realsense-driver"``).
            broker_url:     MQTT broker URI for WebRTC signaling
                            (e.g. ``"mqtt://10.231.0.2:1883"``).
            mqtt_options:   Optional :class:`luxai.robot.MqttOptions` for the
                            signaling broker (TLS, authentication, etc.).
            webrtc_options: Optional :class:`luxai.robot.WebRTCOptions` for
                            the WebRTC peer (STUN/TURN, codec prefs, etc.).
            reconnect:      Automatically re-establish if the connection drops.
            connect_timeout: End-to-end timeout (seconds) for signaling + handshake.

        Examples:
            robot.enable_plugin_webrtc_mqtt(
                "realsense-driver",
                node_id="qtrobot-realsense-driver",
                broker_url="mqtt://10.231.0.2:1883",
            )
        """
        ...

    def enable_plugin_webrtc_zmq(
        self,
        name: str,
        node_id: str,
        *,
        endpoint: str | None = None,
        bind: bool | None = None,
        webrtc_options: Any | None = None,
        reconnect: bool | None = None,
        connect_timeout: float | None = None,
    ) -> None:
        """
        Enable a remote plugin over a dedicated WebRTC peer connection, using
        ZMQ as the (broker-less) signaling channel.

        Args:
            name:           Plugin name as registered in the plugin registry
                            (e.g. ``"realsense-driver"``).
            node_id:        Plugin's ZMQ node identifier, used as the WebRTC
                            session ID for signaling
                            (e.g. ``"qtrobot-realsense-driver"``).
            endpoint:       ZMQ endpoint for WebRTC signaling
                            (e.g. ``"tcp://192.168.1.10:5556"``).
            bind:           ``True`` → bind the ZMQ socket; ``False`` → connect (default).
            webrtc_options: Optional :class:`luxai.robot.WebRTCOptions` for
                            the WebRTC peer (STUN/TURN, codec prefs, etc.).
            reconnect:      Automatically re-establish if the connection drops.
            connect_timeout: End-to-end timeout (seconds) for signaling + handshake.

        Examples:
            robot.enable_plugin_webrtc_zmq(
                "realsense-driver",
                node_id="qtrobot-realsense-driver",
                endpoint="tcp://192.168.1.10:5556",
            )
        """
        ...

    def disable_plugin(self, name: str) -> None:
        """
        Disable (stop + remove) a previously enabled plugin.
        """
        ...

    # --- AUTO-GENERATED ROBOT NAMESPACES ---
