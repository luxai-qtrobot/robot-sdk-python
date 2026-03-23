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

    def __init__(
        self,
        transport: Transport,
        *,
        connect_timeout: float = 5.0,
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

    def enable_plugin_zmq(self, name: str, endpoint: str | None = None) -> None:
        """
        Enable a plugin by name (string) over ZMQ transport.

        Examples:
            robot.enable_plugin("realsense-driver") # lets discovery find the it
            robot.enable_plugin("realsense-driver", endpoint="tcp://192.168.3.152:50655")
        """
        ...

    def disable_plugin(self, name: str) -> None:
        """
        Disable (stop + remove) a previously enabled plugin.
        """
        ...

    # --- AUTO-GENERATED ROBOT NAMESPACES ---
