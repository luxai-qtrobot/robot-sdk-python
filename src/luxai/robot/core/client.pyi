from __future__ import annotations

from typing import Any
from luxai.robot.core.actions import ActionHandle


class AudioAPI:
    """Namespace for audio APIs."""

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
    """Namespace for emotion APIs."""

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
    """Namespace for gesture APIs."""

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


class MicrophoneAPI:
    """Namespace for microphone APIs."""

    def get_tuning(self, param: str, blocking: bool = True) -> ActionHandle:
        """Get a tuning parameter value from the microphone front-end. (API: microphone.get_tuning)"""
        ...

    def set_tuning(self, param: str, value: float, blocking: bool = True) -> ActionHandle:
        """Set a tuning parameter value on the microphone front-end. (API: microphone.set_tuning)"""
        ...


class MotorsAPI:
    """Namespace for motors APIs."""

    def home(self, parts: list, blocking: bool = True) -> ActionHandle:
        """Move the specified motor groups to their home positions. (API: motors.home)"""
        ...

    def set_mode(self, parts: list, mode: int, blocking: bool = True) -> ActionHandle:
        """Set control mode for the specified motors (ON, OFF, BRAKE). (API: motors.set_mode)"""
        ...

    def set_velocity(self, parts: list, velocity: int, blocking: bool = True) -> ActionHandle:
        """Set movement velocity for the specified motor groups. (API: motors.set_velocity)"""
        ...


class SpeakerAPI:
    """Namespace for speaker APIs."""

    def set_volume(self, volume: int, blocking: bool = True) -> ActionHandle:
        """Set the master speaker output volume (0-100). (API: speaker.set_volume)"""
        ...


class SpeechAPI:
    """Namespace for speech APIs."""

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


class Robot:
    """Type stub for Robot client (auto-generated from IDL)."""

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
