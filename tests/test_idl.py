"""
tests/test_idl.py — Validate the IDL definitions in api_core.py and api_plugins.py.

These tests run entirely without a robot connection and catch:
  - Missing required fields
  - Duplicate service names / topics (wire-level collisions)
  - Malformed param tuples
  - Unknown frame_type strings
  - Invalid async_variant values
"""
from __future__ import annotations

from typing import Any, Dict

import pytest

from luxai.robot.core.idl.api_core import QTROBOT_CORE_APIS
from luxai.robot.core.idl.api_plugins import QTROBOT_PLUGINS_APIS
from luxai.robot.core.api_factory import FRAME_TYPE_REGISTRY


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_rpc() -> Dict[str, Dict[str, Any]]:
    """Merged RPC specs from core + plugins."""
    return {
        **QTROBOT_CORE_APIS.get("rpc", {}),
        **QTROBOT_PLUGINS_APIS.get("rpc", {}),
    }


def _all_stream() -> Dict[str, Dict[str, Any]]:
    """Merged stream specs from core + plugins."""
    return {
        **QTROBOT_CORE_APIS.get("stream", {}),
        **QTROBOT_PLUGINS_APIS.get("stream", {}),
    }


# ---------------------------------------------------------------------------
# RPC field validation
# ---------------------------------------------------------------------------

class TestRpcRequiredFields:

    def test_every_rpc_has_service_name(self):
        for api_id, spec in _all_rpc().items():
            assert "service_name" in spec, f"{api_id!r} missing 'service_name'"
            assert isinstance(spec["service_name"], str), (
                f"{api_id!r} service_name must be str"
            )
            assert spec["service_name"].startswith("/"), (
                f"{api_id!r} service_name must start with '/'"
            )

    def test_every_rpc_has_params_list(self):
        for api_id, spec in _all_rpc().items():
            assert "params" in spec, f"{api_id!r} missing 'params'"
            assert isinstance(spec["params"], list), (
                f"{api_id!r} params must be a list"
            )

    def test_every_rpc_has_response_type(self):
        for api_id, spec in _all_rpc().items():
            assert "response_type" in spec, f"{api_id!r} missing 'response_type'"

    def test_every_rpc_has_doc(self):
        for api_id, spec in _all_rpc().items():
            doc = spec.get("doc", "")
            assert isinstance(doc, str), f"{api_id!r} doc must be str"
            assert len(doc.strip()) > 0, f"{api_id!r} has empty doc string"

    def test_api_keys_follow_namespace_dot_method_format(self):
        for api_id in _all_rpc():
            assert "." in api_id, (
                f"RPC key {api_id!r} must follow 'namespace.method' format"
            )


class TestRpcCancelAndAsyncFields:

    def test_cancel_service_name_is_none_or_nonempty_string(self):
        for api_id, spec in _all_rpc().items():
            val = spec.get("cancel_service_name", None)
            if val is not None:
                assert isinstance(val, str), (
                    f"{api_id!r} cancel_service_name must be str or None"
                )
                assert len(val) > 0, (
                    f"{api_id!r} cancel_service_name must not be empty string"
                )
                assert val.startswith("/"), (
                    f"{api_id!r} cancel_service_name must start with '/'"
                )

    def test_async_variant_is_bool_or_absent(self):
        for api_id, spec in _all_rpc().items():
            if "async_variant" in spec:
                assert isinstance(spec["async_variant"], bool), (
                    f"{api_id!r} async_variant must be bool (True/False)"
                )


class TestRpcParamStructure:

    def test_each_param_is_2_or_3_tuple(self):
        for api_id, spec in _all_rpc().items():
            for i, entry in enumerate(spec.get("params", [])):
                assert isinstance(entry, (tuple, list)), (
                    f"{api_id!r} param[{i}] must be tuple/list"
                )
                assert len(entry) in (2, 3), (
                    f"{api_id!r} param[{i}] must have 2 or 3 elements, got {len(entry)}"
                )

    def test_each_param_name_is_string(self):
        for api_id, spec in _all_rpc().items():
            for i, entry in enumerate(spec.get("params", [])):
                assert isinstance(entry[0], str), (
                    f"{api_id!r} param[{i}] name must be str, got {type(entry[0])}"
                )

    def test_each_param_type_is_type(self):
        for api_id, spec in _all_rpc().items():
            for i, entry in enumerate(spec.get("params", [])):
                # Allow generic types (list, dict, etc.) or typing generics
                ptype = entry[1]
                assert ptype is not None, (
                    f"{api_id!r} param[{i}] type must not be None"
                )

    def test_no_duplicate_param_names_within_spec(self):
        for api_id, spec in _all_rpc().items():
            names = [entry[0] for entry in spec.get("params", [])]
            assert len(names) == len(set(names)), (
                f"{api_id!r} has duplicate param names: {names}"
            )


# ---------------------------------------------------------------------------
# Stream field validation
# ---------------------------------------------------------------------------

class TestStreamRequiredFields:

    def test_every_stream_has_topic(self):
        for api_id, spec in _all_stream().items():
            assert "topic" in spec, f"{api_id!r} missing 'topic'"
            assert isinstance(spec["topic"], str), (
                f"{api_id!r} topic must be str"
            )
            assert len(spec["topic"]) > 0, f"{api_id!r} topic must not be empty"

    def test_every_stream_has_direction(self):
        for api_id, spec in _all_stream().items():
            assert "direction" in spec, f"{api_id!r} missing 'direction'"
            assert spec["direction"] in ("in", "out"), (
                f"{api_id!r} direction must be 'in' or 'out', got {spec['direction']!r}"
            )

    def test_every_stream_has_frame_type(self):
        for api_id, spec in _all_stream().items():
            assert "frame_type" in spec, f"{api_id!r} missing 'frame_type'"

    def test_every_stream_frame_type_in_registry(self):
        for api_id, spec in _all_stream().items():
            ft = spec.get("frame_type")
            assert ft in FRAME_TYPE_REGISTRY, (
                f"{api_id!r} frame_type {ft!r} not in FRAME_TYPE_REGISTRY. "
                f"Valid: {sorted(FRAME_TYPE_REGISTRY)}"
            )

    def test_every_stream_has_doc(self):
        for api_id, spec in _all_stream().items():
            doc = spec.get("doc", "")
            assert isinstance(doc, str), f"{api_id!r} doc must be str"
            assert len(doc.strip()) > 0, f"{api_id!r} has empty doc string"

    def test_stream_api_keys_follow_namespace_dot_name_format(self):
        for api_id in _all_stream():
            assert "." in api_id, (
                f"Stream key {api_id!r} must follow 'namespace.name' format"
            )


# ---------------------------------------------------------------------------
# Uniqueness / collision checks
# ---------------------------------------------------------------------------

class TestUniqueness:

    def test_no_duplicate_rpc_api_keys(self):
        core_keys = set(QTROBOT_CORE_APIS.get("rpc", {}).keys())
        plugin_keys = set(QTROBOT_PLUGINS_APIS.get("rpc", {}).keys())
        overlap = core_keys & plugin_keys
        assert not overlap, (
            f"Duplicate RPC api_keys between core and plugins: {overlap}"
        )

    def test_no_duplicate_stream_api_keys(self):
        core_keys = set(QTROBOT_CORE_APIS.get("stream", {}).keys())
        plugin_keys = set(QTROBOT_PLUGINS_APIS.get("stream", {}).keys())
        overlap = core_keys & plugin_keys
        assert not overlap, (
            f"Duplicate stream api_keys between core and plugins: {overlap}"
        )

    def test_no_duplicate_service_names(self):
        service_names = [
            spec["service_name"] for spec in _all_rpc().values()
        ]
        seen: Dict[str, str] = {}
        for api_id, spec in _all_rpc().items():
            sn = spec["service_name"]
            assert sn not in seen, (
                f"Duplicate service_name {sn!r}: used by {seen[sn]!r} and {api_id!r}"
            )
            seen[sn] = api_id

    def test_no_duplicate_stream_topics(self):
        seen: Dict[str, str] = {}
        for api_id, spec in _all_stream().items():
            topic = spec["topic"]
            assert topic not in seen, (
                f"Duplicate topic {topic!r}: used by {seen[topic]!r} and {api_id!r}"
            )
            seen[topic] = api_id

    def test_cancel_service_names_do_not_clash_with_rpc_service_names_unintentionally(self):
        """
        Each cancel_service_name should match an existing service_name in the IDL
        OR be a dedicated cancel-only service. This test just ensures cancel
        service names are at least syntactically valid strings (already covered
        above), not that they are separately defined — that is a firmware concern.
        """
        for api_id, spec in _all_rpc().items():
            csn = spec.get("cancel_service_name")
            if csn:
                assert isinstance(csn, str) and csn.startswith("/"), (
                    f"{api_id!r} cancel_service_name {csn!r} is invalid"
                )


# ---------------------------------------------------------------------------
# Frame type registry completeness
# ---------------------------------------------------------------------------

class TestFrameTypeRegistry:

    def test_registry_contains_common_frame_types(self):
        expected = {
            "AudioFrameRaw", "ImageFrameRaw", "JointStateFrame",
            "JointCommandFrame", "DictFrame", "StringFrame", "ListFrame",
        }
        for ft in expected:
            assert ft in FRAME_TYPE_REGISTRY, (
                f"Expected {ft!r} in FRAME_TYPE_REGISTRY"
            )

    def test_registry_values_are_classes(self):
        for name, cls in FRAME_TYPE_REGISTRY.items():
            assert isinstance(cls, type), (
                f"FRAME_TYPE_REGISTRY[{name!r}] must be a class, got {type(cls)}"
            )
