"""
tests/test_api_factory.py — Unit tests for the IDL → Robot method codegen.

Tests create_rpc_methods / create_stream_methods in isolation (no transport
needed), and verifies that attach_core_apis correctly populates a class with
the right methods and namespace properties.
"""
from __future__ import annotations

import inspect
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from luxai.robot.core.api_factory import (
    create_rpc_methods,
    create_stream_methods,
    attach_core_apis,
    _NamespaceView,
    _StreamNamespaceView,
    FRAME_TYPE_REGISTRY,
)
from luxai.robot.core.actions import ActionHandle


# ---------------------------------------------------------------------------
# Minimal fake Robot for calling generated methods
# ---------------------------------------------------------------------------

class FakeRobot:
    """Minimal stand-in for Robot, implementing only the two call helpers."""

    def __init__(self):
        self.sync_calls = []     # [(service_name, args)]
        self.async_calls = []    # [(service_name, args, cancel_service_name)]
        self.sync_return = "ok"  # value returned by _call_rpc_sync

    def _call_rpc_sync(self, service_name: str, args: Dict[str, Any], timeout=None):
        self.sync_calls.append((service_name, args))
        return self.sync_return

    def _start_action(self, service_name, args, *, cancel_service_name=None, timeout=None):
        self.async_calls.append((service_name, args, cancel_service_name))
        # Return a real ActionHandle backed by an instant-success rpc_call
        def instant_rpc(svc, a, timeout=None):
            return {"status": True, "response": "async_ok"}
        return ActionHandle(
            service_name=service_name,
            args=args,
            cancel_service_name=cancel_service_name,
            rpc_call=instant_rpc,
        )


# ---------------------------------------------------------------------------
# Minimal IDL specs used in isolation tests
# ---------------------------------------------------------------------------

SIMPLE_SPEC_NO_CANCEL = {
    "service_name": "/test/list",
    "cancel_service_name": None,
    "params": [],
    "response_type": list,
    "doc": "List things.",
}

SPEC_WITH_CANCEL = {
    "service_name": "/test/play",
    "cancel_service_name": "/test/stop",
    "params": [
        ("name", str),
        ("speed", float, 1.0),
    ],
    "response_type": bool,
    "doc": "Play something.",
}

SPEC_ASYNC_FORCED = {
    "service_name": "/test/query",
    "cancel_service_name": None,
    "params": [("text", str)],
    "response_type": dict,
    "async_variant": True,
    "doc": "Query with forced async.",
}

SPEC_ASYNC_SUPPRESSED = {
    "service_name": "/test/fire",
    "cancel_service_name": "/test/abort",
    "params": [],
    "response_type": type(None),
    "async_variant": False,
    "doc": "Fire and forget — no async despite cancel present.",
}

STREAM_OUT_SPEC = {
    "direction": "out",
    "topic": "/test/audio:o",
    "frame_type": "AudioFrameRaw",
    "delivery": "reliable",
    "queue_size": 10,
    "doc": "Audio output stream.",
}

STREAM_IN_SPEC = {
    "direction": "in",
    "topic": "/test/cmd:i",
    "frame_type": "JointCommandFrame",
    "delivery": "reliable",
    "queue_size": 5,
    "doc": "Command input stream.",
}


# ===========================================================================
# create_rpc_methods — method generation
# ===========================================================================

class TestCreateRpcMethods:

    def test_sync_method_always_generated(self):
        methods = create_rpc_methods("ns.list", SIMPLE_SPEC_NO_CANCEL)
        assert "ns_list" in methods

    def test_async_not_generated_when_cancel_absent(self):
        methods = create_rpc_methods("ns.list", SIMPLE_SPEC_NO_CANCEL)
        assert "ns_list_async" not in methods

    def test_async_generated_when_cancel_present(self):
        methods = create_rpc_methods("ns.play", SPEC_WITH_CANCEL)
        assert "ns_play" in methods
        assert "ns_play_async" in methods

    def test_async_variant_true_forces_async_without_cancel(self):
        methods = create_rpc_methods("ns.query", SPEC_ASYNC_FORCED)
        assert "ns_query_async" in methods

    def test_async_variant_false_suppresses_async_despite_cancel(self):
        methods = create_rpc_methods("ns.fire", SPEC_ASYNC_SUPPRESSED)
        assert "ns_fire" in methods
        assert "ns_fire_async" not in methods

    def test_method_names_use_underscore_separator(self):
        methods = create_rpc_methods("gesture.list_files", SIMPLE_SPEC_NO_CANCEL)
        assert "gesture_list_files" in methods

    def test_sync_method_has_correct_dunder_name(self):
        methods = create_rpc_methods("tts.say_text", SPEC_WITH_CANCEL)
        assert methods["tts_say_text"].__name__ == "tts_say_text"

    def test_async_method_has_correct_dunder_name(self):
        methods = create_rpc_methods("tts.say_text", SPEC_WITH_CANCEL)
        assert methods["tts_say_text_async"].__name__ == "tts_say_text_async"

    def test_method_doc_matches_spec(self):
        methods = create_rpc_methods("ns.play", SPEC_WITH_CANCEL)
        assert "Play something." in methods["ns_play"].__doc__
        assert "Play something." in methods["ns_play_async"].__doc__

    def test_sync_return_annotation_matches_response_type(self):
        methods = create_rpc_methods("ns.play", SPEC_WITH_CANCEL)
        sig = inspect.signature(methods["ns_play"])
        assert sig.return_annotation is bool

    def test_async_return_annotation_is_action_handle(self):
        methods = create_rpc_methods("ns.play", SPEC_WITH_CANCEL)
        sig = inspect.signature(methods["ns_play_async"])
        assert sig.return_annotation is ActionHandle

    def test_required_params_have_no_default(self):
        methods = create_rpc_methods("ns.play", SPEC_WITH_CANCEL)
        sig = inspect.signature(methods["ns_play"])
        # "name" param is required (no default)
        name_param = sig.parameters["name"]
        assert name_param.default is inspect.Parameter.empty

    def test_optional_params_have_correct_default(self):
        methods = create_rpc_methods("ns.play", SPEC_WITH_CANCEL)
        sig = inspect.signature(methods["ns_play"])
        speed_param = sig.parameters["speed"]
        assert speed_param.default == 1.0

    def test_spec_without_namespace_prefix(self):
        spec = {**SIMPLE_SPEC_NO_CANCEL, "service_name": "/top/level"}
        methods = create_rpc_methods("top_level", spec)
        assert "top_level" in methods


class TestRpcMethodBehaviour:
    """Tests that actually *call* the generated methods."""

    def test_sync_method_calls_call_rpc_sync(self):
        methods = create_rpc_methods("ns.list", SIMPLE_SPEC_NO_CANCEL)
        robot = FakeRobot()
        methods["ns_list"](robot)
        assert len(robot.sync_calls) == 1
        assert robot.sync_calls[0][0] == "/test/list"

    def test_sync_method_passes_args(self):
        methods = create_rpc_methods("ns.play", SPEC_WITH_CANCEL)
        robot = FakeRobot()
        methods["ns_play"](robot, "QT/bye")
        assert robot.sync_calls[0][1] == {"name": "QT/bye", "speed": 1.0}

    def test_sync_method_strips_none_params(self):
        spec = {
            "service_name": "/tts/say",
            "cancel_service_name": None,
            "params": [("engine", str), ("lang", str, None)],
            "response_type": type(None),
            "doc": "Say text.",
        }
        methods = create_rpc_methods("tts.say", spec)
        robot = FakeRobot()
        # lang not provided → defaults to None → should be stripped from args
        methods["tts_say"](robot, "acapela")
        assert "lang" not in robot.sync_calls[0][1]

    def test_sync_method_returns_value_from_call_rpc_sync(self):
        methods = create_rpc_methods("ns.list", SIMPLE_SPEC_NO_CANCEL)
        robot = FakeRobot()
        robot.sync_return = ["item1", "item2"]
        result = methods["ns_list"](robot)
        assert result == ["item1", "item2"]

    def test_async_method_calls_start_action(self):
        methods = create_rpc_methods("ns.play", SPEC_WITH_CANCEL)
        robot = FakeRobot()
        methods["ns_play_async"](robot, "QT/bye")
        assert len(robot.async_calls) == 1
        assert robot.async_calls[0][0] == "/test/play"
        assert robot.async_calls[0][2] == "/test/stop"

    def test_async_method_returns_action_handle(self):
        methods = create_rpc_methods("ns.play", SPEC_WITH_CANCEL)
        robot = FakeRobot()
        handle = methods["ns_play_async"](robot, "QT/bye")
        assert isinstance(handle, ActionHandle)


# ===========================================================================
# create_stream_methods — stream method generation
# ===========================================================================

class TestCreateStreamMethods:

    def test_outbound_stream_generates_reader_and_callback(self):
        methods = create_stream_methods("audio.int_ch0", STREAM_OUT_SPEC)
        assert "audio_stream_open_int_ch0_reader" in methods
        assert "audio_stream_on_int_ch0" in methods

    def test_outbound_stream_does_not_generate_writer(self):
        methods = create_stream_methods("audio.int_ch0", STREAM_OUT_SPEC)
        assert "audio_stream_open_int_ch0_writer" not in methods

    def test_inbound_stream_generates_writer(self):
        methods = create_stream_methods("motor.cmd", STREAM_IN_SPEC)
        assert "motor_stream_open_cmd_writer" in methods

    def test_inbound_stream_does_not_generate_reader(self):
        methods = create_stream_methods("motor.cmd", STREAM_IN_SPEC)
        assert "motor_stream_open_cmd_reader" not in methods
        assert "motor_stream_on_cmd" not in methods

    def test_reader_method_name(self):
        methods = create_stream_methods("audio.int_ch0", STREAM_OUT_SPEC)
        func = methods["audio_stream_open_int_ch0_reader"]
        assert func.__name__ == "audio_stream_open_int_ch0_reader"

    def test_callback_method_name(self):
        methods = create_stream_methods("audio.int_ch0", STREAM_OUT_SPEC)
        func = methods["audio_stream_on_int_ch0"]
        assert func.__name__ == "audio_stream_on_int_ch0"


# ===========================================================================
# attach_core_apis — full integration on a synthetic class
# ===========================================================================

class TestAttachCoreApis:

    def _make_test_class(self):
        """Return a fresh class to attach APIs to."""
        class TestRobot(FakeRobot):
            pass
        return TestRobot

    def _minimal_api_specs(self) -> dict:
        return {
            "rpc": {
                "tts.say": SPEC_WITH_CANCEL,
                "gesture.list_files": SIMPLE_SPEC_NO_CANCEL,
            },
            "stream": {
                "mic.audio_ch0": STREAM_OUT_SPEC,
                "motor.cmd": STREAM_IN_SPEC,
            },
        }

    def test_rpc_methods_attached_to_class(self):
        cls = self._make_test_class()
        attach_core_apis(cls, self._minimal_api_specs())
        assert hasattr(cls, "tts_say")
        assert hasattr(cls, "gesture_list_files")

    def test_async_methods_attached_when_cancel_present(self):
        cls = self._make_test_class()
        attach_core_apis(cls, self._minimal_api_specs())
        assert hasattr(cls, "tts_say_async")

    def test_no_async_method_when_cancel_absent(self):
        cls = self._make_test_class()
        attach_core_apis(cls, self._minimal_api_specs())
        assert not hasattr(cls, "gesture_list_files_async")

    def test_stream_reader_attached(self):
        cls = self._make_test_class()
        attach_core_apis(cls, self._minimal_api_specs())
        assert hasattr(cls, "mic_stream_open_audio_ch0_reader")

    def test_stream_writer_attached(self):
        cls = self._make_test_class()
        attach_core_apis(cls, self._minimal_api_specs())
        assert hasattr(cls, "motor_stream_open_cmd_writer")

    def test_namespace_properties_attached(self):
        cls = self._make_test_class()
        attach_core_apis(cls, self._minimal_api_specs())
        # tts, gesture, mic, motor namespaces should exist as properties
        for ns in ("tts", "gesture", "mic", "motor"):
            assert hasattr(cls, ns), f"namespace {ns!r} not attached"

    def test_namespace_property_returns_namespace_view(self):
        cls = self._make_test_class()
        attach_core_apis(cls, self._minimal_api_specs())
        robot = cls()
        assert isinstance(robot.tts, _NamespaceView)

    def test_namespace_view_resolves_to_robot_method(self):
        cls = self._make_test_class()
        attach_core_apis(cls, self._minimal_api_specs())
        robot = cls()
        # robot.tts.say resolves to robot.tts_say
        assert robot.tts.say == getattr(robot, "tts_say")

    def test_stream_namespace_view_resolves_to_robot_method(self):
        cls = self._make_test_class()
        attach_core_apis(cls, self._minimal_api_specs())
        robot = cls()
        # robot.mic.stream.open_audio_ch0_reader resolves to robot.mic_stream_open_audio_ch0_reader
        assert robot.mic.stream.open_audio_ch0_reader == getattr(
            robot, "mic_stream_open_audio_ch0_reader"
        )

    def test_async_resolves_through_namespace_view(self):
        cls = self._make_test_class()
        attach_core_apis(cls, self._minimal_api_specs())
        robot = cls()
        # robot.tts.say_async should resolve to robot.tts_say_async
        assert robot.tts.say_async == getattr(robot, "tts_say_async")


# ===========================================================================
# Verify the real Robot class already has all IDL-derived methods
# ===========================================================================

class TestRobotClassHasAllGeneratedMethods:
    """
    Smoke-tests that attach_core_apis(Robot, QTROBOT_APIS) ran correctly at
    import time — without instantiating a Robot (no transport needed).
    """

    def test_robot_has_tts_say_text(self):
        from luxai.robot.core import Robot
        assert hasattr(Robot, "tts_say_text")

    def test_robot_has_tts_say_text_async(self):
        from luxai.robot.core import Robot
        assert hasattr(Robot, "tts_say_text_async")

    def test_robot_has_gesture_list_files_but_no_async(self):
        from luxai.robot.core import Robot
        assert hasattr(Robot, "gesture_list_files")
        assert not hasattr(Robot, "gesture_list_files_async")

    def test_robot_has_face_show_emotion_async(self):
        from luxai.robot.core import Robot
        assert hasattr(Robot, "face_show_emotion_async")

    def test_robot_has_microphone_stream_on_int_event(self):
        from luxai.robot.core import Robot
        assert hasattr(Robot, "microphone_stream_on_int_event")

    def test_robot_has_motor_stream_open_joints_command_writer(self):
        from luxai.robot.core import Robot
        assert hasattr(Robot, "motor_stream_open_joints_command_writer")

    def test_robot_namespace_properties_exist(self):
        from luxai.robot.core import Robot
        for ns in ("tts", "face", "gesture", "motor", "media", "speaker", "microphone"):
            assert hasattr(Robot, ns), f"Robot missing namespace property {ns!r}"
