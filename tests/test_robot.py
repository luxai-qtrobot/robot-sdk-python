"""
tests/test_robot.py — Unit tests for the Robot class using MockTransport.

Every test constructs a Robot backed by MockTransport (no network, no ZMQ).
The mock transport returns a configurable SYSTEM_DESCRIPTION on the handshake
RPC so that Robot._rpc_routes / _stream_routes are populated.
"""
from __future__ import annotations

import copy
from typing import Any, Dict
from unittest.mock import patch

import pytest

from luxai.robot.core import Robot
from luxai.robot.core.actions import ActionError, ActionHandle
from luxai.robot.core.transport.transport import UnsupportedAPIError
from luxai.robot.core.config import SYSTEM_DESCRIBE_SERVICE

from tests.conftest import MockTransport, MINIMAL_SYSTEM_DESC


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_robot(desc: Dict[str, Any] = None) -> Robot:
    """Create a Robot with MockTransport, optionally overriding SYSTEM_DESC."""
    transport = MockTransport(system_description=desc)
    return Robot(transport=transport)


# ---------------------------------------------------------------------------
# Handshake — identity and route building
# ---------------------------------------------------------------------------

class TestHandshake:

    def test_robot_type_set_from_description(self):
        robot = make_robot()
        assert robot.robot_type == "test-robot"
        robot.close()

    def test_robot_serial_set_from_description(self):
        robot = make_robot()
        assert robot.robot_id == "TEST001"
        robot.close()

    def test_sdk_version_set_from_description(self):
        robot = make_robot()
        assert robot.sdk_version == "1.0.0"
        robot.close()

    def test_rpc_routes_populated(self):
        robot = make_robot()
        assert "/tts/engine/say/text" in robot._rpc_routes
        assert "/face/emotion/show" in robot._rpc_routes
        robot.close()

    def test_stream_routes_populated(self):
        robot = make_robot()
        assert "/mic/int/audio/ch0/stream:o" in robot._stream_routes
        assert "/motor/joints/command/stream:i" in robot._stream_routes
        robot.close()

    def test_handshake_failure_does_not_raise(self):
        """If the handshake RPC returns status=False, Robot raises RuntimeError."""
        import pytest
        transport = MockTransport()
        transport.requester.set_response(SYSTEM_DESCRIBE_SERVICE, status=False)
        with pytest.raises(RuntimeError):
            Robot(transport=transport)

    def test_handshake_exception_does_not_raise(self):
        """If transport.get_requester raises, Robot raises RuntimeError."""
        import pytest
        class BrokenTransport(MockTransport):
            def get_requester(self, service_name, transports):
                raise RuntimeError("connection refused")
        with pytest.raises(RuntimeError):
            Robot(transport=BrokenTransport())


# ---------------------------------------------------------------------------
# Version compatibility warnings
# ---------------------------------------------------------------------------

class TestVersionWarnings:

    def test_warns_when_sdk_older_than_min_sdk(self):
        desc = {**MINIMAL_SYSTEM_DESC, "min_sdk": "99.0.0"}
        with patch("luxai.robot.core.client.Logger") as mock_logger:
            robot = make_robot(desc)
            mock_logger.warning.assert_called()
        robot.close()

    def test_warns_when_sdk_newer_than_max_sdk(self):
        desc = {**MINIMAL_SYSTEM_DESC, "max_sdk": "0.0.1"}
        with patch("luxai.robot.core.client.Logger") as mock_logger:
            robot = make_robot(desc)
            mock_logger.warning.assert_called()
        robot.close()

    def test_no_warning_when_sdk_in_range(self):
        desc = {**MINIMAL_SYSTEM_DESC, "min_sdk": "0.1.0", "max_sdk": "99.0.0"}
        with patch("luxai.robot.core.client.Logger") as mock_logger:
            robot = make_robot(desc)
            mock_logger.warning.assert_not_called()
        robot.close()


# ---------------------------------------------------------------------------
# _call_rpc_sync
# ---------------------------------------------------------------------------

class TestCallRpcSync:

    def test_returns_unwrapped_response_on_success(self, robot):
        robot._robot_transport.requester.set_response(
            "/tts/engine/say/text", status=True, response="spoken"
        )
        result = robot._call_rpc_sync("/tts/engine/say/text", {"engine": "acapela", "text": "hi"})
        assert result == "spoken"

    def test_returns_none_when_response_is_none(self, robot):
        robot._robot_transport.requester.set_response(
            "/face/emotion/show", status=True, response=None
        )
        result = robot._call_rpc_sync("/face/emotion/show", {"emotion": "QT/kiss"})
        assert result is None

    def test_raises_action_error_on_status_false(self, robot):
        robot._robot_transport.requester.set_response(
            "/tts/engine/say/text", status=False, response="engine not found"
        )
        with pytest.raises(ActionError):
            robot._call_rpc_sync("/tts/engine/say/text", {"engine": "bad"})

    def test_raises_unsupported_api_error_for_unknown_service(self, robot):
        with pytest.raises(UnsupportedAPIError):
            robot._call_rpc_sync("/nonexistent/service", {})


# ---------------------------------------------------------------------------
# _start_action
# ---------------------------------------------------------------------------

class TestStartAction:

    def test_returns_action_handle(self, robot):
        robot._robot_transport.requester.set_response(
            "/tts/engine/say/text", status=True, response=None
        )
        handle = robot._start_action(
            "/tts/engine/say/text",
            {"engine": "acapela", "text": "hi"},
            cancel_service_name="/tts/engine/cancel",
        )
        assert isinstance(handle, ActionHandle)
        handle.wait()

    def test_handle_result_matches_response(self, robot):
        robot._robot_transport.requester.set_response(
            "/gesture/file/list", status=True, response=["QT/bye", "QT/happy"]
        )
        handle = robot._start_action("/gesture/file/list", {})
        assert handle.result() == ["QT/bye", "QT/happy"]


# ---------------------------------------------------------------------------
# get_stream_reader / get_stream_writer error paths
# ---------------------------------------------------------------------------

class TestStreamRouteValidation:

    def test_stream_reader_raises_for_unknown_topic(self, robot):
        from luxai.magpie.frames import Frame
        with pytest.raises(UnsupportedAPIError):
            robot.get_stream_reader("/unknown/topic", frame_type=Frame)

    def test_stream_writer_raises_for_unknown_topic(self, robot):
        with pytest.raises(UnsupportedAPIError):
            robot.get_stream_writer("/unknown/topic")

    def test_stream_reader_raises_for_inbound_stream(self, robot):
        """'/motor/joints/command/stream:i' is direction='in' — not readable."""
        from luxai.magpie.frames import Frame
        with pytest.raises(UnsupportedAPIError):
            robot.get_stream_reader("/motor/joints/command/stream:i", frame_type=Frame)

    def test_stream_writer_raises_for_outbound_stream(self, robot):
        """'/mic/int/audio/ch0/stream:o' is direction='out' — not writable."""
        with pytest.raises(UnsupportedAPIError):
            robot.get_stream_writer("/mic/int/audio/ch0/stream:o")


# ---------------------------------------------------------------------------
# get_stream_reader / get_stream_writer happy paths
# ---------------------------------------------------------------------------

class TestStreamRouteHappyPaths:

    def test_stream_reader_calls_transport(self, robot):
        from luxai.magpie.frames import AudioFrameRaw
        robot.get_stream_reader("/mic/int/audio/ch0/stream:o", frame_type=AudioFrameRaw)
        assert len(robot._robot_transport.stream_reader_calls) == 1
        topic, _, _ = robot._robot_transport.stream_reader_calls[0]
        assert topic == "/mic/int/audio/ch0/stream:o"

    def test_stream_reader_passes_queue_size_to_transport(self, robot):
        from luxai.magpie.frames import AudioFrameRaw
        robot.get_stream_reader(
            "/mic/int/audio/ch0/stream:o", frame_type=AudioFrameRaw, queue_size=42
        )
        _, _, qs = robot._robot_transport.stream_reader_calls[0]
        assert qs == 42

    def test_stream_writer_calls_transport(self, robot):
        robot.get_stream_writer("/motor/joints/command/stream:i")
        assert len(robot._robot_transport.stream_writer_calls) == 1
        topic, _, _ = robot._robot_transport.stream_writer_calls[0]
        assert topic == "/motor/joints/command/stream:i"


# ---------------------------------------------------------------------------
# Plugin management
# ---------------------------------------------------------------------------

class TestPluginManagement:

    def test_enable_unknown_plugin_raises_value_error(self, robot):
        with pytest.raises(ValueError, match="Unknown plugin"):
            robot.enable_plugin("definitely-not-a-plugin", transport=None)

    def test_enable_uninstalled_plugin_raises_runtime_error(self, robot):
        """Plugins registered as None in PLUGIN_REGISTRY are not installed."""
        from luxai.robot.core.plugins import PLUGIN_REGISTRY
        # Temporarily register a None entry
        PLUGIN_REGISTRY["_test_missing_"] = None
        try:
            with pytest.raises(RuntimeError, match="not installed"):
                robot.enable_plugin("_test_missing_", transport=None)
        finally:
            del PLUGIN_REGISTRY["_test_missing_"]

    def test_double_enable_is_ignored(self, robot):
        """Enabling the same plugin twice should not raise."""
        from unittest.mock import MagicMock
        from luxai.robot.core.plugins import PLUGIN_REGISTRY

        mock_plugin_cls = MagicMock()
        mock_plugin_instance = MagicMock()
        mock_plugin_cls.return_value = mock_plugin_instance

        PLUGIN_REGISTRY["_test_double_"] = mock_plugin_cls
        try:
            robot.enable_plugin("_test_double_", transport=MagicMock())
            robot.enable_plugin("_test_double_", transport=MagicMock())
            # start() should only have been called once
            assert mock_plugin_instance.start.call_count == 1
        finally:
            del PLUGIN_REGISTRY["_test_double_"]

    def test_disable_plugin_calls_stop(self, robot):
        from unittest.mock import MagicMock
        from luxai.robot.core.plugins import PLUGIN_REGISTRY

        mock_plugin_cls = MagicMock()
        mock_plugin_instance = MagicMock()
        mock_plugin_cls.return_value = mock_plugin_instance

        PLUGIN_REGISTRY["_test_stop_"] = mock_plugin_cls
        try:
            robot.enable_plugin("_test_stop_", transport=MagicMock())
            robot.disable_plugin("_test_stop_")
            mock_plugin_instance.stop.assert_called_once()
        finally:
            PLUGIN_REGISTRY.pop("_test_stop_", None)

    def test_close_stops_all_active_plugins(self):
        from unittest.mock import MagicMock
        from luxai.robot.core.plugins import PLUGIN_REGISTRY

        mock_plugin_cls = MagicMock()
        mock_plugin_instance = MagicMock()
        mock_plugin_cls.return_value = mock_plugin_instance

        PLUGIN_REGISTRY["_test_close_"] = mock_plugin_cls
        try:
            robot = make_robot()
            robot.enable_plugin("_test_close_", transport=MagicMock())
            robot.close()
            mock_plugin_instance.stop.assert_called_once()
        finally:
            PLUGIN_REGISTRY.pop("_test_close_", None)


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

class TestRobotLifecycle:

    def test_close_calls_transport_close(self):
        transport = MockTransport()
        robot = Robot(transport=transport)
        assert not transport.closed
        robot.close()
        assert transport.closed

    def test_context_manager_closes_on_exit(self):
        transport = MockTransport()
        with Robot(transport=transport) as robot:
            assert not transport.closed
        assert transport.closed

    def test_context_manager_closes_on_exception(self):
        transport = MockTransport()
        with pytest.raises(ValueError):
            with Robot(transport=transport):
                raise ValueError("test error")
        assert transport.closed


# ---------------------------------------------------------------------------
# Namespace-to-RPC integration (end-to-end through views)
# ---------------------------------------------------------------------------

class TestNamespaceToRpcIntegration:
    """
    Verify that calling robot.tts.say_text(...) ultimately calls rpc_call
    with the correct service name. Uses only services in MINIMAL_SYSTEM_DESC.
    """

    def test_gesture_list_files_calls_correct_service(self, robot):
        robot._robot_transport.requester.set_response(
            "/gesture/file/list", status=True, response=["QT/bye"]
        )
        result = robot.gesture.list_files()
        assert result == ["QT/bye"]
        calls = robot._robot_transport.requester.calls
        service_names = [c[0] for c in calls]
        assert "/gesture/file/list" in service_names

    def test_face_show_emotion_calls_correct_service(self, robot):
        robot._robot_transport.requester.set_response(
            "/face/emotion/show", status=True, response=None
        )
        robot.face.show_emotion("QT/kiss")
        calls = robot._robot_transport.requester.calls
        service_names = [c[0] for c in calls]
        assert "/face/emotion/show" in service_names

    def test_face_show_emotion_async_returns_handle(self, robot):
        robot._robot_transport.requester.set_response(
            "/face/emotion/show", status=True, response=None
        )
        handle = robot.face.show_emotion_async("QT/kiss")
        assert isinstance(handle, ActionHandle)
        handle.wait()
