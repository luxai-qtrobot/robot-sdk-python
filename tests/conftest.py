"""
Shared fixtures for the luxai-robot SDK unit tests.

The core abstraction is MockTransport — a fake Transport that:
  - returns a configurable SYSTEM_DESCRIPTION on the handshake RPC, so
    Robot.__init__ succeeds without any network connection.
  - routes subsequent RPC calls through MockRpcRequester, which returns
    per-service canned responses.
  - provides MockStreamReader / MockStreamWriter for stream tests.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional, Tuple

import pytest

from luxai.robot.core.config import SYSTEM_DESCRIBE_SERVICE


# ---------------------------------------------------------------------------
# Minimal SYSTEM_DESCRIPTION returned by the mock handshake
# ---------------------------------------------------------------------------

#: A minimal description that includes a handful of RPC services and streams
#: so Robot._rpc_routes / _stream_routes are populated for integration-style
#: tests inside test_robot.py.
MINIMAL_SYSTEM_DESC: Dict[str, Any] = {
    "robot_type": "test-robot",
    "robot_id": "TEST001",
    "sdk_version": "1.0.0",
    "min_sdk": "0.1.0",
    "max_sdk": "9.9.9",
    "rpc": {
        "/tts/engine/say/text": {
            "transports": {"zmq": {"endpoint": "tcp://127.0.0.1:50500"}}
        },
        "/tts/engine/cancel": {
            "transports": {"zmq": {"endpoint": "tcp://127.0.0.1:50500"}}
        },
        "/face/emotion/show": {
            "transports": {"zmq": {"endpoint": "tcp://127.0.0.1:50500"}}
        },
        "/face/emotion/stop": {
            "transports": {"zmq": {"endpoint": "tcp://127.0.0.1:50500"}}
        },
        "/gesture/file/list": {
            "transports": {"zmq": {"endpoint": "tcp://127.0.0.1:50500"}}
        },
    },
    "stream": {
        "/mic/int/audio/ch0/stream:o": {
            "direction": "out",
            "frame_type": "AudioFrameRaw",
            "transports": {"zmq": {"endpoint": "tcp://127.0.0.1:50501", "queue_size": 10}},
        },
        "/motor/joints/command/stream:i": {
            "direction": "in",
            "frame_type": "JointCommandFrame",
            "transports": {"zmq": {"endpoint": "tcp://127.0.0.1:50502"}},
        },
    },
}


# ---------------------------------------------------------------------------
# Mock magpie primitives
# ---------------------------------------------------------------------------

class MockRpcRequester:
    """
    Fake RpcRequester.

    Behaviour:
    - Responses are keyed by service_name (``rpc_req["name"]``).
    - If no entry for a service, returns ``{"status": True, "response": None}``.
    - A ``blocking_event`` can be set to make a specific service block until
      the event is set — useful for ActionHandle timing tests.
    """

    def __init__(
        self,
        responses: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        # service_name -> {"status": bool, "response": Any}
        self.responses: Dict[str, Dict[str, Any]] = responses or {}
        # service_name -> threading.Event  (call blocks until event is set)
        self.blocking: Dict[str, threading.Event] = {}
        # Record of all calls: [(service_name, args, timeout), ...]
        self.calls: List[Tuple[str, Dict, Any]] = []

    def set_response(self, service_name: str, status: bool, response: Any = None) -> None:
        self.responses[service_name] = {"status": status, "response": response}

    def set_blocking(self, service_name: str, event: threading.Event) -> None:
        """Make calls to service_name block until event is set."""
        self.blocking[service_name] = event

    def call(self, rpc_req: Dict[str, Any], timeout: Any = None) -> Dict[str, Any]:
        service_name: str = rpc_req.get("name", "")
        args: Dict = rpc_req.get("args", {})
        self.calls.append((service_name, args, timeout))

        # Block if requested (for ActionHandle tests)
        if service_name in self.blocking:
            self.blocking[service_name].wait()

        return self.responses.get(service_name, {"status": True, "response": None})

    def close(self) -> None:
        pass


class MockStreamReader:
    """
    Fake StreamReader. Returns frames from a pre-loaded queue.
    `read()` returns ``(raw_dict, {})`` or ``None`` when the queue is empty.
    """

    def __init__(self, frames: Optional[List[Dict]] = None) -> None:
        self._frames: List[Dict] = list(frames or [])
        self.closed = False

    def read(self, timeout: Optional[float] = None) -> Optional[Tuple[Dict, Dict]]:
        if self._frames:
            return (self._frames.pop(0), {})
        return None

    def close(self) -> None:
        self.closed = True


class MockStreamWriter:
    """Fake StreamWriter. Records all write() calls."""

    def __init__(self) -> None:
        self.written: List[Tuple[Any, str]] = []
        self.closed = False

    def write(self, data: Any, topic: str) -> None:
        self.written.append((data, topic))

    def close(self) -> None:
        self.closed = True


# ---------------------------------------------------------------------------
# Mock Transport
# ---------------------------------------------------------------------------

class MockTransport:
    """
    Fake Transport implementing the Transport Protocol.

    A single MockRpcRequester handles ALL RPC calls (including the initial
    handshake). Callers configure it via ``requester.set_response(...)``
    before constructing Robot.

    Stream reader/writer instances are also replaceable for per-test control.
    """

    def __init__(self, system_description: Optional[Dict[str, Any]] = None) -> None:
        desc = system_description if system_description is not None else MINIMAL_SYSTEM_DESC
        self.requester = MockRpcRequester()
        self.requester.set_response(
            SYSTEM_DESCRIBE_SERVICE, status=True, response=desc
        )
        self.stream_reader = MockStreamReader()
        self.stream_writer = MockStreamWriter()
        self.closed = False

        # Call records for assertions
        self.requester_calls: List[Tuple[str, Any]] = []
        self.stream_reader_calls: List[Tuple[str, Any, Any]] = []
        self.stream_writer_calls: List[Tuple[str, Any, Any]] = []

    # --- Transport Protocol ---

    def get_requester(self, service_name: str, transports: Any) -> MockRpcRequester:
        self.requester_calls.append((service_name, transports))
        return self.requester

    def get_stream_reader(
        self, topic: str, transports: Any, queue_size: Any = None
    ) -> MockStreamReader:
        self.stream_reader_calls.append((topic, transports, queue_size))
        return self.stream_reader

    def get_stream_writer(
        self, topic: str, transports: Any, queue_size: Any = None
    ) -> MockStreamWriter:
        self.stream_writer_calls.append((topic, transports, queue_size))
        return self.stream_writer

    def close(self) -> None:
        self.closed = True


# ---------------------------------------------------------------------------
# pytest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_transport() -> MockTransport:
    """A fresh MockTransport with MINIMAL_SYSTEM_DESC for each test."""
    return MockTransport()


@pytest.fixture
def robot(mock_transport: MockTransport):
    """
    A Robot instance backed by MockTransport.
    Automatically closed after the test.
    """
    from luxai.robot.core import Robot
    r = Robot(transport=mock_transport)
    yield r
    r.close()
