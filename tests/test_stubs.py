"""
tests/test_stubs.py — Validate the output of the stub generator.

Imports generate_client_stub() directly from scrtipts/gen_robot_stubs.py
(note: directory has a legacy typo) and checks that the generated content:
  - is valid Python (ast.parse)
  - contains a property for every IDL namespace
  - contains sync and async method signatures for the expected APIs
  - contains stream reader / writer / callback methods
"""
from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import the generator without installing it as a package
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scrtipts"


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "gen_robot_stubs", _SCRIPTS_DIR / "gen_robot_stubs.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_gen = _load_generator()
generate_client_stub = _gen.generate_client_stub


# ---------------------------------------------------------------------------
# Cached stub content (generated once per test session)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def stub_content() -> str:
    return generate_client_stub()


# ---------------------------------------------------------------------------
# Validity
# ---------------------------------------------------------------------------

class TestStubValidity:

    def test_stub_is_valid_python(self, stub_content):
        try:
            ast.parse(stub_content)
        except SyntaxError as e:
            pytest.fail(f"Generated stub is not valid Python: {e}")

    def test_stub_is_non_empty(self, stub_content):
        assert len(stub_content.strip()) > 100

    def test_stub_contains_robot_class(self, stub_content):
        assert "class Robot" in stub_content


# ---------------------------------------------------------------------------
# Namespace properties on Robot
# ---------------------------------------------------------------------------

class TestStubNamespaces:

    EXPECTED_NAMESPACES = [
        "tts", "face", "gesture", "motor",
        "media", "speaker", "microphone",
        # plugin namespaces
        "camera", "asr",
    ]

    def test_all_namespaces_present_as_properties(self, stub_content):
        for ns in self.EXPECTED_NAMESPACES:
            # The generator emits:  def <ns>(self) -> <Ns>API:
            assert f"def {ns}(self)" in stub_content, (
                f"Namespace property {ns!r} not found in stub"
            )

    def test_all_api_classes_present(self, stub_content):
        for ns in self.EXPECTED_NAMESPACES:
            cls_name = f"{ns.capitalize()}API"
            assert f"class {cls_name}" in stub_content, (
                f"API class {cls_name!r} not found in stub"
            )


# ---------------------------------------------------------------------------
# RPC methods — sync
# ---------------------------------------------------------------------------

class TestStubSyncMethods:

    def test_tts_say_text_sync_present(self, stub_content):
        assert "def say_text(self" in stub_content

    def test_face_list_emotions_sync_present(self, stub_content):
        assert "def list_emotions(self" in stub_content

    def test_gesture_list_files_sync_present(self, stub_content):
        assert "def list_files(self" in stub_content

    def test_motor_home_all_sync_present(self, stub_content):
        assert "def home_all(self" in stub_content

    def test_speaker_set_volume_sync_present(self, stub_content):
        assert "def set_volume(self" in stub_content

    def test_microphone_get_int_tuning_sync_present(self, stub_content):
        assert "def get_int_tuning(self" in stub_content


# ---------------------------------------------------------------------------
# RPC methods — async (only for cancellable RPCs)
# ---------------------------------------------------------------------------

class TestStubAsyncMethods:

    def test_tts_say_text_async_present(self, stub_content):
        assert "def say_text_async(self" in stub_content

    def test_face_show_emotion_async_present(self, stub_content):
        assert "def show_emotion_async(self" in stub_content

    def test_gesture_play_file_async_present(self, stub_content):
        assert "def play_file_async(self" in stub_content

    def test_media_play_fg_audio_file_async_present(self, stub_content):
        assert "def play_fg_audio_file_async(self" in stub_content

    def test_asr_recognize_azure_async_present(self, stub_content):
        assert "def recognize_azure_async(self" in stub_content

    def test_face_list_emotions_no_async(self, stub_content):
        """list_emotions has no cancel_service_name → no _async variant."""
        assert "def list_emotions_async(self" not in stub_content

    def test_gesture_list_files_no_async(self, stub_content):
        assert "def list_files_async(self" not in stub_content

    def test_speaker_set_volume_no_async(self, stub_content):
        assert "def set_volume_async(self" not in stub_content

    def test_async_return_type_is_action_handle(self, stub_content):
        assert "-> ActionHandle:" in stub_content


# ---------------------------------------------------------------------------
# Stream methods
# ---------------------------------------------------------------------------

class TestStubStreamMethods:

    def test_motor_stream_class_present(self, stub_content):
        assert "class MotorStreamAPI" in stub_content

    def test_microphone_stream_class_present(self, stub_content):
        assert "class MicrophoneStreamAPI" in stub_content

    def test_camera_stream_class_present(self, stub_content):
        assert "class CameraStreamAPI" in stub_content

    def test_open_reader_method_present(self, stub_content):
        assert "def open_int_audio_ch0_reader(self" in stub_content

    def test_on_callback_method_present(self, stub_content):
        # microphone VAD events
        assert "def on_int_event(self" in stub_content

    def test_writer_method_present(self, stub_content):
        assert "def open_fg_audio_stream_writer(self" in stub_content

    def test_stream_reader_returns_typed_stream_reader(self, stub_content):
        assert "TypedStreamReader" in stub_content

    def test_stream_writer_returns_typed_stream_writer(self, stub_content):
        assert "TypedStreamWriter" in stub_content

    def test_on_callback_returns_stream_subscription(self, stub_content):
        assert "StreamSubscription" in stub_content

    def test_namespace_api_has_stream_property(self, stub_content):
        # The namespace class should expose a .stream property
        assert "def stream(self)" in stub_content


# ---------------------------------------------------------------------------
# client_base.pyi marker is replaced
# ---------------------------------------------------------------------------

class TestStubBaseIntegration:

    def test_auto_generated_marker_present_with_content_after_it(self, stub_content):
        """
        The generator keeps the marker comment so it can be re-run safely,
        and appends namespace @property stubs immediately after it.
        """
        marker = "# --- AUTO-GENERATED ROBOT NAMESPACES ---"
        assert marker in stub_content
        marker_pos = stub_content.index(marker)
        # At least one @property should appear after the marker
        assert "@property" in stub_content[marker_pos:]

    def test_stub_imports_action_handle(self, stub_content):
        assert "ActionHandle" in stub_content

    def test_stub_imports_transport(self, stub_content):
        assert "Transport" in stub_content
