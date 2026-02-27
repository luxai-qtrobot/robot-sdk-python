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
        Recognized speech segments from Azure ASR.
        """
        ...

    def on_azure_speech(self, callback: Callable[[DictFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Recognized speech segments from Azure ASR.
        """
        ...

    def open_azure_event_reader(self, queue_size: int | None = ...) -> TypedStreamReader[StringFrame]:
        """
        Speech recognition events from Azure ASR.
        """
        ...

    def on_azure_event(self, callback: Callable[[StringFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Speech recognition events from Azure ASR.
        """
        ...


class AsrAPI:
    """Namespace for asr RPC/stream APIs."""

    def configure_azure(self, subscription: str, region: str, languages: List = ..., silence_timeout: float = ..., use_vad: bool = ..., continuous_mode: bool = ..., blocking: bool = True) -> ActionHandle:
        """
        configure Azure ASR
        """
        ...

    def recognize_azure(self, blocking: bool = True) -> ActionHandle:
        """
        Perform one-shot recognition with Azure ASR.
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
        Camera color image streaming
        """
        ...

    def on_color(self, callback: Callable[[ImageFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Camera color image streaming
        """
        ...

    def open_depth_reader(self, queue_size: int | None = ...) -> TypedStreamReader[ImageFrameRaw]:
        """
        Camera depth image streaming
        """
        ...

    def on_depth(self, callback: Callable[[ImageFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Camera depth image streaming
        """
        ...

    def open_depth_aligned_reader(self, queue_size: int | None = ...) -> TypedStreamReader[ImageFrameRaw]:
        """
        Camera aligned depth image streaming
        """
        ...

    def on_depth_aligned(self, callback: Callable[[ImageFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Camera aligned depth image streaming
        """
        ...

    def open_depth_color_reader(self, queue_size: int | None = ...) -> TypedStreamReader[ImageFrameRaw]:
        """
        Camera colorized depth image streaming
        """
        ...

    def on_depth_color(self, callback: Callable[[ImageFrameRaw], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Camera colorized depth image streaming
        """
        ...

    def open_gyro_reader(self, queue_size: int | None = ...) -> TypedStreamReader[ListFrame]:
        """
        Camera gyro streaming
        """
        ...

    def on_gyro(self, callback: Callable[[ListFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Camera gyro streaming
        """
        ...

    def open_acceleration_reader(self, queue_size: int | None = ...) -> TypedStreamReader[ListFrame]:
        """
        Camera acceleration streaming
        """
        ...

    def on_acceleration(self, callback: Callable[[ListFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Camera acceleration streaming
        """
        ...


class CameraAPI:
    """Namespace for camera RPC/stream APIs."""

    def get_color_intrinsics(self, blocking: bool = True) -> ActionHandle:
        """
        Get Camera color intrinsics parameters.
        """
        ...

    def get_depth_intrinsics(self, blocking: bool = True) -> ActionHandle:
        """
        Get Camera depth intrinsics parameters.
        """
        ...

    def get_depth_scale(self, blocking: bool = True) -> ActionHandle:
        """
        Get Camera depth scale value.
        """
        ...

    @property
    def stream(self) -> CameraStreamAPI:
        """Stream namespace for camera APIs."""
        ...


class FaceAPI:
    """Namespace for face RPC/stream APIs."""

    def look(self, l_eye: list, r_eye: list, duration: float = ..., blocking: bool = True) -> ActionHandle:
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
        """
        ...

    def show_emotion(self, emotion: str, speed: float | None = None, blocking: bool = True) -> ActionHandle:
        """
        Play an emotion video on the face background lane.

        Emotion resolves to an .avi file (emotion + '.avi' if not provided).
        Use cancel_service_name to stop the emotion playback.

        Args:
            emotion (str): Emotion name or relative path (with/without .avi).
            speed (float): Optional playback speed factor.

        Returns:
            bool: True if playback started, False otherwise.
        """
        ...

    def list_emotions(self, blocking: bool = True) -> ActionHandle:
        """
        List available emotion video files under the emotions directory.

        Scans recursively and returns relative paths for .avi/.AVI files.

        Returns:
            list: List[str] of emotion file paths.
        """
        ...


class GestureStreamAPI:
    """Stream APIs for gesture namespace."""

    def open_progress_reader(self, queue_size: int | None = ...) -> TypedStreamReader[DictFrame]:
        """
        Outbound stream of gesture playback progress.

        Publishes a DictFrame with fields:
          percentage (float), time_us (int)
        """
        ...

    def on_progress(self, callback: Callable[[DictFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of gesture playback progress.

        Publishes a DictFrame with fields:
          percentage (float), time_us (int)
        """
        ...


class GestureAPI:
    """Namespace for gesture RPC/stream APIs."""

    def record(self, motors: list, release_motors: bool = ..., delay_start_ms: int = ..., timeout_ms: int = ..., refine_keyframe: bool = ..., keyframe_pos_eps: float = ..., keyframe_max_gap_us: int = ..., blocking: bool = True) -> ActionHandle:
        """
        Start recording a gesture trajectory for selected motors.

        Records time-stamped joint positions and returns a trajectory dict.
        Use cancel_service_name to stop recording early.

        Args:
            motors (list): List[str] motor names (order preserved).
            release_motors (bool): If True, torque is disabled during recording.
            delay_start_ms (int): Optional delay before recording starts.
            timeout_ms (int): Optional max duration (ms).
            refine_keyframe (bool): If True, compress to keyframes.
            keyframe_pos_eps (float): Keyframe compression epsilon (deg).
            keyframe_max_gap_us (int): Max allowed gap for compression (us).

        Returns:
            dict: Trajectory dict with 'meta' and 'points'.
        """
        ...

    def stop_record(self, blocking: bool = True) -> ActionHandle:
        """
        Stop recording a gesture trajectory.

        Args:
            None

        Returns:
            bool: True if recording was stopped, False if no recording in progress.
        """
        ...

    def store_record(self, gesture: str, blocking: bool = True) -> ActionHandle:
        """
        Store the last recorded gesture trajectory to an XML file.

        Args:
            gesture (str): Gesture name/path (saved as <gesture>.xml).

        Returns:
            bool: True if saved successfully.
        """
        ...

    def play(self, keyframes: dict, resample: bool = ..., rate_hz: float = ..., speed_factor: float = ..., blocking: bool = True) -> ActionHandle:
        """
        Play a gesture trajectory (keyframes dict).

        Use cancel_service_name to stop playback.

        Args:
            keyframes (dict): Trajectory dict.
            resample (bool): If True, resample for smooth playback.
            rate_hz (float): Resample rate.
            speed_factor (float): Playback speed multiplier.

        Returns:
            bool: True if playback ran (or started) successfully.

        Notes:
            Progress is published on the gesture.progress stream.
        """
        ...

    def play_file(self, gesture: str, speed_factor: float = ..., blocking: bool = True) -> ActionHandle:
        """
        Load a gesture XML file and play it.

        Use cancel_service_name to stop playback.

        Args:
            gesture (str): Gesture name/path (with/without .xml).
            speed_factor (float): Playback speed multiplier.

        Returns:
            bool: True if loaded and played successfully.
        """
        ...

    def list_files(self, blocking: bool = True) -> ActionHandle:
        """
        List available gesture XML files under the configured gesture directory.

        Returns:
            list: List[str] of gesture file paths.
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
            Use media.cancel_fg_audio_stream / pause / resume to control the pipeline.
        """
        ...

    def open_bg_audio_stream_writer(self, queue_size: int | None = ...) -> TypedStreamWriter[AudioFrameRaw]:
        """
        Inbound audio stream to the media BG audio lane.

        Send AudioFrameRaw frames to this topic to play streamed background audio.

        Notes:
            Use media.cancel_bg_audio_stream / pause / resume to control the pipeline.
        """
        ...

    def open_fg_video_stream_writer(self, queue_size: int | None = ...) -> TypedStreamWriter[ImageFrameRaw]:
        """
        Inbound video stream to the media FG video lane.

        Send ImageFrameRaw frames to this topic to render streamed foreground video.
        """
        ...

    def open_bg_video_stream_writer(self, queue_size: int | None = ...) -> TypedStreamWriter[ImageFrameRaw]:
        """
        Inbound video stream to the media BG video lane.

        Send ImageFrameRaw frames to this topic to render streamed background video.
        """
        ...


class MediaAPI:
    """Namespace for media RPC/stream APIs."""

    def play_fg_audio_file(self, uri: str, blocking: bool = True) -> ActionHandle:
        """
        Play an audio file on the foreground (FG) audio lane.

        This plays the given URI via the media audio engine FG file player.
        Use the cancel RPC (cancel_service_name) to stop playback.

        Args:
            uri (str): Audio file URI/path supported by the engine.

        Returns:
            bool: True if playback started successfully, False otherwise.
        """
        ...

    def pause_fg_audio_file(self, blocking: bool = True) -> ActionHandle:
        """
        Pause current foreground (FG) audio file playback.

        Returns:
            None
        """
        ...

    def resume_fg_audio_file(self, blocking: bool = True) -> ActionHandle:
        """
        Resume foreground (FG) audio file playback after pause.

        Returns:
            None
        """
        ...

    def cancel_fg_audio_stream(self, blocking: bool = True) -> ActionHandle:
        """
        Cancel / stop the current foreground (FG) audio stream pipeline.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def pause_fg_audio_stream(self, blocking: bool = True) -> ActionHandle:
        """
        Pause foreground (FG) audio stream processing.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def resume_fg_audio_stream(self, blocking: bool = True) -> ActionHandle:
        """
        Resume foreground (FG) audio stream processing.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def set_fg_audio_volume(self, value: float, blocking: bool = True) -> ActionHandle:
        """
        Set foreground (FG) audio lane volume.

        Args:
            value (float): Volume in range [0.0, 1.0].

        Returns:
            None
        """
        ...

    def get_fg_audio_volume(self, blocking: bool = True) -> ActionHandle:
        """
        Get foreground (FG) audio lane volume.

        Returns:
            float: Volume in range [0.0, 1.0].
        """
        ...

    def play_bg_audio_file(self, uri: str, blocking: bool = True) -> ActionHandle:
        """
        Play an audio file on the background (BG) audio lane.

        Args:
            uri (str): Audio file URI/path supported by the engine.

        Returns:
            bool: True if playback started successfully, False otherwise.
        """
        ...

    def pause_bg_audio_file(self, blocking: bool = True) -> ActionHandle:
        """
        Pause current background (BG) audio file playback.

        Returns:
            None
        """
        ...

    def resume_bg_audio_file(self, blocking: bool = True) -> ActionHandle:
        """
        Resume background (BG) audio file playback after pause.

        Returns:
            None
        """
        ...

    def cancel_bg_audio_stream(self, blocking: bool = True) -> ActionHandle:
        """
        Cancel / stop the current background (BG) audio stream pipeline.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def pause_bg_audio_stream(self, blocking: bool = True) -> ActionHandle:
        """
        Pause background (BG) audio stream processing.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def resume_bg_audio_stream(self, blocking: bool = True) -> ActionHandle:
        """
        Resume background (BG) audio stream processing.

        This is for streamed audio frames (not file playback).

        Returns:
            None
        """
        ...

    def set_bg_audio_volume(self, value: float, blocking: bool = True) -> ActionHandle:
        """
        Set background (BG) audio lane volume.

        Args:
            value (float): Volume in range [0.0, 1.0].

        Returns:
            None
        """
        ...

    def get_bg_audio_volume(self, blocking: bool = True) -> ActionHandle:
        """
        Get background (BG) audio lane volume.

        Returns:
            float: Volume in range [0.0, 1.0].
        """
        ...

    def play_fg_video_file(self, uri: str, speed: float = ..., with_audio: bool = ..., blocking: bool = True) -> ActionHandle:
        """
        Play a video file on the foreground (FG) video lane.

        Args:
            uri (str): Video file URI/path supported by the engine.
            speed (float): Playback speed factor (default 1.0).
            with_audio (bool): If True, play embedded audio track (default False).

        Returns:
            bool: True if playback started successfully, False otherwise.
        """
        ...

    def pause_fg_video_file(self, blocking: bool = True) -> ActionHandle:
        """
        Pause current foreground (FG) video file playback.

        Returns:
            None
        """
        ...

    def resume_fg_video_file(self, blocking: bool = True) -> ActionHandle:
        """
        Resume foreground (FG) video file playback after pause.

        Returns:
            None
        """
        ...

    def cancel_fg_video_stream(self, blocking: bool = True) -> ActionHandle:
        """
        Cancel / stop the current foreground (FG) video stream pipeline.

        This is for streamed video frames (not file playback).

        Returns:
            None
        """
        ...

    def pause_fg_video_stream(self, blocking: bool = True) -> ActionHandle:
        """
        Pause foreground (FG) video stream processing.

        This is for streamed video frames (not file playback).

        Returns:
            None
        """
        ...

    def resume_fg_video_stream(self, blocking: bool = True) -> ActionHandle:
        """
        Resume foreground (FG) video stream processing.

        This is for streamed video frames (not file playback).

        Returns:
            None
        """
        ...

    def set_fg_video_alpha(self, value: float, blocking: bool = True) -> ActionHandle:
        """
        Set foreground (FG) video alpha (transparency).

        Args:
            value (float): Alpha in range [0.0, 1.0].

        Returns:
            None
        """
        ...

    def play_bg_video_file(self, uri: str, speed: float = ..., with_audio: bool = ..., blocking: bool = True) -> ActionHandle:
        """
        Play a video file on the background (BG) video lane.

        Args:
            uri (str): Video file URI/path supported by the engine.
            speed (float): Playback speed factor (default 1.0).
            with_audio (bool): If True, play embedded audio track (default False).

        Returns:
            bool: True if playback started successfully, False otherwise.
        """
        ...

    def pause_bg_video_file(self, blocking: bool = True) -> ActionHandle:
        """
        Pause current background (BG) video file playback.

        Returns:
            None
        """
        ...

    def resume_bg_video_file(self, blocking: bool = True) -> ActionHandle:
        """
        Resume background (BG) video file playback after pause.

        Returns:
            None
        """
        ...

    def cancel_bg_video_stream(self, blocking: bool = True) -> ActionHandle:
        """
        Cancel / stop the current background (BG) video stream pipeline.

        This is for streamed video frames (not file playback).

        Returns:
            None
        """
        ...

    def pause_bg_video_stream(self, blocking: bool = True) -> ActionHandle:
        """
        Pause background (BG) video stream processing.

        This is for streamed video frames (not file playback).

        Returns:
            None
        """
        ...

    def resume_bg_video_stream(self, blocking: bool = True) -> ActionHandle:
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


class MotorStreamAPI:
    """Stream APIs for motor namespace."""

    def open_joints_state_reader(self, queue_size: int | None = ...) -> TypedStreamReader[JointStateFrame]:
        """
        Outbound stream of joint states.

        Frame payload is a DictFrame mapping motor_name -> state dict:
          {position, velocity, effort, voltage, temprature}

        Typical usage:
            sub = robot.motor.stream.on_joints_state(callback)
            reader = robot.motor.stream.open_joints_state_reader()
        """
        ...

    def on_joints_state(self, callback: Callable[[JointStateFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of joint states.

        Frame payload is a DictFrame mapping motor_name -> state dict:
          {position, velocity, effort, voltage, temprature}

        Typical usage:
            sub = robot.motor.stream.on_joints_state(callback)
            reader = robot.motor.stream.open_joints_state_reader()
        """
        ...

    def open_joints_error_reader(self, queue_size: int | None = ...) -> TypedStreamReader[DictFrame]:
        """
        Outbound stream of motor error flags (when present).

        Frame payload is a DictFrame mapping motor_name -> error flags:
          {overload_limit?, voltage_limit?, temperature_limit?, sensor_failure?}
        """
        ...

    def on_joints_error(self, callback: Callable[[DictFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """
        Outbound stream of motor error flags (when present).

        Frame payload is a DictFrame mapping motor_name -> error flags:
          {overload_limit?, voltage_limit?, temperature_limit?, sensor_failure?}
        """
        ...

    def open_joints_command_writer(self, queue_size: int | None = ...) -> TypedStreamWriter[JointCommandFrame]:
        """
        Inbound stream of joint commands.

        Send DictFrame mapping motor_name -> command dict:
          {'position': float, 'velocity': float(optional)}

        Typical usage:
            writer = robot.motor.stream.open_joints_command_writer()
            writer.write(DictFrame({...}))
        """
        ...


class MotorAPI:
    """Namespace for motor RPC/stream APIs."""

    def list(self, blocking: bool = True) -> ActionHandle:
        """
        List configured motors and their parameters.

        Returns:
            dict: {motor_name: {part, position_min, position_max, position_home,
                  velocity_max, calibration_offset, overload_threshold, ...}}
        """
        ...

    def set_calib(self, motor: str, offset: float, store: bool = ..., blocking: bool = True) -> ActionHandle:
        """
        Set calibration offset for a motor.

        Args:
            motor (str): Motor name.
            offset (float): Offset in degrees.
            store (bool): If True, persist to config (default False).

        Returns:
            bool: True on success.
        """
        ...

    def calib_all(self, blocking: bool = True) -> ActionHandle:
        """
        Run manual calibration procedure for all motors (writes offsets and stores them).

        Returns:
            bool: True on success.
        """
        ...

    def set_velocity(self, motor: str, velocity: int, blocking: bool = True) -> ActionHandle:
        """
        Set default velocity for a motor (deg/s).

        Args:
            motor (str): Motor name.
            velocity (int): Velocity value; clamped/validated against motor max.

        Returns:
            bool: True on success.
        """
        ...

    def on(self, motor: str, blocking: bool = True) -> ActionHandle:
        """
        Enable torque for a motor.

        Args:
            motor (str): Motor name.

        Returns:
            bool: True on success.
        """
        ...

    def off(self, motor: str, blocking: bool = True) -> ActionHandle:
        """
        Disable torque for a motor.

        Args:
            motor (str): Motor name.

        Returns:
            bool: True on success.
        """
        ...

    def on_all(self, blocking: bool = True) -> ActionHandle:
        """
        Enable torque for all motors.

        Returns:
            bool: True
        """
        ...

    def off_all(self, blocking: bool = True) -> ActionHandle:
        """
        Disable torque for all motors.

        Returns:
            bool: True
        """
        ...

    def home(self, motor: str, blocking: bool = True) -> ActionHandle:
        """
        Move a motor to its configured home position.

        Args:
            motor (str): Motor name.

        Returns:
            bool: True on success.
        """
        ...

    def home_all(self, blocking: bool = True) -> ActionHandle:
        """
        Move all motors to their configured home positions.

        Returns:
            bool: True
        """
        ...

    @property
    def stream(self) -> MotorStreamAPI:
        """Stream namespace for motor APIs."""
        ...


class SpeakerAPI:
    """Namespace for speaker RPC/stream APIs."""

    def set_volume(self, value: float, blocking: bool = True) -> ActionHandle:
        """
        Set the master speaker volume.

        Args:
            value (float): Volume in range [0.0, 1.0].

        Returns:
            bool: True if mixer control succeeded, False otherwise.
        """
        ...

    def get_volume(self, blocking: bool = True) -> ActionHandle:
        """
        Get the master speaker volume.

        Returns:
            float: Volume in range [0.0, 1.0].
        """
        ...

    def mute(self, blocking: bool = True) -> ActionHandle:
        """
        Mute the speaker output.

        Returns:
            bool: True if succeeded, False otherwise.
        """
        ...

    def unmute(self, blocking: bool = True) -> ActionHandle:
        """
        Unmute the speaker output.

        Returns:
            bool: True if succeeded, False otherwise.
        """
        ...


class TtsAPI:
    """Namespace for tts RPC/stream APIs."""

    def set_default_engine(self, engine: str, blocking: bool = True) -> ActionHandle:
        """
        Set the default TTS engine id.

        Args:
            engine (str): Engine id (e.g. 'acapela', 'azure', or custom).

        Returns:
            None
        """
        ...

    def get_default_engine(self, blocking: bool = True) -> ActionHandle:
        """
        Get the current default TTS engine id.

        Returns:
            str: Default engine id.
        """
        ...

    def list_engines(self, blocking: bool = True) -> ActionHandle:
        """
        List loaded/available TTS engine ids.

        Returns:
            list: List[str] of engine ids.
        """
        ...

    def say_text(self, engine: str, text: str, lang: str | None = None, voice: str | None = None, rate: float | None = None, pitch: float | None = None, volume: float | None = None, style: str | None = None, blocking: bool = True) -> ActionHandle:
        """
        Synthesize and play plain text using a selected TTS engine.

        This call blocks until playback finishes (current implementation).
        Use cancel_service_name to interrupt playback.

        Args:
            engine (str): Engine id to use.
            text (str): Text to synthesize.
            lang (str): Optional language code.
            voice (str): Optional voice id/name.
            rate (float): Optional speaking rate.
            pitch (float): Optional pitch.
            volume (float): Optional volume.
            style (str): Optional style (engine dependent).

        Returns:
            bool: True on success.

        Notes:
            Visemes may be scheduled to the FaceNode if connected.
        """
        ...

    def say_ssml(self, engine: str, ssml: str, blocking: bool = True) -> ActionHandle:
        """
        Synthesize and play SSML using a selected TTS engine.

        This call blocks until playback finishes (current implementation).
        Use cancel_service_name to interrupt playback.

        Args:
            engine (str): Engine id to use.
            ssml (str): SSML markup.

        Returns:
            bool: True on success.
        """
        ...

    def set_config(self, engine: str, config: dict, blocking: bool = True) -> ActionHandle:
        """
        Set engine-specific configuration parameters.

        Args:
            engine (str): Engine id.
            config (dict): Key/value config map.

        Returns:
            bool: True if engine accepted configuration.
        """
        ...

    def get_config(self, engine: str, blocking: bool = True) -> ActionHandle:
        """
        Get engine-specific configuration parameters.

        Args:
            engine (str): Engine id.

        Returns:
            dict: Current engine configuration map.
        """
        ...

    def get_languages(self, engine: str, blocking: bool = True) -> ActionHandle:
        """
        Get supported language codes for a TTS engine.

        Args:
            engine (str): Engine id.

        Returns:
            list: List[str] language codes.
        """
        ...

    def get_voices(self, engine: str, blocking: bool = True) -> ActionHandle:
        """
        Get supported voices for a TTS engine.

        Args:
            engine (str): Engine id.

        Returns:
            list: List[dict] voice info dicts (id, lang, gender, display_name, ...).
        """
        ...

    def supports_ssml(self, engine: str, blocking: bool = True) -> ActionHandle:
        """
        Check whether the selected TTS engine supports SSML.

        Args:
            engine (str): Engine id.

        Returns:
            bool: True if SSML is supported.
        """
        ...

