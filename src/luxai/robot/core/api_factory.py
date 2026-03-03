# src/luxai/robot/core/api_factory.py
from __future__ import annotations

import inspect
import threading
from typing import Any, Callable, Dict, Set, Type, TYPE_CHECKING

from luxai.magpie.utils.logger import Logger
from luxai.magpie.transport.stream_writer import StreamWriter

from .actions import ActionHandle  # only for type hints / docstrings

from luxai.magpie.frames import * 
from .frames import *
from .typed_stream import TypedStreamReader, TypedStreamWriter

if TYPE_CHECKING:
    from .client import Robot  # for type hints only


FRAME_TYPE_REGISTRY: dict[str, type[Frame]] = {    
    "JointStateFrame": JointStateFrame,
    "JointTrajectoryFrame": JointTrajectoryFrame,
    "JointCommandFrame": JointCommandFrame,
    "LedColorFrame": LedColorFrame,
    "Frame": Frame,
    "BoolFrame": BoolFrame,
    "IntFrame": IntFrame,
    "FloatFrame": FloatFrame,
    "StringFrame": StringFrame,
    "BytesFrame": BytesFrame,
    "DictFrame": DictFrame,
    "ListFrame": ListFrame,
    "AudioFrameRaw": AudioFrameRaw,
    "AudioFrameFlac": AudioFrameFlac,
    "ImageFrameRaw": ImageFrameRaw,
    "ImageFrameCV": ImageFrameCV,
    "ImageFrameJpeg": ImageFrameJpeg,
}

# ---------------------------------------------------------------------------
# Internal helper for stream callbacks
# ---------------------------------------------------------------------------


class _StreamSubscription:
    """
    Handle for a streaming callback subscription.

    Internally:
      - holds a TypedStreamReader
      - runs a background thread that repeatedly calls reader.read()
        and invokes the user callback with each frame.

    Users can call .cancel() to terminate the thread.
    """

    def __init__(self, reader: TypedStreamReader, callback: Callable[[Frame], None]) -> None:
        self._reader = reader
        self._callback = callback
        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._run_loop,
            name="RobotStreamCallback",
            daemon=True,
        )
        self._thread.start()

    @property
    def reader(self) -> TypedStreamReader:
        """Access to the underlying TypedStreamReader (if needed)."""
        return self._reader

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                frame = self._reader.read()                
                if frame is None:
                    continue
                self._callback(frame)
            except Exception as e:  # pragma: no cover - defensive logging
                Logger.debug(f"Robot stream callback raised: {e}")
        self._reader.close()        

    def cancel(self) -> None:
        """Stop the callback thread."""        
        self._stop_event.set()
        # We don't force-join; daemon=True means it won't block process exit.


# ---------------------------------------------------------------------------
# RPC API generation
# ---------------------------------------------------------------------------


def _split_namespace(api_key: str) -> tuple[str | None, str]:
    """
    Split an IDL key like "speech.say" into:
        ("speech", "say")

    If there is no '.', returns (None, api_key).
    """
    if "." in api_key:
        ns, leaf = api_key.split(".", 1)
        return ns, leaf
    return None, api_key


def create_rpc_methods(api_key: str, spec: Dict[str, Any]) -> Dict[str, Callable]:
    """
    Create Robot instance method(s) for an RPC API defined in the IDL.

    api_key example: "gesture.list_files"

    Always generates a synchronous blocking method (e.g. list_files()) that
    calls the RPC directly on the calling thread and returns the unwrapped value.

    Also generates an async variant (e.g. list_files_async()) that returns an
    :class:`ActionHandle` for non-blocking use, when either:
      - ``cancel_service_name`` is not None (default rule), or
      - ``spec["async_variant"]`` is explicitly True.

    The async variant is suppressed when ``spec["async_variant"]`` is False.

    spec keys (simplified):
        - service_name: str  (e.g. "/gesture/file/list")
        - cancel_service_name: Optional[str]
        - params: List[(name, type) or (name, type, default)]
        - response_type: type
        - async_variant: Optional[bool]  (override; None means use default rule)
        - doc: Optional[str]
    """
    service_name: str = spec["service_name"]
    cancel_service_name: str | None = spec.get("cancel_service_name")
    response_type = spec.get("response_type", Any)

    ns, leaf = _split_namespace(api_key)
    if ns:
        method_attr_name = f"{ns}_{leaf}"
        qualname_base = f"Robot.{ns}.{leaf}"
    else:
        method_attr_name = leaf
        qualname_base = f"Robot.{leaf}"

    # Decide whether to generate the async variant.
    # Default rule: generate if cancel_service_name is present.
    # Override: spec["async_variant"] = True/False takes precedence.
    async_variant_override = spec.get("async_variant")
    if async_variant_override is None:
        generate_async = cancel_service_name is not None
    else:
        generate_async = bool(async_variant_override)

    # Build the shared RPC parameter list (reused for both variants).
    rpc_params = []
    for entry in spec.get("params", []):
        if len(entry) == 2:
            pname, ptype = entry
            default = inspect.Parameter.empty
        else:
            pname, ptype, default = entry
        rpc_params.append(
            inspect.Parameter(
                pname,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=ptype,
            )
        )

    doc = spec.get("doc") or f"Auto-generated RPC API for service {service_name}."
    methods: Dict[str, Callable] = {}

    # ------------------------------------------------------------------ #
    # Synchronous variant: blocks on the calling thread, returns value    #
    # ------------------------------------------------------------------ #
    sig_sync = inspect.Signature(
        [inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)] + rpc_params,
        return_annotation=response_type,
    )

    def sync_func(*args, **kwargs):
        bound = sig_sync.bind(*args, **kwargs)
        bound.apply_defaults()
        self_ = bound.arguments["self"]
        rpc_args: Dict[str, Any] = {
            name: value
            for name, value in bound.arguments.items()
            if name != "self" and value is not None
        }
        return self_._call_rpc_sync(service_name, rpc_args)

    sync_func.__name__ = method_attr_name
    sync_func.__qualname__ = qualname_base
    sync_func.__doc__ = doc
    sync_func.__signature__ = sig_sync
    methods[method_attr_name] = sync_func

    # ------------------------------------------------------------------ #
    # Async variant (optional): returns ActionHandle immediately          #
    # ------------------------------------------------------------------ #
    if generate_async:
        async_attr_name = f"{method_attr_name}_async"
        sig_async = inspect.Signature(
            [inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)] + rpc_params,
            return_annotation=ActionHandle,
        )

        def async_func(*args, **kwargs):
            bound = sig_async.bind(*args, **kwargs)
            bound.apply_defaults()
            self_ = bound.arguments["self"]
            rpc_args: Dict[str, Any] = {
                name: value
                for name, value in bound.arguments.items()
                if name != "self" and value is not None
            }
            return self_._start_action(
                service_name=service_name,
                args=rpc_args,
                cancel_service_name=cancel_service_name,
            )

        async_func.__name__ = async_attr_name
        async_func.__qualname__ = f"{qualname_base}_async"
        async_func.__doc__ = doc
        async_func.__signature__ = sig_async
        methods[async_attr_name] = async_func

    return methods


# ---------------------------------------------------------------------------
# Stream API generation
# ---------------------------------------------------------------------------


def create_stream_methods(api_key: str, spec: Dict[str, Any]):
    """
    Create Robot instance methods for a stream API defined in the IDL.

    api_key example: "motors.joints_state"

    spec keys (simplified):
        - direction: "out" (robot -> SDK) or "in" (SDK -> robot)
        - frame_type: Optional[str]
        - topic: str (e.g. "/qt_robot/joints/state")
        - deprecated: bool
        - experimental: bool
        - doc: Optional[str]

    Generated methods are attached to Robot with internal names like:
        - "motors_stream_open_joints_state_reader"
        - "motors_stream_on_joints_state"
        - "motors_stream_open_head_position_writer"

    They are exposed to users via namespace views:
        robot.motors.stream.open_joints_state_reader(...)
        robot.motors.stream.on_joints_state(...)
    """
    topic: str = spec["topic"]
    direction: str | None = spec.get("direction")
    doc: str | None = spec.get("doc")

    ns, leaf = _split_namespace(api_key)
    if ns is None:
        # For streams we expect a namespace like "motors.joints_state".
        ns = "root"  # fallback, but practically you won't use this
    base = leaf  # e.g. "joints_state"

    methods: Dict[str, Callable[..., Any]] = {}

    frame_type_name: str | None = spec.get("frame_type")
    if frame_type_name is not None:
        try:
            frame_cls: Type[Frame] = FRAME_TYPE_REGISTRY[frame_type_name]
        except KeyError:
            raise ValueError(f"Unknown frame_type {frame_type_name!r} in spec for {api_key!r}")
    else:
        frame_cls = Frame  # or some default like DictFrame

    # ---- Outgoing from robot -> SDK: reader + callback ----
    if direction in ("out", None):
        # 1) open_<base>_reader(queue_size=None) -> TypedStreamReader
        reader_attr_name = f"{ns}_stream_open_{base}_reader"

        def open_reader(
            self,
            queue_size: int | None = None,
            _frame_cls: type[Frame] = frame_cls,  # bind via default arg!
        ) -> TypedStreamReader[Frame]:
            """
            Open a TypedStreamReader for this stream.

            Exposed as:
                robot.<ns>.stream.open_<base>_reader(queue_size=None)
            """
            return self.get_stream_reader(topic=topic, queue_size=queue_size, frame_type=_frame_cls)

        open_reader.__name__ = reader_attr_name
        open_reader.__qualname__ = f"Robot.{ns}.stream.open_{base}_reader"
        open_reader.__doc__ = doc or f"Open a reader for stream topic {topic!r}."
        methods[reader_attr_name] = open_reader

        # 2) on_<base>(callback, queue_size=None) -> _StreamSubscription
        on_attr_name = f"{ns}_stream_on_{base}"

        def on_stream(
            self,
            callback: Callable[[Frame], None],  # type-wise: Frame
            queue_size: int | None = None,
            _frame_cls: type[Frame] = frame_cls,
        ) -> _StreamSubscription:
            """
            Subscribe to this stream with a callback.

            Exposed as:
                robot.<ns>.stream.on_<base>(callback, queue_size=None)

            Returns a _StreamSubscription handle; call .cancel() to terminate.
            """            
            reader = self.get_stream_reader(
                topic=topic,
                queue_size=queue_size,
                frame_type=_frame_cls,
            )          
            return _StreamSubscription(reader, callback)

        on_stream.__name__ = on_attr_name
        on_stream.__qualname__ = f"Robot.{ns}.stream.on_{base}"
        on_stream.__doc__ = (
            doc or f"Attach a callback to stream topic {topic!r}."
        )
        methods[on_attr_name] = on_stream

    # ---- Incoming to robot (SDK -> robot): writer ----
    if direction in ("in", None):
        writer_attr_name = f"{ns}_stream_open_{base}_writer"

        def open_writer(self, queue_size: int | None = None) -> TypedStreamWriter[Frame]:
            """
            Open a TypedStreamWriter for this stream.

            Exposed as:
                robot.<ns>.stream.open_<base>_writer(queue_size=None)
            """
            return self.get_stream_writer(topic=topic, queue_size=queue_size)

        open_writer.__name__ = writer_attr_name
        open_writer.__qualname__ = f"Robot.{ns}.stream.open_{base}_writer"
        open_writer.__doc__ = doc or f"Open a writer for stream topic {topic!r}."
        methods[writer_attr_name] = open_writer

    return methods


# ---------------------------------------------------------------------------
# Namespace views (robot.speech, robot.motors.stream, etc.)
# ---------------------------------------------------------------------------


class _NamespaceView:
    """
    View object for a top-level namespace, e.g. robot.speech, robot.motors.

    It forwards attribute access to Robot methods named "<ns>_<attr>".

    Example:
        - api_key "speech.say" -> Robot.speech_say(...)
        - user calls robot.speech.say(...)
          -> _NamespaceView.__getattr__("say")
          -> getattr(robot, "speech_say")
    """

    def __init__(self, robot: "Robot", prefix: str) -> None:
        self._robot = robot
        self._prefix = prefix

    def __getattr__(self, name: str) -> Any:
        attr_name = f"{self._prefix}_{name}"
        return getattr(self._robot, attr_name)

    @property
    def stream(self) -> "_StreamNamespaceView":
        """
        Nested namespace for streams under this group, e.g. robot.motors.stream.
        """
        return _StreamNamespaceView(self._robot, self._prefix)


class _StreamNamespaceView:
    """
    View object for stream APIs under a namespace, e.g. robot.motors.stream.

    It forwards attribute access to Robot methods named
    "<ns>_stream_<attr>".

    Example:
        - IDL "motors.joints_state" (direction="out")
        - internal Robot method: "motors_stream_open_joints_state_reader"
        - user calls: robot.motors.stream.open_joints_state_reader(...)
          -> _StreamNamespaceView.__getattr__("open_joints_state_reader")
          -> getattr(robot, "motors_stream_open_joints_state_reader")
    """

    def __init__(self, robot: "Robot", prefix: str) -> None:
        self._robot = robot
        self._prefix = prefix

    def __getattr__(self, name: str) -> Any:
        attr_name = f"{self._prefix}_stream_{name}"
        return getattr(self._robot, attr_name)


def _attach_namespace_properties(Robot_cls: type["Robot"], namespaces: Set[str]) -> None:
    """
    Attach properties like 'speech', 'motors', 'audio' to Robot:

        @property
        def speech(self) -> _NamespaceView:
            return _NamespaceView(self, "speech")

    Also used for stream APIs via .stream on the view.
    """

    def make_prop(ns: str):
        def prop(self: "Robot") -> _NamespaceView:
            return _NamespaceView(self, ns)

        prop.__doc__ = f"Namespace view for '{ns}' APIs."
        return property(prop)

    for ns in namespaces:
        # Avoid overriding existing attributes
        if hasattr(Robot_cls, ns):
            continue
        setattr(Robot_cls, ns, make_prop(ns))


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def attach_core_apis(Robot_cls: type["Robot"], api_specs: Dict[str, Dict[str, Any]]) -> None:
    """
    Attach all RPC + stream APIs (and namespace views) to the Robot class.

    api_specs structure:

        {
            "rpc": {
                "speech.say": { ... },
                "gesture.play": { ... },
                ...
            },
            "stream": {
                "motors.joints_state": { ... },
                "motors.head_position": { ... },
                ...
            },
        }
    """
    rpc_specs: Dict[str, Dict[str, Any]] = api_specs.get("rpc", {})
    stream_specs: Dict[str, Dict[str, Any]] = api_specs.get("stream", {})

    namespaces: Set[str] = set()

    # ---- Attach RPC methods ----
    for api_key, spec in rpc_specs.items():
        ns, _ = _split_namespace(api_key)
        if ns:
            namespaces.add(ns)

        for attr_name, func in create_rpc_methods(api_key, spec).items():
            setattr(Robot_cls, attr_name, func)

    # ---- Attach stream methods ----
    for api_key, spec in stream_specs.items():
        ns, _ = _split_namespace(api_key)
        if ns:
            namespaces.add(ns)

        methods = create_stream_methods(api_key, spec)
        for attr_name, func in methods.items():
            setattr(Robot_cls, attr_name, func)

    # ---- Attach namespace properties on Robot (speech, motors, audio, ...) ----
    if namespaces:
        _attach_namespace_properties(Robot_cls, namespaces)
