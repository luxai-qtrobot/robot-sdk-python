"""
tests/test_actions.py — Unit tests for ActionHandle, ActionError,
ActionCancelledError, wait_all_actions, and wait_any_action.

All tests use a mock rpc_call function — no transport or robot needed.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, call

import pytest

from luxai.robot.core.actions import (
    ActionHandle,
    ActionError,
    ActionCancelledError,
    wait_all_actions,
    wait_any_action,
)


# ---------------------------------------------------------------------------
# Mock RPC call factory helpers
# ---------------------------------------------------------------------------

def instant_rpc(response: Any = None, status: bool = True, exc: Optional[Exception] = None):
    """Return a rpc_call function that resolves immediately."""
    def _rpc(service_name: str, args: Dict, timeout=None):
        if exc is not None:
            raise exc
        return {"status": status, "response": response}
    return _rpc


def blocking_rpc(gate: threading.Event, response: Any = None, status: bool = True):
    """Return a rpc_call function that blocks until gate.set() is called."""
    def _rpc(service_name: str, args: Dict, timeout=None):
        gate.wait()
        return {"status": status, "response": response}
    return _rpc


def make_handle(
    service_name: str = "/test/action",
    args: Optional[Dict] = None,
    cancel_service_name: Optional[str] = None,
    response: Any = None,
    status: bool = True,
    exc: Optional[Exception] = None,
    gate: Optional[threading.Event] = None,
) -> ActionHandle:
    if gate is not None:
        rpc = blocking_rpc(gate, response=response, status=status)
    else:
        rpc = instant_rpc(response=response, status=status, exc=exc)
    return ActionHandle(
        service_name=service_name,
        args=args or {},
        cancel_service_name=cancel_service_name,
        rpc_call=rpc,
    )


# ---------------------------------------------------------------------------
# Basic success / result
# ---------------------------------------------------------------------------

class TestActionHandleSuccess:

    def test_result_returns_unwrapped_response(self):
        h = make_handle(response=["a", "b", "c"])
        assert h.result() == ["a", "b", "c"]

    def test_result_returns_none_when_response_is_none(self):
        h = make_handle(response=None)
        assert h.result() is None

    def test_result_returns_dict_response(self):
        h = make_handle(response={"key": 42})
        assert h.result() == {"key": 42}

    def test_done_is_true_after_result(self):
        h = make_handle(response="ok")
        h.result()
        assert h.done() is True

    def test_wait_returns_without_raising(self):
        h = make_handle(response="ok")
        h.wait()   # should not raise

    def test_wait_is_idempotent(self):
        h = make_handle(response="ok")
        h.wait()
        h.wait()  # calling again is safe


# ---------------------------------------------------------------------------
# Timing: done() transitions False → True
# ---------------------------------------------------------------------------

class TestActionHandleTiming:

    def test_done_false_while_rpc_is_blocking(self):
        gate = threading.Event()
        h = make_handle(gate=gate)
        # Give the thread a moment to start and block
        time.sleep(0.02)
        assert h.done() is False
        gate.set()
        h.wait()

    def test_done_true_after_rpc_completes(self):
        gate = threading.Event()
        h = make_handle(gate=gate, response="hello")
        gate.set()
        h.wait()
        assert h.done() is True

    def test_wait_blocks_until_gate_is_set(self):
        gate = threading.Event()
        h = make_handle(gate=gate, response=42)
        results = []
        def waiter():
            h.wait()
            results.append("done")
        t = threading.Thread(target=waiter, daemon=True)
        t.start()
        time.sleep(0.02)
        assert results == []  # still blocking
        gate.set()
        t.join(timeout=1.0)
        assert results == ["done"]

    def test_wait_with_tight_timeout_raises_when_blocking(self):
        gate = threading.Event()
        h = make_handle(gate=gate)
        with pytest.raises(TimeoutError):
            h.wait(timeout=0.05)
        gate.set()   # unblock the thread so it doesn't leak


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

class TestActionHandleErrors:

    def test_result_raises_action_error_when_status_false(self):
        h = make_handle(response="some error detail", status=False)
        with pytest.raises(ActionError):
            h.result()

    def test_result_raises_action_error_wrapping_transport_exception(self):
        h = make_handle(exc=RuntimeError("ZMQ socket closed"))
        with pytest.raises(ActionError):
            h.result()

    def test_action_error_is_exception(self):
        assert issubclass(ActionError, Exception)

    def test_action_cancelled_error_is_action_error(self):
        assert issubclass(ActionCancelledError, ActionError)


# ---------------------------------------------------------------------------
# Cancellation
# ---------------------------------------------------------------------------

class TestActionHandleCancel:

    def test_cancel_without_cancel_service_is_noop(self):
        """cancel() should be silently ignored when no cancel service is set."""
        gate = threading.Event()
        h = make_handle(gate=gate)
        h.cancel()   # should not raise
        gate.set()
        h.wait()

    def test_cancel_calls_cancel_rpc(self):
        """cancel() must call rpc_call with the cancel service name."""
        called_services = []

        def tracking_rpc(service_name, args, timeout=None):
            called_services.append(service_name)
            return {"status": True, "response": None}

        gate = threading.Event()

        def slow_rpc(svc, args, timeout=None):
            gate.wait()
            return {"status": True, "response": None}

        h = ActionHandle(
            service_name="/test/action",
            args={},
            cancel_service_name="/test/stop",
            rpc_call=slow_rpc,
        )

        # Patch the internal rpc call used by cancel() — but cancel() calls
        # self._call_rpc which is the same rpc_call passed at construction.
        # We need to replace it temporarily to track the cancel call.
        h._call_rpc = tracking_rpc
        h.cancel()
        assert "/test/stop" in called_services
        gate.set()

    def test_result_raises_cancelled_error_after_cancel(self):
        gate = threading.Event()

        def slow_then_success(svc, args, timeout=None):
            gate.wait()
            return {"status": True, "response": None}

        h = ActionHandle(
            service_name="/test/action",
            args={},
            cancel_service_name="/test/stop",
            rpc_call=slow_then_success,
        )
        # cancel() just fires the cancel RPC and sets _cancelled flag
        h._call_rpc = lambda svc, args, timeout=None: {"status": True, "response": None}
        h.cancel()
        gate.set()   # allow the main thread to finish too

        with pytest.raises(ActionCancelledError):
            h.result()


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

class TestActionHandleCallbacks:

    def test_callback_fires_after_completion(self):
        fired = []
        h = make_handle(response="done")
        h.add_done_callback(lambda handle: fired.append(handle))
        h.wait()
        time.sleep(0.02)  # callbacks fire from the worker thread
        assert len(fired) == 1
        assert fired[0] is h

    def test_callback_fires_immediately_if_already_done(self):
        h = make_handle(response="done")
        h.wait()
        fired = []
        h.add_done_callback(lambda handle: fired.append(handle))
        assert len(fired) == 1

    def test_multiple_callbacks_all_fire(self):
        fired = []
        h = make_handle(response="done")
        h.add_done_callback(lambda _: fired.append(1))
        h.add_done_callback(lambda _: fired.append(2))
        h.wait()
        time.sleep(0.02)
        assert sorted(fired) == [1, 2]

    def test_callback_exception_does_not_crash_other_callbacks(self):
        results = []
        h = make_handle(response="ok")

        def bad_cb(handle):
            raise RuntimeError("intentional error")

        def good_cb(handle):
            results.append("good")

        h.add_done_callback(bad_cb)
        h.add_done_callback(good_cb)
        h.wait()
        time.sleep(0.02)
        assert "good" in results


# ---------------------------------------------------------------------------
# wait_all_actions
# ---------------------------------------------------------------------------

class TestWaitAllActions:

    def test_returns_when_all_done(self):
        handles = [make_handle(response=i) for i in range(5)]
        wait_all_actions(handles)   # should not raise

    def test_all_handles_are_done_after_call(self):
        handles = [make_handle(response=i) for i in range(3)]
        wait_all_actions(handles)
        assert all(h.done() for h in handles)

    def test_empty_list_is_noop(self):
        wait_all_actions([])

    def test_timeout_raises_when_one_handle_is_slow(self):
        gate = threading.Event()
        fast = make_handle(response="fast")
        slow = make_handle(gate=gate)
        fast.wait()
        with pytest.raises(TimeoutError):
            wait_all_actions([fast, slow], timeout=0.05)
        gate.set()


# ---------------------------------------------------------------------------
# wait_any_action
# ---------------------------------------------------------------------------

class TestWaitAnyAction:

    def test_returns_handle_that_finished_first(self):
        gate = threading.Event()
        fast = make_handle(response="fast")
        slow = make_handle(gate=gate)
        fast.wait()   # ensure fast is done before calling wait_any
        result = wait_any_action([fast, slow])
        assert result is fast
        gate.set()

    def test_raises_on_empty_list(self):
        with pytest.raises(ValueError):
            wait_any_action([])

    def test_timeout_raises_when_nothing_finishes(self):
        gate = threading.Event()
        h1 = make_handle(gate=gate)
        h2 = make_handle(gate=threading.Event())
        with pytest.raises(TimeoutError):
            wait_any_action([h1, h2], timeout=0.05)
        gate.set()

    def test_returns_when_first_of_many_finishes(self):
        gates = [threading.Event() for _ in range(4)]
        handles = [make_handle(gate=g) for g in gates]
        # Release only the third handle
        gates[2].set()
        handles[2].wait()
        result = wait_any_action(handles)
        assert result is handles[2]
        # Cleanup
        for g in gates:
            g.set()
