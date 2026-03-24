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

    @property
    def asr(self) -> AsrAPI:
        """Namespace view for asr APIs."""
        ...

    @property
    def camera(self) -> CameraAPI:
        """Namespace view for camera APIs."""
        ...

    @property
    def face(self) -> FaceAPI:
        """Namespace view for face APIs."""
        ...

    @property
    def gesture(self) -> GestureAPI:
        """Namespace view for gesture APIs."""
        ...

    @property
    def media(self) -> MediaAPI:
        """Namespace view for media APIs."""
        ...

    @property
    def microphone(self) -> MicrophoneAPI:
        """Namespace view for microphone APIs."""
        ...

    @property
    def motor(self) -> MotorAPI:
        """Namespace view for motor APIs."""
        ...

    @property
    def speaker(self) -> SpeakerAPI:
        """Namespace view for speaker APIs."""
        ...

    @property
    def tts(self) -> TtsAPI:
        """Namespace view for tts APIs."""
        ...



class AsrStreamAPI:
    """Stream APIs for asr namespace."""

    def open_azure_speech_reader(self, queue_size: int | None = ...) -> TypedStreamReader[DictFrame]:
        """
        Outbound stream of recognised speech segments from Azure ASR.

        Published in both one-shot (``recognize_azure()``) and continuous modes.
        Frame type is DictFrame with fields: 'text', 'confidence', 'language', etc.

        Typical usage:
            def on_speech(frame):
                print(frame.value.get('text'))
            sub = robot.asr.stream.on_azure_speech(on_speech)
        """
        ...

    def on_azure_speech(self, callback: Callable[[DictFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of recognised speech segments from Azure ASR.

        Published in both one-shot (``recognize_azure()``) and continuous modes.
        Frame type is DictFrame with fields: 'text', 'confidence', 'language', etc.

        Typical usage:
            def on_speech(frame):
                print(frame.value.get('text'))
            sub = robot.asr.stream.on_azure_speech(on_speech)
        """
        ...

    def open_azure_event_reader(self, queue_size: int | None = ...) -> TypedStreamReader[StringFrame]:
        """
        Outbound stream of speech recognition lifecycle events from Azure ASR.

        Frame type is StringFrame. Possible values include:
          'recognizing', 'recognized', 'canceled', 'session_started', 'session_stopped'.

        Typical usage:
            def on_event(frame):
                print(frame.value)  # e.g. 'recognized'
            sub = robot.asr.stream.on_azure_event(on_event)
        """
        ...

    def on_azure_event(self, callback: Callable[[StringFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of speech recognition lifecycle events from Azure ASR.

        Frame type is StringFrame. Possible values include:
          'recognizing', 'recognized', 'canceled', 'session_started', 'session_stopped'.

        Typical usage:
            def on_event(frame):
                print(frame.value)  # e.g. 'recognized'
            sub = robot.asr.stream.on_azure_event(on_event)
        """
        ...

    def open_riva_speech_reader(self, queue_size: int | None = ...) -> TypedStreamReader[DictFrame]:
        """
        Outbound stream of recognised speech segments from Nvidia Riva ASR.

        Published in both one-shot (``recognize_riva()``) and continuous modes.
        Frame type is DictFrame with fields: 'text' and 'language'.

        Typical usage:
            def on_speech(frame):
                print(frame.value.get('text'))
            sub = robot.asr.stream.on_riva_speech(on_speech)
        """
        ...

    def on_riva_speech(self, callback: Callable[[DictFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of recognised speech segments from Nvidia Riva ASR.

        Published in both one-shot (``recognize_riva()``) and continuous modes.
        Frame type is DictFrame with fields: 'text' and 'language'.

        Typical usage:
            def on_speech(frame):
                print(frame.value.get('text'))
            sub = robot.asr.stream.on_riva_speech(on_speech)
        """
        ...

    def open_riva_event_reader(self, queue_size: int | None = ...) -> TypedStreamReader[StringFrame]:
        """
        Outbound stream of speech recognition lifecycle events from Nvidia Riva ASR.

        Frame type is StringFrame. Possible values:
          'STARTED', 'RECOGNIZING', 'RECOGNIZED', 'STOPPED', 'CANCELED'.

        Typical usage:
            def on_event(frame):
                print(frame.value)  # e.g. 'RECOGNIZED'
            sub = robot.asr.stream.on_riva_event(on_event)
        """
        ...

    def on_riva_event(self, callback: Callable[[StringFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of speech recognition lifecycle events from Nvidia Riva ASR.

        Frame type is StringFrame. Possible values:
          'STARTED', 'RECOGNIZING', 'RECOGNIZED', 'STOPPED', 'CANCELED'.

        Typical usage:
            def on_event(frame):
                print(frame.value)  # e.g. 'RECOGNIZED'
            sub = robot.asr.stream.on_riva_event(on_event)
        """
        ...

    def open_groq_speech_reader(self, queue_size: int | None = ...) -> TypedStreamReader[DictFrame]:
        """
        Outbound stream of transcribed speech segments from Groq Whisper ASR.

        Published in both one-shot (``recognize_groq()``) and continuous modes.
        Frame type is DictFrame with fields: 'text' and 'language'.

        Typical usage:
            def on_speech(frame):
                print(frame.value.get('text'))
            sub = robot.asr.stream.on_groq_speech(on_speech)
        """
        ...

    def on_groq_speech(self, callback: Callable[[DictFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of transcribed speech segments from Groq Whisper ASR.

        Published in both one-shot (``recognize_groq()``) and continuous modes.
        Frame type is DictFrame with fields: 'text' and 'language'.

        Typical usage:
            def on_speech(frame):
                print(frame.value.get('text'))
            sub = robot.asr.stream.on_groq_speech(on_speech)
        """
        ...

    def open_groq_event_reader(self, queue_size: int | None = ...) -> TypedStreamReader[StringFrame]:
        """
        Outbound stream of speech recognition lifecycle events from Groq Whisper ASR.

        Frame type is StringFrame. Possible values:
          'STARTED', 'RECOGNIZING', 'RECOGNIZED', 'STOPPED', 'CANCELED'.

        Typical usage:
            def on_event(frame):
                print(frame.value)  # e.g. 'RECOGNIZED'
            sub = robot.asr.stream.on_groq_event(on_event)
        """
        ...

    def on_groq_event(self, callback: Callable[[StringFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of speech recognition lifecycle events from Groq Whisper ASR.

        Frame type is StringFrame. Possible values:
          'STARTED', 'RECOGNIZING', 'RECOGNIZED', 'STOPPED', 'CANCELED'.

        Typical usage:
            def on_event(frame):
                print(frame.value)  # e.g. 'RECOGNIZED'
            sub = robot.asr.stream.on_groq_event(on_event)
        """
        ...


class AsrAPI:
    """Namespace for asr RPC/stream APIs."""

    def configure_azure(self, subscription: str, region: str, languages: List = ..., silence_timeout: float = ..., use_vad: bool = ..., continuous_mode: bool = ...) -> bool:
        """
        Configure the Azure ASR engine with credentials and recognition settings.

        Must be called once before using ``recognize_azure()`` or subscribing
        to the ``asr.azure_speech`` / ``asr.azure_event`` streams.

        Args:
            subscription (str): Azure Speech subscription key.
            region (str): Azure Speech region (e.g. 'westeurope').
            languages (list): Language codes to recognise (default ['en-US']).
            silence_timeout (float): Silence end-of-speech threshold in seconds (default 0.2).
            use_vad (bool): Enable voice-activity detection (default False).
            continuous_mode (bool): Enable continuous recognition mode (default False).

        Returns:
            bool: True if configured successfully.

        Example:
            ok = robot.asr.configure_azure(
                subscription='<key>',
                region='westeurope',
                continuous_mode=True,
                use_vad=True,
            )
        """
        ...

    def recognize_azure(self) -> dict:
        """
        Perform a single speech recognition with the Azure ASR engine.

        Blocks until a complete utterance is recognised and returns the result.
        For non-blocking use, call ``recognize_azure_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to abort recognition.

        Returns:
            dict: Recognition result with fields such as 'text', 'confidence', etc.

        Examples:
            # Blocking
            result = robot.asr.recognize_azure()
            print(result.get('text'))

            # Non-blocking
            h = robot.asr.recognize_azure_async()
            result = h.result()
            print(result.get('text'))
        """
        ...

    def recognize_azure_async(self) -> ActionHandle:
        """
        Perform a single speech recognition with the Azure ASR engine.

        Blocks until a complete utterance is recognised and returns the result.
        For non-blocking use, call ``recognize_azure_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to abort recognition.

        Returns:
            dict: Recognition result with fields such as 'text', 'confidence', etc.

        Examples:
            # Blocking
            result = robot.asr.recognize_azure()
            print(result.get('text'))

            # Non-blocking
            h = robot.asr.recognize_azure_async()
            result = h.result()
            print(result.get('text'))
        """
        ...

    def configure_riva(self, server: str = ..., language: str = ..., use_ssl: bool = ..., ssl_cert: str | None = None, profanity_filter: bool = ..., automatic_punctuation: bool = ..., use_vad: bool = ..., continuous_mode: bool = ...) -> bool:
        """
        Configure the Nvidia Riva ASR engine with server address and recognition settings.

        Must be called once before using ``recognize_riva()`` or subscribing
        to the ``asr.riva_speech`` / ``asr.riva_event`` streams.

        Args:
            server (str): Riva server address (default 'localhost:50051').
            language (str): BCP-47 language code (default 'en-US').
            use_ssl (bool): Use SSL/TLS for the gRPC connection (default False).
            ssl_cert (str): Path to SSL certificate file (default None).
            profanity_filter (bool): Enable profanity filtering (default False).
            automatic_punctuation (bool): Enable automatic punctuation (default True).
            use_vad (bool): Enable client-side voice-activity detection (default False).
            continuous_mode (bool): Enable continuous recognition mode (default False).

        Returns:
            bool: True if configured successfully.

        Example:
            ok = robot.asr.configure_riva(
                server='localhost:50051',
                language='en-US',
                continuous_mode=True,
                use_vad=True,
            )
        """
        ...

    def recognize_riva(self) -> dict:
        """
        Perform a single speech recognition with the Nvidia Riva ASR engine.

        Blocks until a complete utterance is recognised and returns the result.
        For non-blocking use, call ``recognize_riva_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to abort recognition.

        Returns:
            dict: Recognition result with fields 'text' and 'language'.

        Examples:
            # Blocking
            result = robot.asr.recognize_riva()
            print(result.get('text'))

            # Non-blocking
            h = robot.asr.recognize_riva_async()
            result = h.result()
            print(result.get('text'))
        """
        ...

    def recognize_riva_async(self) -> ActionHandle:
        """
        Perform a single speech recognition with the Nvidia Riva ASR engine.

        Blocks until a complete utterance is recognised and returns the result.
        For non-blocking use, call ``recognize_riva_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to abort recognition.

        Returns:
            dict: Recognition result with fields 'text' and 'language'.

        Examples:
            # Blocking
            result = robot.asr.recognize_riva()
            print(result.get('text'))

            # Non-blocking
            h = robot.asr.recognize_riva_async()
            result = h.result()
            print(result.get('text'))
        """
        ...

    def configure_groq(self, api_key: str, language: str = ..., context_prompt: str | None = None, silence_timeout: float = ..., use_vad: bool = ..., continuous_mode: bool = ...) -> bool:
        """
        Configure the Groq Whisper ASR engine.

        Must be called once before using ``recognize_groq()`` or subscribing
        to the ``asr.groq_speech`` / ``asr.groq_event`` streams.

        Args:
            api_key (str): Groq API key.
            language (str): ISO-639-1 language code (e.g. 'en', 'fr'). Default 'en'.
            context_prompt (str): Optional domain hint for Whisper (max 224 chars).
            silence_timeout (float): Seconds of silence that end an utterance (default 0.5).
            use_vad (bool): Enable client-side voice-activity detection (default True).
            continuous_mode (bool): Enable continuous recognition mode (default False).

        Returns:
            bool: True if configured successfully.

        Example:
            ok = robot.asr.configure_groq(
                api_key='<your-groq-api-key>',
                language='en',
                continuous_mode=True,
            )
        """
        ...

    def recognize_groq(self) -> dict:
        """
        Perform a single speech recognition with the Groq Whisper ASR engine.

        Blocks until voice activity is detected, one utterance is captured
        (ended by silence), and Groq transcribes it via the Whisper API.
        For non-blocking use, call ``recognize_groq_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to abort recognition.

        Returns:
            dict: Recognition result with fields 'text' and 'language'.

        Examples:
            # Blocking
            result = robot.asr.recognize_groq()
            print(result.get('text'))

            # Non-blocking
            h = robot.asr.recognize_groq_async()
            result = h.result()
            print(result.get('text'))
        """
        ...

    def recognize_groq_async(self) -> ActionHandle:
        """
        Perform a single speech recognition with the Groq Whisper ASR engine.

        Blocks until voice activity is detected, one utterance is captured
        (ended by silence), and Groq transcribes it via the Whisper API.
        For non-blocking use, call ``recognize_groq_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to abort recognition.

        Returns:
            dict: Recognition result with fields 'text' and 'language'.

        Examples:
            # Blocking
            result = robot.asr.recognize_groq()
            print(result.get('text'))

            # Non-blocking
            h = robot.asr.recognize_groq_async()
            result = h.result()
            print(result.get('text'))
        """
        ...

    @property
    def stream(self) -> AsrStreamAPI:
        """Stream namespace for asr APIs."""
        ...


class CameraStreamAPI:
    """Stream APIs for camera namespace."""

    def open_color_reader(self, queue_size: int | None = ...) -> TypedStreamReader[ImageFrameRaw]:
        """
        Outbound color image stream from the RealSense camera.

        Frame type is ImageFrameRaw (BGR, width x height x 3).

        Typical usage:
            reader = robot.camera.stream.open_color_reader()
            frame = reader.read(timeout=3.0)
        """
        ...

    def on_color(self, callback: Callable[[ImageFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound color image stream from the RealSense camera.

        Frame type is ImageFrameRaw (BGR, width x height x 3).

        Typical usage:
            reader = robot.camera.stream.open_color_reader()
            frame = reader.read(timeout=3.0)
        """
        ...

    def open_depth_reader(self, queue_size: int | None = ...) -> TypedStreamReader[ImageFrameRaw]:
        """
        Outbound depth image stream from the RealSense camera.

        Frame type is ImageFrameRaw (16-bit depth, width x height).

        Typical usage:
            reader = robot.camera.stream.open_depth_reader()
            frame = reader.read(timeout=3.0)
        """
        ...

    def on_depth(self, callback: Callable[[ImageFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound depth image stream from the RealSense camera.

        Frame type is ImageFrameRaw (16-bit depth, width x height).

        Typical usage:
            reader = robot.camera.stream.open_depth_reader()
            frame = reader.read(timeout=3.0)
        """
        ...

    def open_depth_aligned_reader(self, queue_size: int | None = ...) -> TypedStreamReader[ImageFrameRaw]:
        """
        Outbound depth image aligned to the color frame from the RealSense camera.

        Frame type is ImageFrameRaw (16-bit depth, same resolution as color).

        Typical usage:
            reader = robot.camera.stream.open_depth_aligned_reader()
            frame = reader.read(timeout=3.0)
        """
        ...

    def on_depth_aligned(self, callback: Callable[[ImageFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound depth image aligned to the color frame from the RealSense camera.

        Frame type is ImageFrameRaw (16-bit depth, same resolution as color).

        Typical usage:
            reader = robot.camera.stream.open_depth_aligned_reader()
            frame = reader.read(timeout=3.0)
        """
        ...

    def open_depth_color_reader(self, queue_size: int | None = ...) -> TypedStreamReader[ImageFrameRaw]:
        """
        Outbound false-colour depth image stream from the RealSense camera.

        Frame type is ImageFrameRaw (BGR, colourised for visualisation).

        Typical usage:
            reader = robot.camera.stream.open_depth_color_reader()
            frame = reader.read(timeout=3.0)
        """
        ...

    def on_depth_color(self, callback: Callable[[ImageFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound false-colour depth image stream from the RealSense camera.

        Frame type is ImageFrameRaw (BGR, colourised for visualisation).

        Typical usage:
            reader = robot.camera.stream.open_depth_color_reader()
            frame = reader.read(timeout=3.0)
        """
        ...

    def open_gyro_reader(self, queue_size: int | None = ...) -> TypedStreamReader[ListFrame]:
        """
        Outbound gyroscope stream from the RealSense IMU.

        Frame type is ListFrame: [x, y, z] angular velocity (rad/s).

        Typical usage:
            def on_gyro(frame):
                print(frame.value)  # [x, y, z]
            sub = robot.camera.stream.on_gyro(on_gyro)
        """
        ...

    def on_gyro(self, callback: Callable[[ListFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound gyroscope stream from the RealSense IMU.

        Frame type is ListFrame: [x, y, z] angular velocity (rad/s).

        Typical usage:
            def on_gyro(frame):
                print(frame.value)  # [x, y, z]
            sub = robot.camera.stream.on_gyro(on_gyro)
        """
        ...

    def open_acceleration_reader(self, queue_size: int | None = ...) -> TypedStreamReader[ListFrame]:
        """
        Outbound accelerometer stream from the RealSense IMU.

        Frame type is ListFrame: [x, y, z] linear acceleration (m/s²).

        Typical usage:
            def on_accel(frame):
                print(frame.value)  # [x, y, z]
            sub = robot.camera.stream.on_acceleration(on_accel)
        """
        ...

    def on_acceleration(self, callback: Callable[[ListFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound accelerometer stream from the RealSense IMU.

        Frame type is ListFrame: [x, y, z] linear acceleration (m/s²).

        Typical usage:
            def on_accel(frame):
                print(frame.value)  # [x, y, z]
            sub = robot.camera.stream.on_acceleration(on_accel)
        """
        ...


class CameraAPI:
    """Namespace for camera RPC/stream APIs."""

    def get_color_intrinsics(self) -> dict:
        """
        Get color camera intrinsic parameters.

        Returns:
            dict: Intrinsics dict (fx, fy, ppx, ppy, width, height, model, coeffs).

        Example:
            intr = robot.camera.get_color_intrinsics()
        """
        ...

    def get_depth_intrinsics(self) -> dict:
        """
        Get depth camera intrinsic parameters.

        Returns:
            dict: Intrinsics dict (fx, fy, ppx, ppy, width, height, model, coeffs).

        Example:
            intr = robot.camera.get_depth_intrinsics()
        """
        ...

    def get_depth_scale(self) -> dict:
        """
        Get the depth scale factor (metres per depth unit).

        Returns:
            dict: {'scale': float} where scale converts raw depth units to metres.

        Example:
            info = robot.camera.get_depth_scale()
            scale = info['scale']
        """
        ...

    @property
    def stream(self) -> CameraStreamAPI:
        """Stream namespace for camera APIs."""
        ...


class FaceAPI:
    """Namespace for face RPC/stream APIs."""

    def look(self, l_eye: list, r_eye: list, duration: float = ...) -> None:
        """
        Move (offset) the eyes on the face display.

        Offsets are applied relative to the configured center positions.
        If duration > 0, eyes reset back to center after the given seconds.

        Args:
            l_eye (list): [dx, dy] offset for left eye (pixels).
            r_eye (list): [dx, dy] offset for right eye (pixels).
            duration (float): Optional reset delay in seconds (default 0.0).

        Returns:
            None

        Examples:
            robot.face.look(l_eye=[30, 0], r_eye=[30, 0])          # look right
            robot.face.look(l_eye=[0, 0], r_eye=[0, 0], duration=2) # center, auto-reset
        """
        ...

    def show_emotion(self, emotion: str, speed: float | None = None) -> None:
        """
        Play an emotion video on the face background lane.

        Blocks until the emotion finishes playing and returns the result.
        For non-blocking use, call ``show_emotion_async()`` which returns
        an :class:`ActionHandle` — call ``.cancel()`` on it to stop the emotion early.

        Args:
            emotion (str): Emotion name or relative path (with/without .avi).
            speed (float): Optional playback speed factor.

        Returns:
            bool: True if playback completed, False otherwise.

        Examples:
            # Blocking
            robot.face.show_emotion('QT/kiss')
            robot.face.show_emotion('QT/surprise', speed=2.0)

            # Non-blocking — cancel after 3 seconds
            h = robot.face.show_emotion_async('QT/breathing_exercise')
            time.sleep(3)
            h.cancel()
        """
        ...

    def show_emotion_async(self, emotion: str, speed: float | None = None) -> ActionHandle:
        """
        Play an emotion video on the face background lane.

        Blocks until the emotion finishes playing and returns the result.
        For non-blocking use, call ``show_emotion_async()`` which returns
        an :class:`ActionHandle` — call ``.cancel()`` on it to stop the emotion early.

        Args:
            emotion (str): Emotion name or relative path (with/without .avi).
            speed (float): Optional playback speed factor.

        Returns:
            bool: True if playback completed, False otherwise.

        Examples:
            # Blocking
            robot.face.show_emotion('QT/kiss')
            robot.face.show_emotion('QT/surprise', speed=2.0)

            # Non-blocking — cancel after 3 seconds
            h = robot.face.show_emotion_async('QT/breathing_exercise')
            time.sleep(3)
            h.cancel()
        """
        ...

    def list_emotions(self) -> list:
        """
        List available emotion video files under the emotions directory.

        Scans recursively and returns relative paths for .avi/.AVI files.

        Returns:
            list: List[str] of emotion file paths.

        Example:
            emotions = robot.face.list_emotions()
            for e in emotions:
                print(e)
        """
        ...


class GestureStreamAPI:
    """Stream APIs for gesture namespace."""

    def open_progress_reader(self, queue_size: int | None = ...) -> TypedStreamReader[DictFrame]:
        """
        Outbound stream of gesture playback progress.

        Publishes a DictFrame with fields:
          percentage (float), time_us (int)

        Typical usage:
            def on_progress(frame):
                print(f"{frame.value['percentage']:.1f}%")
            sub = robot.gesture.stream.on_progress(on_progress)
        """
        ...

    def on_progress(self, callback: Callable[[DictFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of gesture playback progress.

        Publishes a DictFrame with fields:
          percentage (float), time_us (int)

        Typical usage:
            def on_progress(frame):
                print(f"{frame.value['percentage']:.1f}%")
            sub = robot.gesture.stream.on_progress(on_progress)
        """
        ...


class GestureAPI:
    """Namespace for gesture RPC/stream APIs."""

    def record(self, motors: list, release_motors: bool = ..., delay_start_ms: int = ..., timeout_ms: int = ..., refine_keyframe: bool = ..., keyframe_pos_eps: float = ..., keyframe_max_gap_us: int = ...) -> dict:
        """
        Start recording a gesture trajectory for selected motors.

        Blocks until recording finishes (timeout or manual stop) and returns
        the captured trajectory dict.
        For non-blocking use (e.g. stop recording on user input), call
        ``record_async()`` which returns an :class:`ActionHandle`, then call
        ``gesture.stop_record()`` to end recording and ``handle.result()`` to
        retrieve the trajectory.

        Args:
            motors (list): List[str] of motor names to record.
            release_motors (bool): If True, torque is disabled during recording.
            delay_start_ms (int): Delay before recording starts (ms, default 0).
            timeout_ms (int): Max recording duration (ms, default 60000).
            refine_keyframe (bool): If True, compress redundant keyframes.
            keyframe_pos_eps (float): Position epsilon for keyframe compression (deg).
            keyframe_max_gap_us (int): Max gap for keyframe compression (μs).

        Returns:
            dict: Trajectory dict with 'meta' and 'points'.

        Examples:
            # Non-blocking — stop on user input
            h = robot.gesture.record_async(
                motors=['RightShoulderPitch', 'RightElbowRoll'],
                release_motors=True,
                delay_start_ms=2000,
                timeout_ms=20000,
            )
            input('Press Enter to stop...')
            robot.gesture.stop_record()
            keyframes = h.result()
        """
        ...

    def record_async(self, motors: list, release_motors: bool = ..., delay_start_ms: int = ..., timeout_ms: int = ..., refine_keyframe: bool = ..., keyframe_pos_eps: float = ..., keyframe_max_gap_us: int = ...) -> ActionHandle:
        """
        Start recording a gesture trajectory for selected motors.

        Blocks until recording finishes (timeout or manual stop) and returns
        the captured trajectory dict.
        For non-blocking use (e.g. stop recording on user input), call
        ``record_async()`` which returns an :class:`ActionHandle`, then call
        ``gesture.stop_record()`` to end recording and ``handle.result()`` to
        retrieve the trajectory.

        Args:
            motors (list): List[str] of motor names to record.
            release_motors (bool): If True, torque is disabled during recording.
            delay_start_ms (int): Delay before recording starts (ms, default 0).
            timeout_ms (int): Max recording duration (ms, default 60000).
            refine_keyframe (bool): If True, compress redundant keyframes.
            keyframe_pos_eps (float): Position epsilon for keyframe compression (deg).
            keyframe_max_gap_us (int): Max gap for keyframe compression (μs).

        Returns:
            dict: Trajectory dict with 'meta' and 'points'.

        Examples:
            # Non-blocking — stop on user input
            h = robot.gesture.record_async(
                motors=['RightShoulderPitch', 'RightElbowRoll'],
                release_motors=True,
                delay_start_ms=2000,
                timeout_ms=20000,
            )
            input('Press Enter to stop...')
            robot.gesture.stop_record()
            keyframes = h.result()
        """
        ...

    def stop_record(self) -> bool:
        """
        Stop an in-progress gesture recording.

        Returns:
            bool: True if a recording was stopped, False if none was in progress.

        Example:
            robot.gesture.stop_record()
        """
        ...

    def store_record(self, gesture: str) -> None:
        """
        Store the last recorded gesture trajectory to an XML file.

        Args:
            gesture (str): Gesture name/path (saved as <gesture>.xml).

        Returns:
            bool: True if saved successfully.

        Example:
            robot.gesture.store_record('my_wave')
        """
        ...

    def play(self, keyframes: dict, resample: bool = ..., rate_hz: float = ..., speed_factor: float = ...) -> None:
        """
        Play a gesture trajectory (keyframes dict).

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            keyframes (dict): Trajectory dict (as returned by ``gesture.record()``).
            resample (bool): If True, resample for smooth playback (default True).
            rate_hz (float): Resample rate in Hz (default 100.0).
            speed_factor (float): Playback speed multiplier (default 1.0).

        Returns:
            bool: True if playback completed successfully.

        Notes:
            Progress is published on the ``gesture.progress`` stream.

        Examples:
            # Blocking
            robot.gesture.play(keyframes)

            # Non-blocking — cancel on demand
            h = robot.gesture.play_async(keyframes)
            h.cancel()
        """
        ...

    def play_async(self, keyframes: dict, resample: bool = ..., rate_hz: float = ..., speed_factor: float = ...) -> ActionHandle:
        """
        Play a gesture trajectory (keyframes dict).

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            keyframes (dict): Trajectory dict (as returned by ``gesture.record()``).
            resample (bool): If True, resample for smooth playback (default True).
            rate_hz (float): Resample rate in Hz (default 100.0).
            speed_factor (float): Playback speed multiplier (default 1.0).

        Returns:
            bool: True if playback completed successfully.

        Notes:
            Progress is published on the ``gesture.progress`` stream.

        Examples:
            # Blocking
            robot.gesture.play(keyframes)

            # Non-blocking — cancel on demand
            h = robot.gesture.play_async(keyframes)
            h.cancel()
        """
        ...

    def play_file(self, gesture: str, speed_factor: float = ...) -> bool:
        """
        Load a gesture XML file and play it.

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_file_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            gesture (str): Gesture name/path (with/without .xml).
            speed_factor (float): Playback speed multiplier (default 1.0).

        Returns:
            bool: True if loaded and played successfully.

        Examples:
            # Blocking — wait for gesture to complete
            robot.gesture.play_file('QT/wave')

            # Non-blocking — cancel on user input
            h = robot.gesture.play_file_async('QT/bye')
            input('Press Enter to cancel...')
            h.cancel()
        """
        ...

    def play_file_async(self, gesture: str, speed_factor: float = ...) -> ActionHandle:
        """
        Load a gesture XML file and play it.

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_file_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            gesture (str): Gesture name/path (with/without .xml).
            speed_factor (float): Playback speed multiplier (default 1.0).

        Returns:
            bool: True if loaded and played successfully.

        Examples:
            # Blocking — wait for gesture to complete
            robot.gesture.play_file('QT/wave')

            # Non-blocking — cancel on user input
            h = robot.gesture.play_file_async('QT/bye')
            input('Press Enter to cancel...')
            h.cancel()
        """
        ...

    def list_files(self) -> list:
        """
        List available gesture XML files under the configured gesture directory.

        Returns:
            list: List[str] of gesture file paths.

        Example:
            gestures = robot.gesture.list_files()
            for g in gestures:
                print(g)
        """
        ...

    @property
    def stream(self) -> GestureStreamAPI:
        """Stream namespace for gesture APIs."""
        ...


class MediaStreamAPI:
    """Stream APIs for media namespace."""

    def open_fg_audio_stream_writer(self, queue_size: int | None = ...) -> TypedStreamWriter[AudioFrameRaw]:
        """
        Inbound audio stream to the media FG audio lane.

        Send AudioFrameRaw frames to this topic to play streamed audio.

        Typical usage:
            writer = robot.media.stream.open_fg_audio_stream_writer()
            writer.write(AudioFrameRaw(...))

        Notes:
            Use ``media.cancel_fg_audio_stream()`` / ``pause`` / ``resume`` to control the pipeline.
        """
        ...

    def open_bg_audio_stream_writer(self, queue_size: int | None = ...) -> TypedStreamWriter[AudioFrameRaw]:
        """
        Inbound audio stream to the media BG audio lane.

        Send AudioFrameRaw frames to this topic to play streamed background audio.

        Typical usage:
            writer = robot.media.stream.open_bg_audio_stream_writer()
            writer.write(AudioFrameRaw(...))

        Notes:
            Use ``media.cancel_bg_audio_stream()`` / ``pause`` / ``resume`` to control the pipeline.
        """
        ...

    def open_fg_video_stream_writer(self, queue_size: int | None = ...) -> TypedStreamWriter[ImageFrameRaw]:
        """
        Inbound video stream to the media FG video lane.

        Send ImageFrameRaw frames to this topic to render streamed foreground video.

        Typical usage:
            writer = robot.media.stream.open_fg_video_stream_writer()
            writer.write(ImageFrameRaw(...))
        """
        ...

    def open_bg_video_stream_writer(self, queue_size: int | None = ...) -> TypedStreamWriter[ImageFrameRaw]:
        """
        Inbound video stream to the media BG video lane.

        Send ImageFrameRaw frames to this topic to render streamed background video.

        Typical usage:
            writer = robot.media.stream.open_bg_video_stream_writer()
            writer.write(ImageFrameRaw(...))
        """
        ...


class MediaAPI:
    """Namespace for media RPC/stream APIs."""

    def play_fg_audio_file(self, uri: str) -> bool:
        """
        Play an audio file on the foreground (FG) audio lane.

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_fg_audio_file_async()`` which returns
        an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            uri (str): Audio file URI/path supported by the engine.

        Returns:
            bool: True if playback completed successfully, False otherwise.

        Examples:
            # Blocking — wait for file to finish
            ok = robot.media.play_fg_audio_file('/data/audio/hello.wav')

            # Non-blocking — cancel after 3 seconds
            h = robot.media.play_fg_audio_file_async('/data/audio/hello.wav')
            time.sleep(3)
            h.cancel()
        """
        ...

    def play_fg_audio_file_async(self, uri: str) -> ActionHandle:
        """
        Play an audio file on the foreground (FG) audio lane.

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_fg_audio_file_async()`` which returns
        an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            uri (str): Audio file URI/path supported by the engine.

        Returns:
            bool: True if playback completed successfully, False otherwise.

        Examples:
            # Blocking — wait for file to finish
            ok = robot.media.play_fg_audio_file('/data/audio/hello.wav')

            # Non-blocking — cancel after 3 seconds
            h = robot.media.play_fg_audio_file_async('/data/audio/hello.wav')
            time.sleep(3)
            h.cancel()
        """
        ...

    def pause_fg_audio_file(self) -> None:
        """
        Pause current foreground (FG) audio file playback.

        Returns:
            None
        """
        ...

    def resume_fg_audio_file(self) -> None:
        """
        Resume foreground (FG) audio file playback after pause.

        Returns:
            None
        """
        ...

    def cancel_fg_audio_stream(self) -> None:
        """
        Cancel / stop the current foreground (FG) audio stream pipeline.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def pause_fg_audio_stream(self) -> None:
        """
        Pause foreground (FG) audio stream processing.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def resume_fg_audio_stream(self) -> None:
        """
        Resume foreground (FG) audio stream processing.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def set_fg_audio_volume(self, value: float) -> None:
        """
        Set foreground (FG) audio lane volume.

        Args:
            value (float): Volume in range [0.0, 1.0].

        Returns:
            None

        Example:
            robot.media.set_fg_audio_volume(0.8)
        """
        ...

    def get_fg_audio_volume(self) -> float:
        """
        Get foreground (FG) audio lane volume.

        Returns:
            float: Volume in range [0.0, 1.0].

        Example:
            vol = robot.media.get_fg_audio_volume()
        """
        ...

    def play_bg_audio_file(self, uri: str) -> bool:
        """
        Play an audio file on the background (BG) audio lane.

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_bg_audio_file_async()`` which returns
        an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            uri (str): Audio file URI/path supported by the engine.

        Returns:
            bool: True if playback completed successfully, False otherwise.

        Examples:
            # Blocking — wait for file to finish
            ok = robot.media.play_bg_audio_file('/data/audio/music.wav')

            # Non-blocking — cancel after 5 seconds
            h = robot.media.play_bg_audio_file_async('/data/audio/music.wav')
            time.sleep(5)
            h.cancel()
        """
        ...

    def play_bg_audio_file_async(self, uri: str) -> ActionHandle:
        """
        Play an audio file on the background (BG) audio lane.

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_bg_audio_file_async()`` which returns
        an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            uri (str): Audio file URI/path supported by the engine.

        Returns:
            bool: True if playback completed successfully, False otherwise.

        Examples:
            # Blocking — wait for file to finish
            ok = robot.media.play_bg_audio_file('/data/audio/music.wav')

            # Non-blocking — cancel after 5 seconds
            h = robot.media.play_bg_audio_file_async('/data/audio/music.wav')
            time.sleep(5)
            h.cancel()
        """
        ...

    def pause_bg_audio_file(self) -> None:
        """
        Pause current background (BG) audio file playback.

        Returns:
            None
        """
        ...

    def resume_bg_audio_file(self) -> None:
        """
        Resume background (BG) audio file playback after pause.

        Returns:
            None
        """
        ...

    def cancel_bg_audio_stream(self) -> None:
        """
        Cancel / stop the current background (BG) audio stream pipeline.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def pause_bg_audio_stream(self) -> None:
        """
        Pause background (BG) audio stream processing.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def resume_bg_audio_stream(self) -> None:
        """
        Resume background (BG) audio stream processing.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def set_bg_audio_volume(self, value: float) -> None:
        """
        Set background (BG) audio lane volume.

        Args:
            value (float): Volume in range [0.0, 1.0].

        Returns:
            None

        Example:
            robot.media.set_bg_audio_volume(0.5)
        """
        ...

    def get_bg_audio_volume(self) -> float:
        """
        Get background (BG) audio lane volume.

        Returns:
            float: Volume in range [0.0, 1.0].

        Example:
            vol = robot.media.get_bg_audio_volume()
        """
        ...

    def play_fg_video_file(self, uri: str, speed: float = ..., with_audio: bool = ...) -> bool:
        """
        Play a video file on the foreground (FG) video lane.

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_fg_video_file_async()`` which returns
        an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            uri (str): Video file URI/path supported by the engine.
            speed (float): Playback speed factor (default 1.0).
            with_audio (bool): If True, play embedded audio track (default False).

        Returns:
            bool: True if playback completed successfully, False otherwise.

        Examples:
            # Blocking
            ok = robot.media.play_fg_video_file('/data/video/intro.mp4')

            # Non-blocking
            h = robot.media.play_fg_video_file_async('/data/video/intro.mp4')
            h.cancel()
        """
        ...

    def play_fg_video_file_async(self, uri: str, speed: float = ..., with_audio: bool = ...) -> ActionHandle:
        """
        Play a video file on the foreground (FG) video lane.

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_fg_video_file_async()`` which returns
        an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            uri (str): Video file URI/path supported by the engine.
            speed (float): Playback speed factor (default 1.0).
            with_audio (bool): If True, play embedded audio track (default False).

        Returns:
            bool: True if playback completed successfully, False otherwise.

        Examples:
            # Blocking
            ok = robot.media.play_fg_video_file('/data/video/intro.mp4')

            # Non-blocking
            h = robot.media.play_fg_video_file_async('/data/video/intro.mp4')
            h.cancel()
        """
        ...

    def pause_fg_video_file(self) -> None:
        """
        Pause current foreground (FG) video file playback.

        Returns:
            None
        """
        ...

    def resume_fg_video_file(self) -> None:
        """
        Resume foreground (FG) video file playback after pause.

        Returns:
            None
        """
        ...

    def cancel_fg_video_stream(self) -> None:
        """
        Cancel / stop the current foreground (FG) video stream pipeline.

        This is for streamed video frames (not file playback).

        Returns:
            None
        """
        ...

    def pause_fg_video_stream(self) -> None:
        """
        Pause foreground (FG) video stream processing.

        This is for streamed video frames (not file playback).

        Returns:
            None
        """
        ...

    def resume_fg_video_stream(self) -> None:
        """
        Resume foreground (FG) video stream processing.

        This is for streamed video frames (not file playback).

        Returns:
            None
        """
        ...

    def set_fg_video_alpha(self, value: float) -> None:
        """
        Set foreground (FG) video alpha (transparency).

        Args:
            value (float): Alpha in range [0.0, 1.0] where 0.0 is fully transparent.

        Returns:
            None

        Example:
            robot.media.set_fg_video_alpha(0.8)
        """
        ...

    def play_bg_video_file(self, uri: str, speed: float = ..., with_audio: bool = ...) -> bool:
        """
        Play a video file on the background (BG) video lane.

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_bg_video_file_async()`` which returns
        an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            uri (str): Video file URI/path supported by the engine.
            speed (float): Playback speed factor (default 1.0).
            with_audio (bool): If True, play embedded audio track (default False).

        Returns:
            bool: True if playback completed successfully, False otherwise.

        Examples:
            # Blocking
            ok = robot.media.play_bg_video_file('/data/emotions/QT/kiss.avi')

            # Non-blocking — pause, then resume
            h = robot.media.play_bg_video_file_async('/data/emotions/QT/kiss.avi')
            time.sleep(2)
            robot.media.pause_bg_video_file()
            time.sleep(3)
            robot.media.resume_bg_video_file()
            h.wait()
        """
        ...

    def play_bg_video_file_async(self, uri: str, speed: float = ..., with_audio: bool = ...) -> ActionHandle:
        """
        Play a video file on the background (BG) video lane.

        Blocks until playback finishes and returns the result.
        For non-blocking use, call ``play_bg_video_file_async()`` which returns
        an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.

        Args:
            uri (str): Video file URI/path supported by the engine.
            speed (float): Playback speed factor (default 1.0).
            with_audio (bool): If True, play embedded audio track (default False).

        Returns:
            bool: True if playback completed successfully, False otherwise.

        Examples:
            # Blocking
            ok = robot.media.play_bg_video_file('/data/emotions/QT/kiss.avi')

            # Non-blocking — pause, then resume
            h = robot.media.play_bg_video_file_async('/data/emotions/QT/kiss.avi')
            time.sleep(2)
            robot.media.pause_bg_video_file()
            time.sleep(3)
            robot.media.resume_bg_video_file()
            h.wait()
        """
        ...

    def pause_bg_video_file(self) -> None:
        """
        Pause current background (BG) video file playback.

        Returns:
            None
        """
        ...

    def resume_bg_video_file(self) -> None:
        """
        Resume background (BG) video file playback after pause.

        Returns:
            None
        """
        ...

    def cancel_bg_video_stream(self) -> None:
        """
        Cancel / stop the current background (BG) video stream pipeline.

        This is for streamed video frames (not file playback).

        Returns:
            None
        """
        ...

    def pause_bg_video_stream(self) -> None:
        """
        Pause background (BG) video stream processing.

        This is for streamed video frames (not file playback).

        Returns:
            None
        """
        ...

    def resume_bg_video_stream(self) -> None:
        """
        Resume background (BG) video stream processing.

        This is for streamed video frames (not file playback).

        Returns:
            None
        """
        ...

    @property
    def stream(self) -> MediaStreamAPI:
        """Stream namespace for media APIs."""
        ...


class MicrophoneStreamAPI:
    """Stream APIs for microphone namespace."""

    def open_int_audio_ch0_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameRaw]:
        """
        Internal microphone audio stream channel 0 (mono).

        AudioFrameRaw stream published by MicrophoneNode.
        Channel 0 is the processed/ASR channel.

        Typical usage:
            def on_audio(frame: AudioFrameRaw):
                process(frame.data)
            sub = robot.microphone.stream.on_int_audio_ch0(on_audio, queue_size=10)

            # Or use a reader directly
            reader = robot.microphone.stream.open_int_audio_ch0_reader(queue_size=10)
            frame = reader.read(timeout=3.0)
        """
        ...

    def on_int_audio_ch0(self, callback: Callable[[AudioFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Internal microphone audio stream channel 0 (mono).

        AudioFrameRaw stream published by MicrophoneNode.
        Channel 0 is the processed/ASR channel.

        Typical usage:
            def on_audio(frame: AudioFrameRaw):
                process(frame.data)
            sub = robot.microphone.stream.on_int_audio_ch0(on_audio, queue_size=10)

            # Or use a reader directly
            reader = robot.microphone.stream.open_int_audio_ch0_reader(queue_size=10)
            frame = reader.read(timeout=3.0)
        """
        ...

    def open_int_audio_ch1_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameRaw]:
        """
        Internal microphone audio stream channel 1 (mono).

        AudioFrameRaw stream published by MicrophoneNode.
        Typically corresponds to physical mic 1 (raw), depending on ALSA layout.
        """
        ...

    def on_int_audio_ch1(self, callback: Callable[[AudioFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Internal microphone audio stream channel 1 (mono).

        AudioFrameRaw stream published by MicrophoneNode.
        Typically corresponds to physical mic 1 (raw), depending on ALSA layout.
        """
        ...

    def open_int_audio_ch2_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameRaw]:
        """
        Internal microphone audio stream channel 2 (mono).

        AudioFrameRaw stream published by MicrophoneNode.
        """
        ...

    def on_int_audio_ch2(self, callback: Callable[[AudioFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Internal microphone audio stream channel 2 (mono).

        AudioFrameRaw stream published by MicrophoneNode.
        """
        ...

    def open_int_audio_ch3_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameRaw]:
        """
        Internal microphone audio stream channel 3 (mono).

        AudioFrameRaw stream published by MicrophoneNode.
        """
        ...

    def on_int_audio_ch3(self, callback: Callable[[AudioFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Internal microphone audio stream channel 3 (mono).

        AudioFrameRaw stream published by MicrophoneNode.
        """
        ...

    def open_int_audio_ch4_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameRaw]:
        """
        Internal microphone audio stream channel 4 (mono).

        AudioFrameRaw stream published by MicrophoneNode.
        """
        ...

    def on_int_audio_ch4(self, callback: Callable[[AudioFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Internal microphone audio stream channel 4 (mono).

        AudioFrameRaw stream published by MicrophoneNode.
        """
        ...

    def open_int_event_reader(self, queue_size: int | None = ...) -> TypedStreamReader[DictFrame]:
        """
        Internal microphone event stream (VAD + direction-of-arrival).

        Publishes DictFrame events when voice activity changes.
        Payload fields:
            activity (bool): True when voice is detected.
            direction (int): Estimated direction-of-arrival in degrees.

        Typical usage:
            def on_evt(frame):
                evt = frame.value
                if evt.get('activity'):
                    print('Voice detected — DOA:', evt.get('direction'))
            sub = robot.microphone.stream.on_int_event(on_evt, queue_size=2)

        Notes:
            Stream delivery is 'latest' — events may be dropped if the consumer is slow.
        """
        ...

    def on_int_event(self, callback: Callable[[DictFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Internal microphone event stream (VAD + direction-of-arrival).

        Publishes DictFrame events when voice activity changes.
        Payload fields:
            activity (bool): True when voice is detected.
            direction (int): Estimated direction-of-arrival in degrees.

        Typical usage:
            def on_evt(frame):
                evt = frame.value
                if evt.get('activity'):
                    print('Voice detected — DOA:', evt.get('direction'))
            sub = robot.microphone.stream.on_int_event(on_evt, queue_size=2)

        Notes:
            Stream delivery is 'latest' — events may be dropped if the consumer is slow.
        """
        ...

    def open_ext_audio_ch0_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameRaw]:
        """
        External microphone audio stream channel 0 (mono).

        AudioFrameRaw stream published only if microphone.external.enabled is True.

        Typical usage:
            sub = robot.microphone.stream.on_ext_audio_ch0(cb, queue_size=10)
        """
        ...

    def on_ext_audio_ch0(self, callback: Callable[[AudioFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        External microphone audio stream channel 0 (mono).

        AudioFrameRaw stream published only if microphone.external.enabled is True.

        Typical usage:
            sub = robot.microphone.stream.on_ext_audio_ch0(cb, queue_size=10)
        """
        ...


class MicrophoneAPI:
    """Namespace for microphone RPC/stream APIs."""

    def get_int_tuning(self) -> dict:
        """
        Get all readable Respeaker (internal mic array) tuning parameters.

        Returns a dictionary of every readable parameter exposed by the
        Respeaker controller (keys are parameter names, values are numeric).

        Returns:
            dict: Mapping {param_name: value} for all readable params.

        Example:
            params = robot.microphone.get_int_tuning()
            print(params.get('AECNORM'))

        Notes:
            If the Respeaker device is not available, may return an empty dict.
        """
        ...

    def set_int_tuning(self, name: str, value: float) -> bool:
        """
        Set a Respeaker (internal mic array) tuning parameter.

        Args:
            name (str): Parameter name (e.g. 'AECNORM', 'AGCONOFF', ...).
            value (float): Value to set.

        Returns:
            bool: True if the parameter was set successfully.

        Example:
            ok = robot.microphone.set_int_tuning(name='AGCONOFF', value=1.0)

        Notes:
            Persistence is handled via config (microphone.tunning.*) applied at startup.
        """
        ...

    @property
    def stream(self) -> MicrophoneStreamAPI:
        """Stream namespace for microphone APIs."""
        ...


class MotorStreamAPI:
    """Stream APIs for motor namespace."""

    def open_joints_state_reader(self, queue_size: int | None = ...) -> TypedStreamReader[JointStateFrame]:
        """
        Outbound stream of joint states.

        Frame type is JointStateFrame mapping motor_name -> state:
          {position, velocity, effort, voltage, temperature}

        Typical usage:
            # Callback-based
            def on_state(frame: JointStateFrame):
                print(frame.position('HeadYaw'))
            sub = robot.motor.stream.on_joints_state(on_state)

            # Reader-based
            reader = robot.motor.stream.open_joints_state_reader()
            frame = reader.read()
        """
        ...

    def on_joints_state(self, callback: Callable[[JointStateFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of joint states.

        Frame type is JointStateFrame mapping motor_name -> state:
          {position, velocity, effort, voltage, temperature}

        Typical usage:
            # Callback-based
            def on_state(frame: JointStateFrame):
                print(frame.position('HeadYaw'))
            sub = robot.motor.stream.on_joints_state(on_state)

            # Reader-based
            reader = robot.motor.stream.open_joints_state_reader()
            frame = reader.read()
        """
        ...

    def open_joints_error_reader(self, queue_size: int | None = ...) -> TypedStreamReader[DictFrame]:
        """
        Outbound stream of motor error flags (when present).

        Frame payload is a DictFrame mapping motor_name -> error flags:
          {overload_limit?, voltage_limit?, temperature_limit?, sensor_failure?}

        Typical usage:
            def on_error(frame):
                print('Motor error:', frame.value)
            sub = robot.motor.stream.on_joints_error(on_error)
        """
        ...

    def on_joints_error(self, callback: Callable[[DictFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of motor error flags (when present).

        Frame payload is a DictFrame mapping motor_name -> error flags:
          {overload_limit?, voltage_limit?, temperature_limit?, sensor_failure?}

        Typical usage:
            def on_error(frame):
                print('Motor error:', frame.value)
            sub = robot.motor.stream.on_joints_error(on_error)
        """
        ...

    def open_joints_command_writer(self, queue_size: int | None = ...) -> TypedStreamWriter[JointCommandFrame]:
        """
        Inbound stream of joint commands.

        Send JointCommandFrame mapping motor_name -> command:
          {'position': float, 'velocity': float (optional)}

        Typical usage:
            writer = robot.motor.stream.open_joints_command_writer()
            cmd = JointCommandFrame()
            cmd.set_joint('HeadYaw', position=30, velocity=40)
            writer.write(cmd)
        """
        ...


class MotorAPI:
    """Namespace for motor RPC/stream APIs."""

    def list(self) -> dict:
        """
        List configured motors and their parameters.

        Returns:
            dict: {motor_name: {part, position_min, position_max, position_home,
                  velocity_max, calibration_offset, overload_threshold, ...}}

        Example:
            motors = robot.motor.list()
            for name, info in motors.items():
                print(name, info)
        """
        ...

    def set_calib(self, motor: str, offset: float | None = None, overload_threshold: int | None = None, velocity_max: int | None = None, store: bool = ...) -> None:
        """
        Set calibration parameters for a motor.

        Args:
            motor (str): Motor name.
            offset (float): Optional calibration offset in degrees.
            overload_threshold (int): Optional overload threshold value.
            velocity_max (int): Optional maximum velocity value.
            store (bool): If True, persist changes to config (default False).

        Returns:
            bool: True on success.

        Example:
            robot.motor.set_calib('HeadYaw', offset=2.5, store=True)
            robot.motor.set_calib('HeadYaw', overload_threshold=80.0, velocity_max=100.0)
        """
        ...

    def calib_all(self) -> None:
        """
        Run manual calibration procedure for all motors (writes offsets and stores them).

        Returns:
            bool: True on success.
        """
        ...

    def set_velocity(self, motor: str, velocity: int) -> None:
        """
        Set default velocity for a motor.

        Args:
            motor (str): Motor name.
            velocity (int): Velocity value; validated against the motor's max.

        Returns:
            bool: True on success.

        Example:
            robot.motor.set_velocity('HeadYaw', 50)
        """
        ...

    def on(self, motor: str) -> None:
        """
        Enable torque for a motor.

        Args:
            motor (str): Motor name.

        Returns:
            bool: True on success.

        Example:
            robot.motor.on('HeadYaw')
        """
        ...

    def off(self, motor: str) -> None:
        """
        Disable torque for a motor.

        Args:
            motor (str): Motor name.

        Returns:
            bool: True on success.

        Example:
            robot.motor.off('HeadYaw')
        """
        ...

    def on_all(self) -> None:
        """
        Enable torque for all motors.

        Returns:
            bool: True

        Example:
            robot.motor.on_all()
        """
        ...

    def off_all(self) -> None:
        """
        Disable torque for all motors.

        Returns:
            bool: True

        Example:
            robot.motor.off_all()
        """
        ...

    def home(self, motor: str) -> None:
        """
        Move a motor to its configured home position.

        Args:
            motor (str): Motor name.

        Returns:
            bool: True on success.

        Example:
            robot.motor.home('HeadYaw')
        """
        ...

    def home_all(self) -> None:
        """
        Move all motors to their configured home positions.

        Returns:
            bool: True

        Example:
            robot.motor.home_all()
        """
        ...

    @property
    def stream(self) -> MotorStreamAPI:
        """Stream namespace for motor APIs."""
        ...


class SpeakerAPI:
    """Namespace for speaker RPC/stream APIs."""

    def set_volume(self, value: float) -> bool:
        """
        Set the master speaker volume.

        Args:
            value (float): Volume in range [0.0, 1.0].

        Returns:
            bool: True if mixer control succeeded, False otherwise.

        Example:
            robot.speaker.set_volume(0.8)
        """
        ...

    def get_volume(self) -> float:
        """
        Get the master speaker volume.

        Returns:
            float: Volume in range [0.0, 1.0].

        Example:
            vol = robot.speaker.get_volume()
        """
        ...

    def mute(self) -> bool:
        """
        Mute the speaker output.

        Returns:
            bool: True if succeeded, False otherwise.

        Example:
            robot.speaker.mute()
        """
        ...

    def unmute(self) -> bool:
        """
        Unmute the speaker output.

        Returns:
            bool: True if succeeded, False otherwise.

        Example:
            robot.speaker.unmute()
        """
        ...


class TtsAPI:
    """Namespace for tts RPC/stream APIs."""

    def set_default_engine(self, engine: str) -> None:
        """
        Set the default TTS engine id.

        Args:
            engine (str): Engine id (e.g. 'acapela', 'azure', or custom).

        Returns:
            None

        Example:
            robot.tts.set_default_engine('acapela')
        """
        ...

    def get_default_engine(self) -> str:
        """
        Get the current default TTS engine id.

        Returns:
            str: Default engine id.

        Example:
            engine = robot.tts.get_default_engine()
        """
        ...

    def list_engines(self) -> list:
        """
        List loaded/available TTS engine ids.

        Returns:
            list: List[str] of engine ids.

        Example:
            engines = robot.tts.list_engines()
        """
        ...

    def say_text(self, text: str, engine: str | None = None, lang: str | None = None, voice: str | None = None, rate: float | None = None, pitch: float | None = None, volume: float | None = None, style: str | None = None) -> None:
        """
        Synthesize and play plain text using a selected TTS engine.

        Blocks until audio playback finishes and returns the result.
        For non-blocking use, call ``say_text_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to interrupt speech.

        Args:
            text (str): Text to synthesize.
            engine (str): Optional engine id to use (uses default if omitted).
            lang (str): Optional language code (e.g. 'en-US').
            voice (str): Optional voice id/name.
            rate (float): Optional speaking rate multiplier.
            pitch (float): Optional pitch adjustment.
            volume (float): Optional volume level.
            style (str): Optional speaking style (engine-dependent).

        Returns:
            bool: True on success.

        Notes:
            Visemes may be scheduled to the FaceNode if connected.

        Examples:
            # Blocking — uses default engine
            robot.tts.say_text('Hello world!')
            robot.tts.say_text('Slower speech', engine='acapela', rate=0.8, pitch=1.1)

            # Non-blocking — cancel after 2 seconds
            h = robot.tts.say_text_async('This is a very long sentence...')
            time.sleep(2)
            h.cancel()
        """
        ...

    def say_text_async(self, text: str, engine: str | None = None, lang: str | None = None, voice: str | None = None, rate: float | None = None, pitch: float | None = None, volume: float | None = None, style: str | None = None) -> ActionHandle:
        """
        Synthesize and play plain text using a selected TTS engine.

        Blocks until audio playback finishes and returns the result.
        For non-blocking use, call ``say_text_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to interrupt speech.

        Args:
            text (str): Text to synthesize.
            engine (str): Optional engine id to use (uses default if omitted).
            lang (str): Optional language code (e.g. 'en-US').
            voice (str): Optional voice id/name.
            rate (float): Optional speaking rate multiplier.
            pitch (float): Optional pitch adjustment.
            volume (float): Optional volume level.
            style (str): Optional speaking style (engine-dependent).

        Returns:
            bool: True on success.

        Notes:
            Visemes may be scheduled to the FaceNode if connected.

        Examples:
            # Blocking — uses default engine
            robot.tts.say_text('Hello world!')
            robot.tts.say_text('Slower speech', engine='acapela', rate=0.8, pitch=1.1)

            # Non-blocking — cancel after 2 seconds
            h = robot.tts.say_text_async('This is a very long sentence...')
            time.sleep(2)
            h.cancel()
        """
        ...

    def say_ssml(self, ssml: str, engine: str | None = None) -> None:
        """
        Synthesize and play SSML markup using a selected TTS engine.

        Blocks until audio playback finishes and returns the result.
        For non-blocking use, call ``say_ssml_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to interrupt speech.

        Args:
            ssml (str): SSML markup string.
            engine (str): Optional engine id to use (uses default if omitted).

        Returns:
            bool: True on success.

        Example:
            robot.tts.say_ssml('<speak>Hello!</speak>')
            robot.tts.say_ssml('<speak>Hello!</speak>', engine='azure')
        """
        ...

    def say_ssml_async(self, ssml: str, engine: str | None = None) -> ActionHandle:
        """
        Synthesize and play SSML markup using a selected TTS engine.

        Blocks until audio playback finishes and returns the result.
        For non-blocking use, call ``say_ssml_async()`` which returns an
        :class:`ActionHandle` — call ``.cancel()`` on it to interrupt speech.

        Args:
            ssml (str): SSML markup string.
            engine (str): Optional engine id to use (uses default if omitted).

        Returns:
            bool: True on success.

        Example:
            robot.tts.say_ssml('<speak>Hello!</speak>')
            robot.tts.say_ssml('<speak>Hello!</speak>', engine='azure')
        """
        ...

    def set_config(self, config: dict, engine: str | None = None) -> None:
        """
        Set engine-specific configuration parameters.

        Args:
            config (dict): Key/value config map.
            engine (str): Optional engine id (uses default if omitted).

        Returns:
            bool: True if engine accepted configuration.

        Example:
            robot.tts.set_config(config={'pitch': 1.0, 'rate': 0.8})
            robot.tts.set_config(engine='acapela', config={'pitch': 1.0, 'rate': 0.8})
        """
        ...

    def get_config(self, engine: str | None = None) -> dict:
        """
        Get engine-specific configuration parameters.

        Args:
            engine (str): Optional engine id (uses default if omitted).

        Returns:
            dict: Current engine configuration map.

        Example:
            cfg = robot.tts.get_config()
            cfg = robot.tts.get_config(engine='acapela')
        """
        ...

    def get_languages(self, engine: str | None = None) -> list:
        """
        Get supported language codes for a TTS engine.

        Args:
            engine (str): Optional engine id (uses default if omitted).

        Returns:
            list: List[str] language codes.

        Example:
            langs = robot.tts.get_languages()
            langs = robot.tts.get_languages(engine='acapela')
        """
        ...

    def get_voices(self, engine: str | None = None) -> list:
        """
        Get supported voices for a TTS engine.

        Args:
            engine (str): Optional engine id (uses default if omitted).

        Returns:
            list: List[dict] voice info dicts (id, lang, gender, display_name, ...).

        Example:
            voices = robot.tts.get_voices()
            voices = robot.tts.get_voices(engine='acapela')
            for v in voices:
                print(v['display_name'], v['lang'])
        """
        ...

    def supports_ssml(self, engine: str | None = None) -> bool:
        """
        Check whether a TTS engine supports SSML.

        Args:
            engine (str): Optional engine id (uses default if omitted).

        Returns:
            bool: True if SSML is supported.

        Example:
            if robot.tts.supports_ssml():
                robot.tts.say_ssml('<speak>Hello!</speak>')
            if robot.tts.supports_ssml(engine='azure'):
                robot.tts.say_ssml('<speak>Hello!</speak>', engine='azure')
        """
        ...

