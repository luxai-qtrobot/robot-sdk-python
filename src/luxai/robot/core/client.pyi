from __future__ import annotations

from typing import Any, Dict, TypeVar, Callable
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

    # --- AUTO-GENERATED ROBOT NAMESPACES ---

    @property
    def audio(self) -> AudioAPI:
        """Namespace view for audio APIs."""
        ...

    @property
    def emotion(self) -> EmotionAPI:
        """Namespace view for emotion APIs."""
        ...

    @property
    def gesture(self) -> GestureAPI:
        """Namespace view for gesture APIs."""
        ...

    @property
    def microphone(self) -> MicrophoneAPI:
        """Namespace view for microphone APIs."""
        ...

    @property
    def motors(self) -> MotorsAPI:
        """Namespace view for motors APIs."""
        ...

    @property
    def speaker(self) -> SpeakerAPI:
        """Namespace view for speaker APIs."""
        ...

    @property
    def speech(self) -> SpeechAPI:
        """Namespace view for speech APIs."""
        ...



class AudioAPI:
    """Namespace for audio RPC/stream APIs."""

    def play(self, filename: str, filepath: str, blocking: bool = True) -> ActionHandle:
        """Play an audio file on the robot speakers. (API: audio.play)"""
        ...

    def stop(self, blocking: bool = True) -> ActionHandle:
        """Stop any audio currently playing. (API: audio.stop)"""
        ...

    def talk(self, filename: str, filepath: str, blocking: bool = True) -> ActionHandle:
        """Trigger a higher-level audio-based talking behavior. (API: audio.talk)"""
        ...


class EmotionAPI:
    """Namespace for emotion RPC/stream APIs."""

    def look(self, eye_l: list, eye_r: list, duration: float = ..., blocking: bool = True) -> ActionHandle:
        """Move the robot eyes to the given positions over a duration. (API: emotion.look)"""
        ...

    def show(self, name: str, blocking: bool = True) -> ActionHandle:
        """Show a named facial emotion on the robot. (API: emotion.show)"""
        ...

    def stop(self, blocking: bool = True) -> ActionHandle:
        """Stop any active emotion or eye animation. (API: emotion.stop)"""
        ...


class GestureAPI:
    """Namespace for gesture RPC/stream APIs."""

    def get_all(self, blocking: bool = True) -> ActionHandle:
        """Return the list of available gesture names. (API: gesture.get_all)"""
        ...

    def play(self, name: str, speed: float = ..., blocking: bool = True) -> ActionHandle:
        """Play a stored gesture by name at the given speed. (API: gesture.play)"""
        ...

    def stop(self, blocking: bool = True) -> ActionHandle:
        """Stop any ongoing gesture playback or recording. (API: gesture.stop)"""
        ...

    def record(self, parts: list, idle_parts: bool = ..., wait: int = ..., timeout: int = ..., blocking: bool = True) -> ActionHandle:
        """Start recording a gesture for the given body parts. (API: gesture.record)"""
        ...

    def save(self, name: str, path: str, blocking: bool = True) -> ActionHandle:
        """Save the last recorded gesture under the given name and path. (API: gesture.save)"""
        ...


class MicrophoneStreamAPI:
    """Stream APIs for microphone namespace."""

    def open_channel0_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameFlac]:
        """Open a reader for stream topic '/qt_respeaker_app/channel0'. (API: microphone.channel0)"""
        ...

    def on_channel0(self, callback: Callable[[AudioFrameFlac], None], queue_size: int | None = ...) -> StreamSubscription:
        """Attach a callback to stream topic '/qt_respeaker_app/channel0'. (API: microphone.channel0)"""
        ...


class MicrophoneAPI:
    """Namespace for microphone RPC/stream APIs."""

    def get_tuning(self, param: str, blocking: bool = True) -> ActionHandle:
        """Get a tuning parameter value from the microphone front-end. (API: microphone.get_tuning)"""
        ...

    def set_tuning(self, param: str, value: float, blocking: bool = True) -> ActionHandle:
        """Set a tuning parameter value on the microphone front-end. (API: microphone.set_tuning)"""
        ...

    @property
    def stream(self) -> MicrophoneStreamAPI:
        """Stream namespace for microphone APIs."""
        ...


class MotorsStreamAPI:
    """Stream APIs for motors namespace."""

    def open_joints_reader(self, queue_size: int | None = ...) -> TypedStreamReader[JointStateFrame]:
        """Open a reader for stream topic '/qt_robot/joints/state'. (API: motors.joints)"""
        ...

    def on_joints(self, callback: Callable[[JointStateFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """Attach a callback to stream topic '/qt_robot/joints/state'. (API: motors.joints)"""
        ...

    def open_state_reader(self, queue_size: int | None = ...) -> TypedStreamReader[MotorStateFrame]:
        """Open a reader for stream topic '/qt_robot/motors/states'. (API: motors.state)"""
        ...

    def on_state(self, callback: Callable[[MotorStateFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """Attach a callback to stream topic '/qt_robot/motors/states'. (API: motors.state)"""
        ...


class MotorsAPI:
    """Namespace for motors RPC/stream APIs."""

    def home(self, parts: list, blocking: bool = True) -> ActionHandle:
        """Move the specified motor groups to their home positions. (API: motors.home)"""
        ...

    def set_mode(self, parts: list, mode: int, blocking: bool = True) -> ActionHandle:
        """Set control mode for the specified motors (ON, OFF, BRAKE). (API: motors.set_mode)"""
        ...

    def set_velocity(self, parts: list, velocity: int, blocking: bool = True) -> ActionHandle:
        """Set movement velocity for the specified motor groups. (API: motors.set_velocity)"""
        ...

    @property
    def stream(self) -> MotorsStreamAPI:
        """Stream namespace for motors APIs."""
        ...


class SpeakerAPI:
    """Namespace for speaker RPC/stream APIs."""

    def set_volume(self, volume: int, blocking: bool = True) -> ActionHandle:
        """Set the master speaker output volume (0-100). (API: speaker.set_volume)"""
        ...


class SpeechAPI:
    """Namespace for speech RPC/stream APIs."""

    def say(self, message: str, blocking: bool = True) -> ActionHandle:
        """Say a text using TTS. (API: speech.say)"""
        ...

    def talk(self, message: str, blocking: bool = True) -> ActionHandle:
        """Trigger a higher-level talking behavior with the given text. (API: speech.talk)"""
        ...

    def stop(self, blocking: bool = True) -> ActionHandle:
        """Stop any ongoing speech or talk behavior. (API: speech.stop)"""
        ...

    def config(self, language: str | None = None, pitch: int = ..., speed: int = ..., blocking: bool = True) -> ActionHandle:
        """Configure TTS parameters (language, pitch, speed). (API: speech.config)"""
        ...

