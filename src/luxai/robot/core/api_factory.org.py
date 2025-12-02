# src/luxai/robot/core/api_factory.py
from __future__ import annotations

import inspect
import threading
from typing import Any, Callable, Dict, TypeVar, Generic

from luxai.magpie.utils import Logger
from luxai.magpie.transport import StreamReader

from .actions import ActionHandle


RobotT = TypeVar("RobotT")  # forward typing for Robot


# ----------------------------------------------------------------------
# Namespace proxies
# ----------------------------------------------------------------------
class _NamespaceProxy(Generic[RobotT]):
    """
    Thin view for a logical namespace, e.g.:

        robot.speech.say(...)
        robot.motors.home(...)

    Internally forwards to methods on the underlying Robot instance
    named as "<namespace>_<method>", e.g. "speech_say".
    """

    def __init__(self, robot: RobotT, namespace: str) -> None:
        self._robot = robot
        self._namespace = namespace
        self._stream_proxy: _StreamNamespaceProxy | None = None

    def __getattr__(self, name: str):
        # Map .say -> robot.speech_say
        method_name = f"{self._namespace}_{name}"
        try:
            attr = getattr(self._robot, method_name)
        except AttributeError as e:
            raise AttributeError(
                f"{self.__class__.__name__} has no attribute {name!r} "
                f"(expected robot method {method_name!r})"
            ) from e
        return attr

    @property
    def stream(self) -> "_StreamNamespaceProxy":
        """
        Access to stream-related helpers for this namespace, e.g.:

            robot.motors.stream.open_joints_state_reader(...)
            robot.motors.stream.on_joints_state(cb)
        """
        if self._stream_proxy is None:
            self._stream_proxy = _StreamNamespaceProxy(self._robot, self._namespace)
        return self._stream_proxy


class _StreamNamespaceProxy(Generic[RobotT]):
    """
    View for stream helpers under a given namespace, e.g.:

        robot.motors.stream.open_joints_state_reader(...)
        robot.motors.stream.open_head_position_writer(...)
        robot.motors.stream.on_joints_state(callback)

    Internally forwards to robot methods named:

        "<namespace>_stream_<operation>"

    For example:
        motors.stream.open_joints_state_reader -> robot.motors_stream_open_joints_state_reader
    """

    def __init__(self, robot: RobotT, namespace: str) -> None:
        self._robot = robot
        self._namespace = namespace

    def __getattr__(self, name: str):
        method_name = f"{self._namespace}_stream_{name}"
        try:
            attr = getattr(self._robot, method_name)
        except AttributeError as e:
            raise AttributeError(
                f"{self.__class__.__name__} has no attribute {name!r} "
                f"(expected robot method {method_name!r})"
            ) from e
        return attr


def _make_namespace_property(namespace: str):
    """
    Create a @property for Robot that returns a _NamespaceProxy.

    Example:
        Robot.speech -> _NamespaceProxy(robot, "speech")
    """

    attr_name = f"_{namespace}_ns_proxy"

    def prop(self) -> _NamespaceProxy:
        proxy = getattr(self, attr_name, None)
        if proxy is None:
            proxy = _NamespaceProxy(self, namespace)
            setattr(self, attr_name, proxy)
        return proxy

    return property(prop)


# ----------------------------------------------------------------------
# Stream subscription helper (for callbacks)
# ----------------------------------------------------------------------
class StreamSubscription:
    """
    Simple subscription wrapper for callback-based stream consumption.

    Usage:
        reader = robot.motors.stream.open_joints_state_reader(...)
        sub = robot.motors.stream.on_joints_state(callback)

    Internally:
        - owns a StreamReader
        - runs a background thread that .read()s from it
        - calls the provided callback for each frame
    """

    def __init__(self, reader: StreamReader, callback: Callable[[Any], None]) -> None:
        self._reader = reader
        self._callback = callback
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                frame = self._reader.read()
                if frame is None:
                    continue
                try:
                    self._callback(frame)
                except Exception as e:
                    Logger.warning(f"StreamSubscription callback raised: {e}")
            except Exception as e:
                Logger.warning(f"StreamSubscription read error: {e}")
                # small backoff could be added here if needed

    def close(self) -> None:
        """Stop the background thread."""
        self._stop_event.set()
        # Let the thread exit naturally; no join() to avoid blocking shutdown


# ----------------------------------------------------------------------
# RPC method factory
# ----------------------------------------------------------------------
def create_rpc_method(
    api_id: str,
    method_name: str,
    spec: Dict[str, Any],
):
    """
    Create a Robot instance method for a single RPC API.

    api_id:
        "speech.say", "gesture.play", etc. (IDL key)
    method_name:
        actual Python name on Robot, e.g. "speech_say".

    Spec keys (from QTROBOT_CORE_APIS["rpc"][api_id]):
        - service_name: str ("/qt_robot/speech/say")
        - cancel_service_name: Optional[str]
        - params: List[(name, type) or (name, type, default)]
        - response_type: type (unused at runtime, for docs/typing only)
        - since: Optional[str]
        - deprecated: bool          (handled at higher level if needed)
        - deprecated_message: Optional[str]
        - robots: Optional[List[str]]
        - doc: Optional[str]
    """

    service_name: str = spec["service_name"]
    cancel_service_name: str | None = spec.get("cancel_service_name")

    # Build signature: (self, <params...>, *, blocking=True)
    params = [
        inspect.Parameter(
            "self",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]

    for entry in spec.get("params", []):
        if len(entry) == 2:
            pname, ptype = entry
            default = inspect.Parameter.empty
        else:
            pname, ptype, default = entry
        params.append(
            inspect.Parameter(
                pname,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=ptype,
            )
        )

    params.append(
        inspect.Parameter(
            "blocking",
            inspect.Parameter.KEYWORD_ONLY,
            default=True,
            annotation=bool,
        )
    )

    signature = inspect.Signature(params)

    def api_func(*args, **kwargs) -> ActionHandle:
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        self = bound.arguments["self"]
        blocking: bool = bound.arguments["blocking"]

        # Build RPC args: skip self and blocking; skip None values
        rpc_args: Dict[str, Any] = {}
        for name, value in bound.arguments.items():
            if name in ("self", "blocking"):
                continue
            if value is None:
                continue
            rpc_args[name] = value

        # Delegate to Robot._start_action
        return self._start_action(
            service_name=service_name,
            args=rpc_args,
            cancel_service_name=cancel_service_name,
            timeout=None,  # Robot decides default timeout
            blocking=blocking,
        )

    api_func.__name__ = method_name
    api_func.__qualname__ = f"Robot.{method_name}"
    api_func.__signature__ = signature

    doc = spec.get("doc") or f"Auto-generated RPC API for service {service_name}."
    api_func.__doc__ = doc

    return api_func


# ----------------------------------------------------------------------
# Stream method factories
# ----------------------------------------------------------------------
def _create_stream_reader_method(
    namespace: str,
    local_name: str,
    topic: str,
):
    """
    Create a Robot method:

        def <namespace>_stream_open_<local_name>_reader(self, queue_size=None) -> StreamReader

    that simply calls Robot.get_stream_reader(topic, queue_size=queue_size).
    """
    method_name = f"{namespace}_stream_open_{local_name}_reader"

    params = [
        inspect.Parameter(
            "self",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ),
        inspect.Parameter(
            "queue_size",
            inspect.Parameter.KEYWORD_ONLY,
            default=None,
            annotation=int | None,
        ),
    ]

    signature = inspect.Signature(params)

    def api_func(*args, **kwargs) -> StreamReader:
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        self = bound.arguments["self"]
        queue_size = bound.arguments["queue_size"]

        return self.get_stream_reader(topic=topic, queue_size=queue_size)

    api_func.__name__ = method_name
    api_func.__qualname__ = f"Robot.{method_name}"
    api_func.__signature__ = signature
    api_func.__doc__ = f"Open a reader for stream topic {topic!r}."

    return method_name, api_func


def _create_stream_writer_method(
    namespace: str,
    local_name: str,
    topic: str,
):
    """
    Create a Robot method:

        def <namespace>_stream_open_<local_name>_writer(self, queue_size=None) -> StreamWriter

    that calls Robot.get_stream_writer(topic, queue_size=queue_size).
    """
    method_name = f"{namespace}_stream_open_{local_name}_writer"

    params = [
        inspect.Parameter(
            "self",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ),
        inspect.Parameter(
            "queue_size",
            inspect.Parameter.KEYWORD_ONLY,
            default=None,
            annotation=int | None,
        ),
    ]

    signature = inspect.Signature(params)

    def api_func(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        self = bound.arguments["self"]
        queue_size = bound.arguments["queue_size"]

        return self.get_stream_writer(topic=topic, queue_size=queue_size)

    api_func.__name__ = method_name
    api_func.__qualname__ = f"Robot.{method_name}"
    api_func.__signature__ = signature
    api_func.__doc__ = f"Open a writer for stream topic {topic!r}."

    return method_name, api_func


def _create_stream_callback_method(
    namespace: str,
    local_name: str,
    topic: str,
):
    """
    Create a Robot method:

        def <namespace>_stream_on_<local_name>(self, callback, queue_size=None) -> StreamSubscription

    which:
        - opens a reader for the given topic
        - starts a background thread dispatching frames to the callback
    """
    method_name = f"{namespace}_stream_on_{local_name}"

    params = [
        inspect.Parameter(
            "self",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ),
        inspect.Parameter(
            "callback",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Callable[[Any], None],
        ),
        inspect.Parameter(
            "queue_size",
            inspect.Parameter.KEYWORD_ONLY,
            default=None,
            annotation=int | None,
        ),
    ]

    signature = inspect.Signature(params)

    def api_func(*args, **kwargs) -> StreamSubscription:
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        self = bound.arguments["self"]
        callback = bound.arguments["callback"]
        queue_size = bound.arguments["queue_size"]

        reader = self.get_stream_reader(topic=topic, queue_size=queue_size)
        return StreamSubscription(reader, callback)

    api_func.__name__ = method_name
    api_func.__qualname__ = f"Robot.{method_name}"
    api_func.__signature__ = signature
    api_func.__doc__ = f"Subscribe to stream topic {topic!r} with a callback."

    return method_name, api_func


# ----------------------------------------------------------------------
# Attach APIs to Robot
# ----------------------------------------------------------------------
def attach_core_apis(Robot_cls, api_specs: Dict[str, Dict[str, Any]]) -> None:
    """
    Attach all RPC and stream APIs defined in QTROBOT_CORE_APIS
    to the given Robot class.

    api_specs shape:

        {
            "rpc": {
                "speech.say": { ... },
                "gesture.play": { ... },
                ...
            },
            "stream": {
                "motors.joints_state": { ... },
                ...
            },
        }
    """
    rpc_specs: Dict[str, Dict[str, Any]] = api_specs.get("rpc", {})
    stream_specs: Dict[str, Dict[str, Any]] = api_specs.get("stream", {})

    # ------------------------------------------------------------------
    # 1) Determine namespaces and attach namespace properties
    # ------------------------------------------------------------------
    namespaces: set[str] = set()

    for api_id in rpc_specs.keys():
        if "." in api_id:
            ns, _ = api_id.split(".", 1)
        else:
            ns = api_id
        namespaces.add(ns)

    for stream_id in stream_specs.keys():
        if "." in stream_id:
            ns, _ = stream_id.split(".", 1)
        else:
            ns = stream_id
        namespaces.add(ns)

    for ns in sorted(namespaces):
        if not hasattr(Robot_cls, ns):
            setattr(Robot_cls, ns, _make_namespace_property(ns))

    # ------------------------------------------------------------------
    # 2) Attach RPC methods: robot.<ns>.<name>() → robot.<ns>_<name>()
    # ------------------------------------------------------------------
    for api_id, spec in rpc_specs.items():
        if "." in api_id:
            namespace, short_name = api_id.split(".", 1)
        else:
            namespace, short_name = api_id, api_id

        method_name = f"{namespace}_{short_name}"
        func = create_rpc_method(api_id, method_name, spec)
        setattr(Robot_cls, method_name, func)

    # ------------------------------------------------------------------
    # 3) Attach stream methods:
    #    - robot.<ns>.stream.open_<local>_reader(...)
    #    - robot.<ns>.stream.open_<local>_writer(...)
    #    - robot.<ns>.stream.on_<local>(callback, ...)
    #
    #    These map to robot methods named:
    #       "<ns>_stream_open_<local>_reader"
    #       "<ns>_stream_open_<local>_writer"
    #       "<ns>_stream_on_<local>"
    # ------------------------------------------------------------------
    for stream_id, spec in stream_specs.items():
        if "." in stream_id:
            namespace, local_name = stream_id.split(".", 1)
        else:
            namespace, local_name = stream_id, stream_id

        topic: str = spec["topic"]
        direction = spec.get("direction")

        # For robot -> SDK streams (direction "out" or None): reader + callback
        if direction in ("out", None):
            mname_reader, fn_reader = _create_stream_reader_method(
                namespace=namespace,
                local_name=local_name,
                topic=topic,
            )
            setattr(Robot_cls, mname_reader, fn_reader)

            mname_cb, fn_cb = _create_stream_callback_method(
                namespace=namespace,
                local_name=local_name,
                topic=topic,
            )
            setattr(Robot_cls, mname_cb, fn_cb)

        # For SDK -> robot streams (direction "in" or None): writer
        if direction in ("in", None):
            mname_writer, fn_writer = _create_stream_writer_method(
                namespace=namespace,
                local_name=local_name,
                topic=topic,
            )
            setattr(Robot_cls, mname_writer, fn_writer)
