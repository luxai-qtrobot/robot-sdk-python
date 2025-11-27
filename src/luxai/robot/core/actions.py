# src/luxai/robot/core/actions.py
from __future__ import annotations

import threading
from typing import Any, Callable, Dict, List, Optional

from .transport.transport import Transport


class ActionError(Exception):
    """Raised when the robot reports an error for an action or RPC fails."""


class ActionCancelledError(ActionError):
    """Raised when result() is called on a cancelled action."""


class ActionHandle:
    """
    Represents a long-running robot action.

    Internally, each handle uses a worker thread that calls
    Transport.call_rpc(...) (which is blocking at magpie level),
    and exposes a non-blocking API to the user.
    """

    def __init__(
        self,
        transport: Transport,
        service_name: str,
        args: Dict[str, Any],
        *,
        timeout: float | None = None,
        cancel_service_name: str | None = None,
    ) -> None:
        self._transport = transport
        self._service_name = service_name
        self._args = args
        self._timeout = timeout
        self._cancel_service_name = cancel_service_name

        self._done_event = threading.Event()
        self._lock = threading.Lock()
        self._callbacks: List[Callable[[ActionHandle], None]] = []

        self._result: Any = None
        self._error: Exception | None = None
        self._cancelled: bool = False

        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    # ---------- internal worker ----------
    def _run(self) -> None:
        try:
            raw = self._transport.call_rpc(
                self._service_name,
                self._args,
                timeout=self._timeout,
            )
            # Expecting: {"status": bool, "response": ...}
            status = bool(raw.get("status", False))
            if not status:
                self._error = ActionError(
                    f"Robot reported failure for {self._service_name}: "
                    f"{raw.get('response')!r}"
                )
            else:
                self._result = raw.get("response")
        except Exception as e:
            self._error = e
        finally:
            self._done_event.set()
            self._fire_callbacks()

    def _fire_callbacks(self) -> None:
        with self._lock:
            callbacks = list(self._callbacks)
        for cb in callbacks:
            try:
                cb(self)
            except Exception:
                # Swallow to not break others; logging can be added
                pass

    # ---------- public API ----------
    def done(self) -> bool:
        """Return True if the action has finished (success, failure, or cancel)."""
        return self._done_event.is_set()

    def wait(self, timeout: float | None = None) -> None:
        """
        Block until the action finishes (success, failure, or cancel).

        Raises:
            TimeoutError: if not finished within 'timeout'.
        """        
        ok = self._done_event.wait(timeout)
        if not ok:
            raise TimeoutError("Action did not finish within timeout")

    def result(self, timeout: float | None = None) -> Any:
        """
        Block until the action finishes and return its result (if any).

        Raises:
            TimeoutError: if not finished within 'timeout'.
            ActionCancelledError: if the action was cancelled.
            ActionError: if the robot reported failure or the RPC errored.
        """
        self.wait(timeout)
        if self._cancelled:
            raise ActionCancelledError("Action was cancelled")
        if self._error is not None:
            # If it's already an ActionError, keep it; otherwise wrap
            if isinstance(self._error, ActionError):
                raise self._error
            raise ActionError(f"Action failed: {self._error}") from self._error
        return self._result

    def cancel(self, timeout: float | None = None) -> None:
        """
        Best-effort cancellation.

        If a cancel service is defined, this issues a separate RPC
        (e.g. /qt_robot/speech/stop) and, on success, marks the action
        as cancelled. It does not forcibly kill the worker thread; the
        underlying RPC is expected to return when the robot honours the stop.
        """
        if self._cancel_service_name is None:
            # No cancel supported for this action
            return

        try:
            self._transport.call_rpc(
                self._cancel_service_name,
                args={},
                timeout=timeout,
            )
            self._cancelled = True
        except Exception as e:
            raise ActionError(f"Cancel failed: {e}") from e

    def add_done_callback(self, callback: Callable[["ActionHandle"], None]) -> None:
        """
        Register a callback to be called once when the action finishes.

        The callback receives this ActionHandle as its only argument.
        If the action is already finished, the callback is invoked immediately.
        """
        with self._lock:
            if self._done_event.is_set():
                cb = callback
            else:
                self._callbacks.append(callback)
                cb = None

        if cb is not None:
            try:
                cb(self)
            except Exception:
                pass


# Simple helpers; you can extend these later if needed
def wait_all(handles: List[ActionHandle], timeout: float | None = None) -> None:
    """
    Block until all actions are finished.

    Raises:
        TimeoutError: if not all actions finish within 'timeout'.
    """
    if timeout is None:
        for h in handles:
            h.wait()
        return

    import time
    deadline = time.time() + timeout
    for h in handles:
        remaining = deadline - time.time()
        if remaining <= 0:
            raise TimeoutError("Not all actions finished within timeout")
        h.wait(timeout=remaining)


def wait_any(handles: List[ActionHandle], timeout: float | None = None) -> ActionHandle:
    """
    Block until the first action finishes and return its handle.

    Raises:
        TimeoutError: if none of the actions finish within 'timeout'.
    """
    import time
    if not handles:
        raise ValueError("wait_any() requires at least one handle")

    if timeout is None:
        while True:
            for h in handles:
                if h.done():
                    return h
            time.sleep(0.01)

    deadline = time.time() + timeout
    while True:
        for h in handles:
            if h.done():
                return h
        if time.time() >= deadline:
            raise TimeoutError("No action finished within timeout")
        time.sleep(0.01)
