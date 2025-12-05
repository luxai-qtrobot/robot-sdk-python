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
        """Play an audio file through the robot's speakers.

Example:
    robot.audio.play(filename="hello.wav", filepath="/data/sounds")

Args:
    filename (str): Name of the audio file.
    filepath (str): Directory or full path where the file is located.
    blocking (bool): If True, wait until playback completes.

Returns:
    ActionHandle: Handle for the playback action.
 (API: audio.play)"""
        ...

    def stop(self, blocking: bool = True) -> ActionHandle:
        """Stop any audio currently playing on the robot.

Example:
    handle = robot.audio.play("music.wav", "/data/sounds", blocking=False)
    # later...
    robot.audio.stop()

Returns:
    None
 (API: audio.stop)"""
        ...

    def talk(self, filename: str, filepath: str, blocking: bool = True) -> ActionHandle:
        """Trigger a higher-level behavior that plays an audio file as part of a
scripted behavior (e.g., pre-recorded prompts).

Example:
    robot.audio.talk(filename="prompt.wav", filepath="/data/prompts")

Args:
    filename (str): Audio file for the behavior.
    filepath (str): Directory or full path to the file.
    blocking (bool): If True, wait until the behavior finishes.

Returns:
    ActionHandle: Handle for the behavior action.
 (API: audio.talk)"""
        ...


class EmotionAPI:
    """Namespace for emotion RPC/stream APIs."""

    def look(self, eye_l: list, eye_r: list, duration: float = ..., blocking: bool = True) -> ActionHandle:
        """Move the robot's eyes to the specified positions over the given duration.

The eye_l and eye_r arguments are lists of servo target values (int or float)
for the left and right eye motors.

Example (simple eye movement):
    robot.emotion.look(
        eye_l=[10, 20],
        eye_r=[10, 20],
        duration=0.5,
    )

Args:
    eye_l (List[int | float]): Left eye servo positions.
    eye_r (List[int | float]): Right eye servo positions.
    duration (float): Duration of the movement in seconds.

Returns:
    ActionHandle: Handle for the eye movement action.
 (API: emotion.look)"""
        ...

    def show(self, name: str, blocking: bool = True) -> ActionHandle:
        """Display a named facial emotion on the robot (e.g. 'happy', 'sad').

Example:
    robot.emotion.show("happy")

Args:
    name (str): Emotion identifier (implementation-specific list).

Returns:
    ActionHandle: Handle representing the emotion display action.
 (API: emotion.show)"""
        ...

    def stop(self, blocking: bool = True) -> ActionHandle:
        """Stop any active facial expression or eye animation.

Typical usage:
    robot.emotion.show("surprised")
    # later...
    robot.emotion.stop()

Returns:
    None
 (API: emotion.stop)"""
        ...


class GestureAPI:
    """Namespace for gesture RPC/stream APIs."""

    def get_all(self, blocking: bool = True) -> ActionHandle:
        """Return a list of all gesture names stored on the robot.

Example:
    names = robot.gesture.get_all()
    for name in names:
        print("Gesture:", name)

Returns:
    List[str]: Names of available gestures.
 (API: gesture.get_all)"""
        ...

    def play(self, name: str, speed: float = ..., blocking: bool = True) -> ActionHandle:
        """Play a stored gesture animation at the given speed.

Example (play at normal speed):
    robot.gesture.play("QT/bye")

Example (play slower):
    robot.gesture.play("QT/bye", speed=0.5)

Args:
    name (str): Gesture name.
    speed (float): Playback speed multiplier (1.0 = normal).
    blocking (bool): If True, wait until completion.

Returns:
    ActionHandle: Handle for the gesture playback.

Notes:
    - A new gesture.play() call will typically interrupt an ongoing one.
 (API: gesture.play)"""
        ...

    def stop(self, blocking: bool = True) -> ActionHandle:
        """Stop any active gesture playback or gesture recording.

Example:
    robot.gesture.play("QT/bye", blocking=False)
    # later...
    robot.gesture.stop()

Returns:
    None
 (API: gesture.stop)"""
        ...

    def record(self, parts: list, idle_parts: bool = ..., wait: int = ..., timeout: int = ..., blocking: bool = True) -> ActionHandle:
        """Start recording a gesture for the specified body parts.

Recording continues until gesture.stop() is called or a timeout is reached.

Example:
    # Record a gesture on the right arm for up to 10 seconds
    handle = robot.gesture.record(parts=["right_arm"], timeout=10)
    # Move the arm manually...
    handle.wait()  # or robot.gesture.stop() to end early

Args:
    parts (List[str]): Body parts to record, e.g. ['left_arm'].
    idle_parts (bool): If True, keep non-recorded parts idle.
    wait (int): Delay in seconds before recording starts.
    timeout (int): Maximum recording duration in seconds (0 = no limit).

Returns:
    ActionHandle: Handle representing the recording action.
 (API: gesture.record)"""
        ...

    def save(self, name: str, path: str, blocking: bool = True) -> ActionHandle:
        """Save the last recorded gesture under a specified name and path.

Example:
    robot.gesture.save(name="QT/bye_custom", path="/data/gestures")

Args:
    name (str): Gesture name.
    path (str): Directory or file path to store the gesture.

Returns:
    None
 (API: gesture.save)"""
        ...


class MicrophoneStreamAPI:
    """Stream APIs for microphone namespace."""

    def open_activity_reader(self, queue_size: int | None = ...) -> TypedStreamReader[BoolFrame]:
        """Open a reader for stream topic '/qt_respeaker_app/is_speaking'. (API: microphone.activity)"""
        ...

    def on_activity(self, callback: Callable[[BoolFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """Attach a callback to stream topic '/qt_respeaker_app/is_speaking'. (API: microphone.activity)"""
        ...

    def open_direction_reader(self, queue_size: int | None = ...) -> TypedStreamReader[IntFrame]:
        """Open a reader for stream topic '/qt_respeaker_app/sound_direction'. (API: microphone.direction)"""
        ...

    def on_direction(self, callback: Callable[[IntFrame], None], queue_size: int | None = ...) -> StreamSubscription:
        """Attach a callback to stream topic '/qt_respeaker_app/sound_direction'. (API: microphone.direction)"""
        ...

    def open_channel0_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameFlac]:
        """Open a reader for stream topic '/qt_respeaker_app/channel0'. (API: microphone.channel0)"""
        ...

    def on_channel0(self, callback: Callable[[AudioFrameFlac], None], queue_size: int | None = ...) -> StreamSubscription:
        """Attach a callback to stream topic '/qt_respeaker_app/channel0'. (API: microphone.channel0)"""
        ...

    def open_channel1_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameFlac]:
        """Open a reader for stream topic '/qt_respeaker_app/channel1'. (API: microphone.channel1)"""
        ...

    def on_channel1(self, callback: Callable[[AudioFrameFlac], None], queue_size: int | None = ...) -> StreamSubscription:
        """Attach a callback to stream topic '/qt_respeaker_app/channel1'. (API: microphone.channel1)"""
        ...

    def open_channel2_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameFlac]:
        """Open a reader for stream topic '/qt_respeaker_app/channel'. (API: microphone.channel2)"""
        ...

    def on_channel2(self, callback: Callable[[AudioFrameFlac], None], queue_size: int | None = ...) -> StreamSubscription:
        """Attach a callback to stream topic '/qt_respeaker_app/channel'. (API: microphone.channel2)"""
        ...

    def open_channel3_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameFlac]:
        """Open a reader for stream topic '/qt_respeaker_app/channel3'. (API: microphone.channel3)"""
        ...

    def on_channel3(self, callback: Callable[[AudioFrameFlac], None], queue_size: int | None = ...) -> StreamSubscription:
        """Attach a callback to stream topic '/qt_respeaker_app/channel3'. (API: microphone.channel3)"""
        ...

    def open_channel4_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameFlac]:
        """Open a reader for stream topic '/qt_respeaker_app/channel4'. (API: microphone.channel4)"""
        ...

    def on_channel4(self, callback: Callable[[AudioFrameFlac], None], queue_size: int | None = ...) -> StreamSubscription:
        """Attach a callback to stream topic '/qt_respeaker_app/channel4'. (API: microphone.channel4)"""
        ...

    def open_external1_reader(self, queue_size: int | None = ...) -> TypedStreamReader[AudioFrameFlac]:
        """Open a reader for stream topic '/qt_respeaker_app/external1'. (API: microphone.external1)"""
        ...

    def on_external1(self, callback: Callable[[AudioFrameFlac], None], queue_size: int | None = ...) -> StreamSubscription:
        """Attach a callback to stream topic '/qt_respeaker_app/external1'. (API: microphone.external1)"""
        ...

    def open_led_writer(self, queue_size: int | None = ...) -> TypedStreamWriter[LedColorFrame]:
        """Open a writer for stream topic '/qt_respeaker_app/status_led'. (API: microphone.led)"""
        ...


class MicrophoneAPI:
    """Namespace for microphone RPC/stream APIs."""

    def get_tuning(self, param: str, blocking: bool = True) -> ActionHandle:
        """Get a tuning parameter value from the microphone front-end.

Example:
    gain = robot.microphone.get_tuning("gain")
    print("Current gain:", gain)

Args:
    param (str): Parameter name, e.g. 'gain', 'noise_suppression'.

Returns:
    float: Current parameter value.
 (API: microphone.get_tuning)"""
        ...

    def set_tuning(self, param: str, value: float, blocking: bool = True) -> ActionHandle:
        """Set a tuning parameter value on the microphone front-end.

Example:
    robot.microphone.set_tuning("gain", 0.8)

Args:
    param (str): Parameter name.
    value (float): New parameter value.

Returns:
    None
 (API: microphone.set_tuning)"""
        ...

    @property
    def stream(self) -> MicrophoneStreamAPI:
        """Stream namespace for microphone APIs."""
        ...


class MotorsStreamAPI:
    """Stream APIs for motors namespace."""

    def open_joints_writer(self, queue_size: int | None = ...) -> TypedStreamWriter[JointCommandFrame]:
        """Open a writer for stream topic '/qt_robot/joints/command'. (API: motors.joints)"""
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
        """Move one or more motor groups to their home (reference) positions.

Example:
    # Home the head motors
    robot.motors.home(["head"])

Args:
    parts (List[str]): Motor groups to home, e.g. ['head', 'right_arm'].
    blocking (bool): If True, wait until homing completes.

Returns:
    ActionHandle: Handle for the homing action.
 (API: motors.home)"""
        ...

    def set_mode(self, parts: list, mode: int, blocking: bool = True) -> ActionHandle:
        """Set the control mode for the given motor groups.

Typical modes are:
    0 = ON (torque enabled)
    1 = OFF (torque disabled)
    2 = BRAKE

Example:
    # Enable torque on both arms
    robot.motors.set_mode(["left_arm", "right_arm"], mode=0)

Args:
    parts (List[str]): Motor groups to configure.
    mode (int): Control mode constant (implementation-specific mapping).

Returns:
    None
 (API: motors.set_mode)"""
        ...

    def set_velocity(self, parts: list, velocity: int, blocking: bool = True) -> ActionHandle:
        """Set the default movement velocity for one or more motor groups.
This velocity is typically used as a scaling factor for future motion.

Example:
    # Slow movements on the head
    robot.motors.set_velocity(["head"], velocity=50)

Args:
    parts (List[str]): Motor groups to affect.
    velocity (int): Velocity scalar (e.g. 0–255, implementation-specific).

Returns:
    None
 (API: motors.set_velocity)"""
        ...

    @property
    def stream(self) -> MotorsStreamAPI:
        """Stream namespace for motors APIs."""
        ...


class SpeakerAPI:
    """Namespace for speaker RPC/stream APIs."""

    def set_volume(self, volume: int, blocking: bool = True) -> ActionHandle:
        """Set the master speaker output volume (0–100).
This affects both speech and audio playback.

Example:
    robot.speaker.set_volume(80)

Args:
    volume (int): Volume percentage (0 = mute, 100 = max).

Returns:
    None
 (API: speaker.set_volume)"""
        ...


class SpeechAPI:
    """Namespace for speech RPC/stream APIs."""

    def say(self, message: str, blocking: bool = True) -> ActionHandle:
        """Speak the given text using the robot's Text-to-Speech engine.

This RPC can run in blocking or non-blocking mode. In the default case
(blocking=True), the call waits until the speech action finishes and
returns a completed ActionHandle. With blocking=False, the method
returns immediately with a running ActionHandle that you can manage.

Blocking example:
    # Wait until speech finishes, then continue
    robot.speech.say("Hello!")

Non-blocking example:
    handle = robot.speech.say("Hello!", blocking=False)
    # do other work...
    handle.wait()            # or handle.result(), handle.cancel()

Args:
    message (str): Text to synthesize.
    blocking (bool): If True, wait for completion before returning.

Returns:
    ActionHandle: Handle representing the speech action.

Notes:
    - Speech configuration (language, pitch, speed) is controlled via
      speech.config().
    - A new speech.say() or speech.talk() call will typically interrupt
      any ongoing speech.
 (API: speech.say)"""
        ...

    def talk(self, message: str, blocking: bool = True) -> ActionHandle:
        """Trigger a behavior-level speaking action using the given text.
Compared to speech.say(), this may involve additional behavior logic
such as coordinated gestures or timing.

Blocking example:
    robot.speech.talk("Welcome to the session.")

Non-blocking example:
    handle = robot.speech.talk("Welcome!", blocking=False)
    # do other work...
    if not handle.done():
        handle.cancel()

Args:
    message (str): Text for the high-level talk behavior.
    blocking (bool): If True, wait for completion before returning.

Returns:
    ActionHandle: Handle representing the behavior-level speech action.
 (API: speech.talk)"""
        ...

    def stop(self, blocking: bool = True) -> ActionHandle:
        """Request cancellation of any ongoing speech or talk action.

Use this when you want to interrupt speech.say() or speech.talk()
before it finishes.

Example:
    handle = robot.speech.say("This is a long sentence...", blocking=False)
    # ... decide to interrupt
    robot.speech.stop()
    # handle.result() will then raise ActionCancelledError

Returns:
    None
 (API: speech.stop)"""
        ...

    def config(self, language: str | None = None, pitch: int = ..., speed: int = ..., blocking: bool = True) -> ActionHandle:
        """Configure the TTS engine used by speech.say() and speech.talk().

Any parameter set to None leaves the existing value unchanged.

Example:
    # Switch to US English and slightly faster speech
    robot.speech.config(language="en-US", pitch=100, speed=120)

Args:
    language (str | None): Language code, e.g. 'en-US', or None to keep current.
    pitch (int): Pitch level (backend-specific range).
    speed (int): Speaking speed (backend-specific range).

Returns:
    None
 (API: speech.config)"""
        ...

