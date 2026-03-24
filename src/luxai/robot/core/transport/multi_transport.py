# src/luxai/robot/core/transport/multi_transport.py
from __future__ import annotations

import queue
import threading
from typing import Any, Dict, List, Protocol, Sequence, Tuple, Union, runtime_checkable

from luxai.magpie.transport import RpcRequester, StreamReader, StreamWriter

from .transport import Transport, TransportsMeta, SupportsPreallocation, UnsupportedAPIError


# ---------------------------------------------------------------------------
# RaceRequester — fires all requesters in parallel, returns first success
# ---------------------------------------------------------------------------

class _RaceRequester:
    """
    RpcRequester that races multiple underlying requesters.

    All are called concurrently; the first successful response wins.
    Remaining threads continue to completion but their results are discarded.
    Raises UnsupportedAPIError if every requester fails.
    """

    def __init__(self, requesters: List[RpcRequester]) -> None:
        self._requesters = requesters

    def call(self, rpc_req: Dict[str, Any], *, timeout: float | None = None) -> Dict[str, Any]:
        if len(self._requesters) == 1:
            return self._requesters[0].call(rpc_req, timeout=timeout)

        result_q: queue.Queue[Tuple[str, Any]] = queue.Queue()

        def _call_one(req: RpcRequester) -> None:
            try:
                result_q.put(("ok", req.call(rpc_req, timeout=timeout)))
            except Exception as e:  # noqa: BLE001
                result_q.put(("err", e))

        threads = [
            threading.Thread(target=_call_one, args=(r,), daemon=True)
            for r in self._requesters
        ]
        for t in threads:
            t.start()

        errors: List[Exception] = []
        for _ in range(len(self._requesters)):
            try:
                status, value = result_q.get(timeout=timeout)
            except queue.Empty:
                raise TimeoutError(
                    "WinnerTakesAll: all transports timed out before responding."
                )
            if status == "ok":
                return value  # type: ignore[return-value]
            errors.append(value)

        raise UnsupportedAPIError(
            f"WinnerTakesAll: all transports failed. Errors: {errors}"
        )


# ---------------------------------------------------------------------------
# Routing policy protocol
# ---------------------------------------------------------------------------

_Candidates = List[Tuple[int, Transport]]  # sorted by priority descending


@runtime_checkable
class RoutingPolicy(Protocol):
    """
    Strategy for selecting a transport (or composing transports) for an API call.

    Implementations receive a *candidates* list of ``(priority, transport)``
    pairs sorted highest-priority-first and the transports_meta block from the
    SYSTEM_DESCRIPTION for the service or stream in question.
    """

    def get_requester(
        self,
        candidates: _Candidates,
        service_name: str,
        transports_meta: TransportsMeta | None,
    ) -> RpcRequester: ...

    def get_stream_reader(
        self,
        candidates: _Candidates,
        topic: str,
        transports_meta: TransportsMeta,
        queue_size: int | None,
    ) -> StreamReader: ...

    def get_stream_writer(
        self,
        candidates: _Candidates,
        topic: str,
        transports_meta: TransportsMeta,
        queue_size: int | None,
    ) -> StreamWriter: ...


# ---------------------------------------------------------------------------
# Built-in policies
# ---------------------------------------------------------------------------

def _first_supporting_requester(
    candidates: _Candidates,
    service_name: str,
    transports_meta: TransportsMeta | None,
) -> RpcRequester:
    """Return the first (highest priority) requester that does not raise."""
    last_err: Exception = UnsupportedAPIError(
        f"No transport supports RPC service {service_name!r}."
    )
    for _, transport in candidates:
        try:
            return transport.get_requester(service_name, transports_meta)
        except UnsupportedAPIError as e:
            last_err = e
    raise last_err


def _first_supporting_reader(
    candidates: _Candidates,
    topic: str,
    transports_meta: TransportsMeta,
    queue_size: int | None,
) -> StreamReader:
    last_err: Exception = UnsupportedAPIError(
        f"No transport supports stream reader for {topic!r}."
    )
    for _, transport in candidates:
        try:
            return transport.get_stream_reader(topic, transports_meta, queue_size)
        except UnsupportedAPIError as e:
            last_err = e
    raise last_err


def _first_supporting_writer(
    candidates: _Candidates,
    topic: str,
    transports_meta: TransportsMeta,
    queue_size: int | None,
) -> StreamWriter:
    last_err: Exception = UnsupportedAPIError(
        f"No transport supports stream writer for {topic!r}."
    )
    for _, transport in candidates:
        try:
            return transport.get_stream_writer(topic, transports_meta, queue_size)
        except UnsupportedAPIError as e:
            last_err = e
    raise last_err


class Priority:
    """
    **Priority** routing policy.

    Each transport is assigned a numeric priority (higher = preferred).
    For every RPC or stream, the highest-priority transport that supports
    the API wins.  Lower-priority transports are tried only if the preferred
    one raises :exc:`UnsupportedAPIError`.

    This is the default policy and the right choice when transports serve
    distinct roles (e.g. MQTT for RPC, WebRTC for streams) *and* you still
    want graceful fallback.

    Example::

        MultiTransport(
            [(mqtt_transport, 10), (webrtc_transport, 5)],
            policy=Priority(),
        )
    """

    def get_requester(
        self,
        candidates: _Candidates,
        service_name: str,
        transports_meta: TransportsMeta | None,
    ) -> RpcRequester:
        return _first_supporting_requester(candidates, service_name, transports_meta)

    def get_stream_reader(
        self,
        candidates: _Candidates,
        topic: str,
        transports_meta: TransportsMeta,
        queue_size: int | None,
    ) -> StreamReader:
        return _first_supporting_reader(candidates, topic, transports_meta, queue_size)

    def get_stream_writer(
        self,
        candidates: _Candidates,
        topic: str,
        transports_meta: TransportsMeta,
        queue_size: int | None,
    ) -> StreamWriter:
        return _first_supporting_writer(candidates, topic, transports_meta, queue_size)


class WinnerTakesAll:
    """
    **Winner-takes-all** routing policy for RPC calls.

    All transports that support an RPC service are called *concurrently*; the
    first successful response is returned and the rest are silently discarded.
    This minimises latency when multiple transports can serve the same service
    but have variable round-trip times (e.g. a local ZMQ path vs. a cloud
    MQTT path).

    For **streams** this policy falls back to :class:`Priority` — racing two
    independent stream readers would duplicate frames, which is never useful.

    Example::

        MultiTransport(
            [zmq_transport, mqtt_transport],
            policy=WinnerTakesAll(),
        )
    """

    _priority_fallback = Priority()

    def get_requester(
        self,
        candidates: _Candidates,
        service_name: str,
        transports_meta: TransportsMeta | None,
    ) -> RpcRequester:
        requesters: List[RpcRequester] = []
        for _, transport in candidates:
            try:
                requesters.append(transport.get_requester(service_name, transports_meta))
            except UnsupportedAPIError:
                pass

        if not requesters:
            raise UnsupportedAPIError(
                f"WinnerTakesAll: no transport supports RPC service {service_name!r}."
            )
        if len(requesters) == 1:
            return requesters[0]
        return _RaceRequester(requesters)

    def get_stream_reader(
        self,
        candidates: _Candidates,
        topic: str,
        transports_meta: TransportsMeta,
        queue_size: int | None,
    ) -> StreamReader:
        # Racing stream readers would duplicate frames — use Priority instead.
        return self._priority_fallback.get_stream_reader(
            candidates, topic, transports_meta, queue_size
        )

    def get_stream_writer(
        self,
        candidates: _Candidates,
        topic: str,
        transports_meta: TransportsMeta,
        queue_size: int | None,
    ) -> StreamWriter:
        return self._priority_fallback.get_stream_writer(
            candidates, topic, transports_meta, queue_size
        )


# ---------------------------------------------------------------------------
# MultiTransport
# ---------------------------------------------------------------------------

# Accept either plain transports or (transport, priority) pairs.
_TransportEntry = Union[Transport, Tuple[Transport, int]]


class MultiTransport:
    """
    Wraps multiple :class:`Transport` instances and dispatches each RPC or
    stream call according to a :class:`RoutingPolicy`.

    Because ``MultiTransport`` itself implements the :class:`Transport`
    protocol, it can be passed directly to :class:`~luxai.robot.core.Robot`
    with no other changes::

        robot = Robot(transport=MultiTransport([t1, t2], policy=Priority()))

    **Priority assignment**

    Pass plain transports for equal priority (insertion order = tie-break)::

        MultiTransport([mqtt_t, webrtc_t])          # mqtt tried first

    Or pass ``(transport, priority)`` tuples for explicit control::

        MultiTransport(
            [(mqtt_t, 10), (webrtc_t, 5)],          # mqtt always preferred
            policy=Priority(),
        )

    **Policies**

    - :class:`Priority` *(default)* — highest-priority supporting transport wins.
    - :class:`WinnerTakesAll` — all supporting transports race for RPC; first
      response wins. Streams still use Priority.

    **Preallocation**

    ``MultiTransport`` implements :class:`SupportsPreallocation`: if any
    wrapped transport supports it, ``preallocate_requesters`` is forwarded to
    all that do.
    """

    def __init__(
        self,
        transports: Sequence[_TransportEntry],
        *,
        policy: RoutingPolicy | None = None,
    ) -> None:
        if not transports:
            raise ValueError("MultiTransport requires at least one transport.")

        # Normalise to (priority, transport), highest priority first.
        n = len(transports)
        normalised: List[Tuple[int, Transport]] = []
        for i, entry in enumerate(transports):
            if isinstance(entry, tuple):
                t, p = entry
                normalised.append((p, t))
            else:
                # Default: preserve insertion order; first entry has highest priority.
                normalised.append((n - i, entry))

        self._candidates: _Candidates = sorted(normalised, key=lambda x: -x[0])
        self._policy: RoutingPolicy = policy if policy is not None else Priority()

    # ------------------------------------------------------------------
    # Transport protocol
    # ------------------------------------------------------------------

    def get_requester(
        self,
        service_name: str,
        transports_meta: TransportsMeta | None,
    ) -> RpcRequester:
        return self._policy.get_requester(self._candidates, service_name, transports_meta)

    def get_stream_reader(
        self,
        topic: str,
        transports_meta: TransportsMeta,
        queue_size: int | None = None,
    ) -> StreamReader:
        return self._policy.get_stream_reader(
            self._candidates, topic, transports_meta, queue_size
        )

    def get_stream_writer(
        self,
        topic: str,
        transports_meta: TransportsMeta,
        queue_size: int | None = None,
    ) -> StreamWriter:
        return self._policy.get_stream_writer(
            self._candidates, topic, transports_meta, queue_size
        )

    def close(self) -> None:
        """Close all wrapped transports."""
        for _, t in self._candidates:
            try:
                t.close()
            except Exception:  # noqa: BLE001
                pass

    # ------------------------------------------------------------------
    # SupportsPreallocation — forward to all capable transports
    # ------------------------------------------------------------------

    def preallocate_requesters(
        self,
        rpc_routes: Dict[str, Dict[str, Any]],
    ) -> None:
        for _, t in self._candidates:
            if isinstance(t, SupportsPreallocation):
                t.preallocate_requesters(rpc_routes)

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "MultiTransport":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        transport_list = ", ".join(
            f"{type(t).__name__}(priority={p})" for p, t in self._candidates
        )
        return (
            f"MultiTransport(policy={type(self._policy).__name__}, "
            f"transports=[{transport_list}])"
        )
