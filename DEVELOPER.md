# Developer & Architecture Guide

This document covers the internal design of the `luxai-robot` SDK — for contributors, for adding new APIs, and as a personal design reference.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Repository Layout](#repository-layout)
- [Core Architecture](#core-architecture)
  - [Startup and API Attachment](#startup-and-api-attachment)
  - [Robot Handshake and Route Building](#robot-handshake-and-route-building)
  - [Transport Abstraction](#transport-abstraction)
  - [Namespace Views](#namespace-views)
  - [RPC Execution: sync vs async](#rpc-execution-sync-vs-async)
  - [ActionHandle Internals](#actionhandle-internals)
  - [Stream Execution](#stream-execution)
- [IDL Reference](#idl-reference)
  - [RPC spec fields](#rpc-spec-fields)
  - [Stream spec fields](#stream-spec-fields)
- [How to Add a New Core API](#how-to-add-a-new-core-api)
- [Stub Generator](#stub-generator)
- [Plugin System](#plugin-system)
  - [PLUGIN_REGISTRY](#plugin_registry)
  - [RobotPlugin base class](#robotplugin-base-class)
  - [Local plugin pattern (ASRAzurePlugin)](#local-plugin-pattern-asrazureplugin)
  - [Remote plugin pattern (RemotePlugin)](#remote-plugin-pattern-remoteplugin)
  - [How to Add a New Local Plugin](#how-to-add-a-new-local-plugin)
  - [How to Add a New Remote Plugin](#how-to-add-a-new-remote-plugin)
- [Frame Types](#frame-types)
- [Design Decisions and Rationale](#design-decisions-and-rationale)
- [Development Setup](#development-setup)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│  User code                                                       │
│                                                                  │
│  robot = Robot.connect_zmq(endpoint="tcp://...")                 │
│  robot.tts.say_text("acapela", "Hello")        # sync RPC       │
│  h = robot.tts.say_text_async("acapela", "Hi") # async RPC      │
│  reader = robot.microphone.stream.open_int_audio_ch0_reader()   │
└──────────────┬───────────────────────────────────────────────────┘
               │  robot.tts  →  _NamespaceView("tts")
               │  .say_text  →  getattr(robot, "tts_say_text")
               ▼
┌──────────────────────────────────────────────────────────────────┐
│  Robot class  (client.py)                                        │
│                                                                  │
│  Methods auto-attached at import time from IDL:                  │
│    tts_say_text(...)         ← create_rpc_methods()             │
│    tts_say_text_async(...)   ← create_rpc_methods()             │
│    microphone_stream_open_int_audio_ch0_reader(...)              │
│    ...                                                           │
│                                                                  │
│  Core methods (manual):                                          │
│    _call_rpc_sync()   – blocks, returns unwrapped value          │
│    _start_action()    – spawns thread, returns ActionHandle      │
│    get_stream_reader() / get_stream_writer()                     │
│    _handshake_with_robot()  – builds _rpc_routes, _stream_routes │
└──────────────┬───────────────────────────────────────────────────┘
               │  rpc_call(service_name, args, timeout)
               ▼
┌──────────────────────────────────────────────────────────────────┐
│  Transport  (transport/transport.py — Protocol)                  │
│                                                                  │
│  ZmqTransport   — ZMQ/Magpie over TCP (network robot)           │
│  LocalTransport — ZMQ inproc:// (local plugins, same process)   │
│                                                                  │
│  get_requester(service_name, transports_meta)  → RpcRequester   │
│  get_stream_reader(topic, transports_meta)     → StreamReader    │
│  get_stream_writer(topic, transports_meta)     → StreamWriter    │
└──────────────┬───────────────────────────────────────────────────┘
               │  ZMQ request/reply  or  inproc streaming
               ▼
┌──────────────────────────────────────────────────────────────────┐
│  Robot firmware  (on the robot)                                  │
│  — OR —                                                          │
│  Local plugin node  (in-process, e.g. ASRAzureNode)             │
└──────────────────────────────────────────────────────────────────┘
```

**Key design principle:** `Robot` is transport-agnostic. It never references ZMQ, endpoints, or wire protocols directly. It receives routing metadata from the robot's `SYSTEM_DESCRIBE_SERVICE` handshake and passes it to whichever `Transport` implementation is active.

---

## Repository Layout

```
robot-sdk-python/
│
├── src/luxai/robot/
│   │
│   ├── __init__.py                    # package version (__version__)
│   │
│   └── core/
│       ├── client.py                  # Robot class — main entry point
│       ├── client_base.pyi            # Hand-written stub base (manual Robot methods)
│       ├── client.pyi                 # AUTO-GENERATED stub (do not edit by hand)
│       │
│       ├── actions.py                 # ActionHandle, ActionError, wait_all/any_actions
│       ├── api_factory.py             # IDL → Robot method codegen + namespace views
│       ├── config.py                  # SDK_VERSION, QTROBOT_APIS, SYSTEM_DESCRIBE_SERVICE
│       ├── typed_stream.py            # TypedStreamReader[F], TypedStreamWriter[F]
│       │
│       ├── idl/
│       │   ├── api.py                 # Merges api_core + api_plugins into QTROBOT_APIS
│       │   ├── api_core.py            # Core robot API definitions (IDL)
│       │   ├── api_core_doc.py        # Docstrings for core APIs (keyed dict)
│       │   └── api_plugins.py        # Plugin API definitions (IDL — camera, ASR, ...)
│       │
│       ├── transport/
│       │   ├── transport.py           # Transport Protocol + SupportsPreallocation
│       │   ├── zmq_transport.py       # ZMQ/Magpie implementation
│       │   ├── local_transport.py     # inproc:// implementation (for local plugins)
│       │   ├── mqtt_transport.py      # MQTT implementation (broker-based, shared connection)
│       │   ├── mqtt_options.py        # Re-exports MqttOptions and related classes
│       │   ├── webrtc_transport.py    # WebRTC implementation (P2P, stores signaling_params)
│       │   └── __init__.py
│       │
│       ├── plugins/
│       │   ├── __init__.py            # PLUGIN_REGISTRY + guarded imports
│       │   ├── robot_plugin.py        # RobotPlugin ABC
│       │   ├── asr_azure_plugin.py    # Local plugin (inproc + magpie node)
│       │   └── remote_plugin.py      # Remote plugin base + RealsenseDriverPlugin
│       │
│       └── frames/
│           ├── __init__.py
│           ├── joint_state.py         # JointStateFrame, JointCommandFrame
│           ├── joint_trajectory.py    # JointTrajectoryFrame
│           └── led.py                 # LedColorFrame
│
├── scrtipts/                          # (note: typo in directory name — intentional legacy)
│   └── gen_robot_stubs.py            # Stub generator: IDL → client.pyi
│
└── examples/                          # Ready-to-run example scripts
```

---

## Core Architecture

### Startup and API Attachment

At the very bottom of [client.py](src/luxai/robot/core/client.py), after the `Robot` class is fully defined, there is one module-level call:

```python
from .api_factory import attach_core_apis
attach_core_apis(Robot, QTROBOT_APIS)
```

`QTROBOT_APIS` is loaded from [idl/api.py](src/luxai/robot/core/idl/api.py), which simply merges the core IDL and plugin IDL dicts:

```python
QTROBOT_APIS = {
    "rpc":    {**QTROBOT_CORE_APIS["rpc"],    **QTROBOT_PLUGINS_APIS["rpc"]},
    "stream": {**QTROBOT_CORE_APIS["stream"], **QTROBOT_PLUGINS_APIS["stream"]},
}
```

`attach_core_apis` does three things:

1. Iterates `QTROBOT_APIS["rpc"]` → calls `create_rpc_methods(api_key, spec)` for each → `setattr(Robot, attr_name, func)` for each returned method.
2. Iterates `QTROBOT_APIS["stream"]` → calls `create_stream_methods(api_key, spec)` for each → `setattr(Robot, attr_name, func)`.
3. Collects all encountered namespace prefixes (e.g. `"tts"`, `"face"`) → calls `_attach_namespace_properties(Robot, namespaces)` to install `@property` descriptors.

This all happens **once at import time**, so the `Robot` class is fully populated before any user code runs.

---

### Robot Handshake and Route Building

When `Robot.__init__` is called (via `Robot.connect_zmq`), it calls `_handshake_with_robot()`, which:

1. Issues a raw RPC call to `SYSTEM_DESCRIBE_SERVICE` (`"/robot/system/describe"`) via the transport.
2. The robot responds with a `SYSTEM_DESCRIPTION` payload containing its identity (`robot_type`, `robot_serial`, `sdk_version`, SDK version range) and a routing table for every RPC and stream it supports.
3. `_apply_system_description()` parses this payload and populates:
   - `robot._rpc_routes`:    `service_name → (Transport, route_meta)`
   - `robot._stream_routes`: `topic → (Transport, route_meta)`

Every subsequent `rpc_call(service_name, ...)` looks up the service in `_rpc_routes` to find which Transport instance and which wire-level transport metadata (`transports_meta`) to use.

**Why this matters:** The SDK never hardcodes endpoints. The robot tells the SDK exactly how to reach each service. Plugins work the same way — they register additional entries into `_rpc_routes` and `_stream_routes` after connecting.

**Version compatibility:** `_apply_system_description` compares `SDK_VERSION` against the robot's `min_sdk` / `max_sdk` fields and logs a warning if out of range.

---

### Transport Abstraction

[`Transport`](src/luxai/robot/core/transport/transport.py) is a `@runtime_checkable Protocol` with three methods:

```python
def get_requester(self, service_name, transports) -> RpcRequester: ...
def get_stream_reader(self, topic, transports, queue_size) -> StreamReader: ...
def get_stream_writer(self, topic, transports, queue_size) -> StreamWriter: ...
def close(self) -> None: ...
```

`RpcRequester`, `StreamReader`, and `StreamWriter` are magpie primitives. `Robot` only ever calls these three methods and never casts the transport to a concrete type.

**`SupportsPreallocation`** is an optional second Protocol. If the transport implements it, `Robot.__init__` calls `preallocate_requesters(rpc_routes)` right after the handshake — this lets `ZmqTransport` pre-create all ZMQ requester sockets upfront instead of lazily, avoiding first-call latency.

> **User-facing plugin guide:** See [PLUGIN.md](PLUGIN.md) for practical usage, examples, and architecture diagrams.

**`ZmqTransport`** — connects to the robot over TCP. Accepts either a direct `endpoint` or a `node_id` for UDP/multicast discovery. Implements `SupportsPreallocation`.

**`LocalTransport`** — connects over ZMQ `inproc://` within the same process. Used exclusively by local plugins (e.g., `ASRAzurePlugin` starts a local magpie node on `inproc://asr-azure-rpc`).

**`MqttTransport`** — connects via an MQTT broker. The `robot_id` (or plugin `node_id`) acts as the topic namespace prefix. Lazily creates `MqttRpcRequester` instances per-topic. Key implementation details:
- `get_requester(service_name, transports=None)` — when `transports is None` (descriptor call), uses `robot_id` as the topic; otherwise reads `transports["mqtt"]["topic"]`.
- `owns_connection: bool` — when `False` (plugin transports), `close()` skips `connection.disconnect()` so the shared broker connection stays alive. Set to `True` (default) for the main robot transport.
- `connection` property — exposes the underlying `MqttConnection` so `enable_plugin_mqtt()` can share it.

**`WebRTCTransport`** — connects via a P2P WebRTC peer connection. Signaling (SDP + ICE) is done through a pluggable channel (MQTT or ZMQ). Key implementation detail:
- `_signaling_params: dict` — stores the signaling configuration (`type`, `broker_url`/`endpoint`, `mqtt_options`, `webrtc_options`, `reconnect`, `connect_timeout`) so that `enable_plugin_webrtc_mqtt/zmq()` can create plugin peers with the same settings without requiring the user to repeat them.

**Adding a new transport:** Implement the `Transport` Protocol (and optionally `SupportsPreallocation`), then pass an instance to `Robot(transport=MyTransport(...))` directly.

---

### Namespace Views

The IDL key `"tts.say_text"` maps to an internal Robot method named `tts_say_text`. Users call `robot.tts.say_text(...)`.

The indirection is handled by two view classes in [api_factory.py](src/luxai/robot/core/api_factory.py):

```
robot.tts
  → @property tts → _NamespaceView(robot, "tts")
  .say_text(...)
  → _NamespaceView.__getattr__("say_text")
  → getattr(robot, "tts_say_text")
  → robot.tts_say_text(...)   ← the generated function

robot.tts.stream.on_int_audio_ch0(callback)
  → _NamespaceView.stream     → _StreamNamespaceView(robot, "tts")
  → __getattr__("on_int_audio_ch0")
  → getattr(robot, "tts_stream_on_int_audio_ch0")
```

`_attach_namespace_properties` installs one `@property` per namespace on the `Robot` class, each returning a `_NamespaceView` for that prefix. `_StreamNamespaceView` is a nested view returned by `_NamespaceView.stream`.

**Important for `_async` methods:** `robot.tts.say_text_async(...)` resolves to `getattr(robot, "tts_say_text_async")`. The `_` in `_async` is part of the method name suffix, not a separate prefix — so the namespace lookup works correctly.

---

### RPC Execution: sync vs async

Two internal Robot methods handle all RPC calls:

**`_call_rpc_sync(service_name, args, timeout)`** — used by every sync method:
- Calls `self.rpc_call(...)` on the **calling thread** — no thread is spawned.
- Checks `raw["status"]`; raises `ActionError` on failure.
- Returns `raw["response"]` directly as the method return value.

**`_start_action(service_name, args, *, cancel_service_name, timeout)`** — used by every `_async` method:
- Creates an `ActionHandle` and returns it immediately.
- The `ActionHandle.__init__` spawns a daemon thread that calls `rpc_call(...)`.
- The calling thread is never blocked.

**Rule for generating `_async`:**
```python
async_variant_override = spec.get("async_variant")   # None, True, or False
if async_variant_override is None:
    generate_async = cancel_service_name is not None  # default rule
else:
    generate_async = bool(async_variant_override)     # explicit override
```

Use `"async_variant": True` in an IDL spec to force an async variant even when there is no cancel service. Use `"async_variant": False` to suppress it even when there is one.

---

### ActionHandle Internals

Defined in [actions.py](src/luxai/robot/core/actions.py).

```
ActionHandle.__init__
  ├─ stores service_name, args, timeout, cancel_service_name, rpc_call ref
  ├─ creates threading.Event() _done_event
  └─ spawns daemon thread → _run()

_run()
  ├─ calls rpc_call(service_name, args, timeout)   ← blocks here
  ├─ on success: stores _result = raw["response"]
  ├─ on failure: stores _error = ActionError(...)
  └─ _done_event.set() → _fire_callbacks()

cancel()
  ├─ if cancel_service_name is None: no-op
  └─ calls rpc_call(cancel_service_name, {}, timeout)
     ├─ on success: sets _cancelled = True
     └─ note: does NOT forcibly kill _run() thread;
        the underlying RPC returns when the robot honours the stop command
```

**Thread safety:** `_callbacks` list is protected by `_lock`. `add_done_callback` either appends to the list (if not done) or invokes the callback immediately (if already done), handling the race without a separate lock.

**Exception hierarchy:**
```
Exception
└── ActionError                  # robot reported failure, or RPC transport error
    └── ActionCancelledError     # result() called after cancel()
```

---

### Stream Execution

For **outbound** streams (robot → SDK, `direction: "out"`), `create_stream_methods` generates two methods per IDL entry:

- `open_<name>_reader(queue_size)` → `TypedStreamReader[FrameType]`
- `on_<name>(callback, queue_size)` → `_StreamSubscription`

`_StreamSubscription` wraps a `TypedStreamReader` and runs a background daemon thread that repeatedly calls `reader.read()` and invokes the user callback.

For **inbound** streams (SDK → robot, `direction: "in"`), only a writer is generated:

- `open_<name>_writer(queue_size)` → `TypedStreamWriter[FrameType]`

`TypedStreamReader[F]` and `TypedStreamWriter[F]` are thin wrappers over the magpie `StreamReader` / `StreamWriter` that enforce the correct frame type on `read()` / `write()`.

---

## IDL Reference

All API definitions live in [idl/api_core.py](src/luxai/robot/core/idl/api_core.py) and [idl/api_plugins.py](src/luxai/robot/core/idl/api_plugins.py). The two are merged at import time in [idl/api.py](src/luxai/robot/core/idl/api.py).

### RPC spec fields

```python
"namespace.method_name": {

    # ── Required ────────────────────────────────────────────────────────
    "service_name": str,
    # The wire-level service name sent to the robot, e.g. "/tts/engine/say/text".
    # Must match exactly what the robot's firmware exposes.

    "params": list,
    # List of parameter descriptors. Each entry is one of:
    #   (name: str, type: type)                  → required param
    #   (name: str, type: type, default: Any)    → optional param
    # Params with default=None get type annotation `type | None`.
    # None-valued params are stripped from the RPC args dict before sending.

    # ── Cancel / async control ──────────────────────────────────────────
    "cancel_service_name": str | None,
    # Wire-level service name for cancellation (e.g. "/tts/engine/cancel").
    # Setting this to a non-None value is the primary signal to generate
    # the _async variant. Set to None for quick non-cancellable RPCs.

    "async_variant": bool,  # optional, default: not present (= None)
    # Explicit override for async variant generation.
    #   True  → always generate _async, even without cancel_service_name
    #   False → never generate _async, even if cancel_service_name is set
    #   (absent) → use default rule: generate _async iff cancel_service_name is not None

    # ── Return type ─────────────────────────────────────────────────────
    "response_type": type,
    # Python type of the unwrapped response value:
    #   str, int, float, bool, list, dict, type(None)
    # Used for type stub generation and documentation.

    # ── Documentation ───────────────────────────────────────────────────
    "doc": str,
    # Docstring for both the sync and async variants. For core APIs,
    # the actual string is stored in api_core_doc.py (keyed by api_id)
    # and referenced here via QTROBOT_CORE_API_DOCS.get("namespace.method", "").

    # ── Metadata (informational, not used at runtime) ────────────────────
    "robots": list[str],
    # e.g. ["qtrobot-v3"]. Not enforced at runtime; used for documentation
    # and potential future per-model filtering.

    # Plugin-only fields (api_plugins.py):
    "provider": str,          # e.g. "asr-azure", "realsense-driver"
    "local": bool,            # True if plugin runs in-process (LocalTransport)
    "install_hint": str,      # e.g. "pip install luxai-robot[asr-azure]"
    "since": str,             # version string when this API was added
    "deprecated": bool,
    "deprecated_message": str | None,
}
```

### Stream spec fields

```python
"namespace.stream_name": {

    # ── Required ────────────────────────────────────────────────────────
    "topic": str,
    # Wire-level topic, e.g. "/mic/int/audio/ch0/stream:o".
    # The ":o" / ":i" suffix is a convention — the firmware uses this exact string.

    "direction": "out" | "in",
    # "out" → robot writes, SDK reads → generates reader + callback
    # "in"  → SDK writes, robot reads → generates writer

    # ── Frame type ──────────────────────────────────────────────────────
    "frame_type": str,
    # String key into FRAME_TYPE_REGISTRY, e.g. "AudioFrameRaw", "JointStateFrame".
    # Controls what TypedStreamReader[T] / TypedStreamWriter[T] is returned,
    # and what type annotation appears in the stub.

    # ── Delivery semantics (informational) ──────────────────────────────
    "delivery": "reliable" | "latest",
    # "reliable" → queued, no drops (good for audio, commands)
    # "latest"   → always get most recent frame, older ones dropped (good for state, video)
    # Not enforced by the SDK — the firmware and magpie transport honour this.

    "queue_size": int,
    # Default queue depth. Users can override via open_*_reader(queue_size=N).

    # ── Documentation ───────────────────────────────────────────────────
    "doc": str,

    # ── Metadata ────────────────────────────────────────────────────────
    "robots": list[str],
    "deprecated": bool,
    "experimental": bool,

    # Plugin-only:
    "provider": str,
    "local": bool,
    "install_hint": str,
}
```

---

## How to Add a New Core API

**Example: add `robot.tts.get_word_timings(engine)` (no cancel, sync only).**

### 1. Add the spec to `api_core.py`

```python
"tts.get_word_timings": {
    "service_name": "/tts/engine/word_timings/get",
    "cancel_service_name": None,
    "params": [
        ("engine", str),
    ],
    "response_type": list,
    "robots": ["qtrobot-v3"],
    "doc": QTROBOT_CORE_API_DOCS.get("tts.get_word_timings", ""),
},
```

### 2. Add the docstring to `api_core_doc.py`

```python
"tts.get_word_timings": (
    "Return word-level timing information for the last utterance.\n"
    "\n"
    "Args:\n"
    "    engine (str): Engine ID.\n"
    "\n"
    "Returns:\n"
    "    list: List of dicts with 'word', 'start_ms', 'end_ms' fields.\n"
    "\n"
    "Example:\n"
    "    timings = robot.tts.get_word_timings('acapela')\n"
),
```

### 3. Regenerate the type stub

```bash
cd robot-sdk-python
python scrtipts/gen_robot_stubs.py
```

This reads the IDL and overwrites `src/luxai/robot/core/client.pyi`.

### 4. Verify

```python
from luxai.robot.core import Robot
# Inspect the generated method
import inspect
print(inspect.signature(Robot.tts_get_word_timings))
```

That's it. The method is available as `robot.tts.get_word_timings(engine)` as soon as the module is imported.

---

**Example: add `robot.tts.say_text_streamed(engine, text)` (cancellable, generates `_async` too).**

Just set `cancel_service_name` to the correct service string:

```python
"tts.say_text_streamed": {
    "service_name": "/tts/engine/say/streamed",
    "cancel_service_name": "/tts/engine/cancel",
    "params": [("engine", str), ("text", str)],
    "response_type": type(None),
    ...
},
```

Both `robot.tts.say_text_streamed(...)` (sync) and `robot.tts.say_text_streamed_async(...)` (async) are generated automatically.

---

## Stub Generator

The type stub for `Robot` is split into two files:

| File | Role |
|---|---|
| [client_base.pyi](src/luxai/robot/core/client_base.pyi) | **Hand-written.** Contains manual `Robot` method signatures (connect, close, plugin methods, stream/rpc helpers). Edit this when adding a new hand-written Robot method. |
| [client.pyi](src/luxai/robot/core/client.pyi) | **Auto-generated.** Never edit by hand — it will be overwritten. |

The generator lives at [scrtipts/gen_robot_stubs.py](scrtipts/gen_robot_stubs.py) *(note: directory name has a typo — legacy)*.

**How it works:**

1. Reads `client_base.pyi` as a template.
2. Locates the marker `# --- AUTO-GENERATED ROBOT NAMESPACES ---` inside the `Robot` class.
3. Replaces the marker with `@property` stubs for every namespace (e.g. `def tts(self) -> TtsAPI: ...`).
4. Appends generated `*StreamAPI` and `*API` classes for every namespace, derived from the IDL.

**When to re-run it:**
- After adding or removing any RPC or stream entry in `api_core.py` or `api_plugins.py`.
- After adding a hand-written method to `client_base.pyi`.

```bash
python scrtipts/gen_robot_stubs.py
# Output: Wrote stub: .../src/luxai/robot/core/client.pyi
```

**`_render_param` rules:**
- `(name, type)` → `name: type`
- `(name, type, None)` → `name: type | None = None`
- `(name, type, <other>)` → `name: type = ...`

---

## Plugin System

### PLUGIN_REGISTRY

[plugins/\_\_init\_\_.py](src/luxai/robot/core/plugins/__init__.py) defines the global registry:

```python
PLUGIN_REGISTRY: Dict[str, Optional[Type[RobotPlugin]]] = {}
```

Each plugin is registered with a guarded import so that missing optional dependencies never break the SDK:

```python
try:
    from .asr_azure_plugin import ASRAzurePlugin
    PLUGIN_REGISTRY["asr-azure"] = ASRAzurePlugin
except ImportError:
    PLUGIN_REGISTRY["asr-azure"] = None   # installed but unavailable
```

`Robot.enable_plugin(name, transport)` looks up the name here. If the value is `None`, it raises a `RuntimeError` with an install hint.

---

### RobotPlugin base class

```python
class RobotPlugin(ABC):
    def __init__(self, plugin_name: str): ...

    @abstractmethod
    def start(self, robot: Robot, transport: Transport) -> None:
        """Called when plugin is enabled. Start nodes, register routes."""

    @abstractmethod
    def stop(self) -> None:
        """Called on disable or robot.close(). Stop threads, release resources."""
```

Every plugin must implement `start` and `stop`. The `Robot` calls `stop()` for all active plugins inside `Robot.close()`.

---

### Local plugin pattern (ASRAzurePlugin)

A **local plugin** runs a magpie node inside the same Python process, communicating over ZMQ `inproc://` sockets.

**`start(robot, transport)`:**
1. Creates a magpie `ZMQRpcResponder` bound to `inproc://<plugin>-rpc`.
2. Creates a magpie `ZmqStreamWriter` bound to `inproc://<plugin>-stream`.
3. Starts the plugin's processing node (e.g. `ASRAzureNode`) using those sockets.
4. Calls `robot._setup_rpc_routes(transport, rpc)` — adds the plugin's service names to `robot._rpc_routes`.
5. Calls `robot._setup_stream_routes(transport, stream)` — adds the plugin's topics to `robot._stream_routes`.

After `start`, `robot.asr.configure_azure(...)` resolves through `_rpc_routes` to the inproc endpoint, exactly like any other RPC.

**`stop()`:**
- Closes the transport.
- Terminates the magpie node.

---

### Remote plugin pattern (RemotePlugin)

A **remote plugin** runs on a separate host (or process) and exposes its interface over a transport. `RemotePlugin` is a base class for these:

**`start(robot, transport)`:**
1. Issues a system-describe RPC (empty args) to the plugin host via the transport.
2. The plugin host responds with its own `SYSTEM_DESCRIPTION` (rpc + stream routing tables).
3. Calls `robot._setup_rpc_routes(transport, rpcs)` and `robot._setup_stream_routes(transport, streams)`.

This is the same mechanism as the main robot handshake — plugins that run remotely are self-describing. **This is why any transport works:** `RemotePlugin.start()` only uses `transport.get_requester()` and `transport.get_stream_reader/writer()` — the same `Transport` Protocol — regardless of whether the underlying wire is ZMQ, MQTT, or WebRTC.

`RealsenseDriverPlugin` is a zero-body subclass of `RemotePlugin`:

```python
class RealsenseDriverPlugin(RemotePlugin):
    def __init__(self):
        super().__init__(plugin_name="realsense-driver")
```

The name string `"realsense-driver"` is used both as the PLUGIN_REGISTRY key and as the service name for the initial describe call.

---

### Plugin transport ownership

Each `enable_plugin_*()` method creates a transport for the plugin and passes it to `plugin.start(robot, transport)`. The plugin stores the transport and closes it in `stop()`.

**Connection sharing (MQTT):** `enable_plugin_mqtt()` creates a new `MqttTransport` that shares the robot's `MqttConnection` but with `owns_connection=False`. This means `transport.close()` releases the plugin's requesters and readers but does **not** disconnect the broker — only the main robot transport (with `owns_connection=True`) does that.

**Independent connections (WebRTC):** `enable_plugin_webrtc_mqtt/zmq()` creates a fully independent `WebRTCConnection` and `WebRTCTransport` for the plugin. Each plugin peer has its own data channel and media tracks — no conflict with the robot peer or other plugin peers. The plugin transport always owns its connection.

**`_signaling_params` propagation:** When `connect_webrtc_mqtt()` creates the robot's transport, it stores the full signaling configuration in `WebRTCTransport._signaling_params`. When `enable_plugin_webrtc_mqtt()` is called without explicit parameters, it reads these stored params to set up the plugin peer with the same broker, options, and timeout — so the common case (same gateway, same broker) requires zero extra configuration.

---

### How to Add a New Remote Plugin (MQTT/WebRTC)

Adding MQTT or WebRTC support to an existing plugin requires **no changes** to the plugin class. `RemotePlugin.start()` is transport-agnostic. The only thing that changes is the `enable_plugin_*()` call:

```python
# ZMQ — existing
robot.enable_plugin_zmq("realsense-driver", endpoint="tcp://192.168.1.150:50655")

# MQTT — same plugin class, different transport
robot.enable_plugin_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")

# WebRTC — same plugin class, different transport
robot.enable_plugin_webrtc_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")
```

The plugin class (`RealsenseDriverPlugin`) does not need to know or care which transport it receives.

---

### How to Add a New Local Plugin

**Scenario:** Add a `"text-classifier"` plugin that runs a local ML model and exposes a `/text-classifier/classify` RPC.

**Step 1 — Create the plugin class** in `plugins/`:

```python
# src/luxai/robot/core/plugins/text_classifier_plugin.py
from luxai.magpie.transport import ZMQRpcResponder
from luxai.robot.core.transport import Transport
from .robot_plugin import RobotPlugin
from ..somewhere import TextClassifierNode   # your processing node

class TextClassifierPlugin(RobotPlugin):

    def __init__(self):
        super().__init__(plugin_name="text-classifier")
        self._node = None
        self._transport = None

    def start(self, robot, transport: Transport) -> None:
        self._transport = transport
        responder = ZMQRpcResponder("inproc://text-classifier-rpc", bind=True)
        self._node = TextClassifierNode(responder=responder)

        rpc = {
            "/text-classifier/classify": {
                "transports": {"zmq": {"endpoint": "inproc://text-classifier-rpc"}}
            }
        }
        robot._setup_rpc_routes(transport, rpc)

    def stop(self) -> None:
        if self._transport:
            self._transport.close()
            self._transport = None
        if self._node:
            self._node.terminate()
            self._node = None
```

**Step 2 — Register it** in `plugins/__init__.py`:

```python
try:
    from .text_classifier_plugin import TextClassifierPlugin
    PLUGIN_REGISTRY["text-classifier"] = TextClassifierPlugin
except ImportError:
    PLUGIN_REGISTRY["text-classifier"] = None
```

**Step 3 — Add API definitions** to `api_plugins.py`:

```python
"classifier.classify": {
    "service_name": "/text-classifier/classify",
    "cancel_service_name": None,
    "params": [("text", str)],
    "response_type": dict,
    "local": True,
    "provider": "text-classifier",
    "robots": ["qtrobot-v3"],
    "doc": "Classify text. Returns {'label': str, 'confidence': float}.",
},
```

**Step 4 — Regenerate stubs:**

```bash
python scrtipts/gen_robot_stubs.py
```

**Step 5 — Use it:**

```python
robot.enable_plugin_local("text-classifier")
result = robot.classifier.classify("Hello world!")
```

---

### How to Add a New Remote Plugin

**Scenario:** Add a `"lidar-driver"` that runs on a separate host.

**Step 1 — Create a trivial RemotePlugin subclass:**

```python
# src/luxai/robot/core/plugins/remote_plugin.py  (add to existing file)
class LidarDriverPlugin(RemotePlugin):
    def __init__(self):
        super().__init__(plugin_name="lidar-driver")
```

**Step 2 — Register it** in `plugins/__init__.py`.

**Step 3 — Add API definitions** to `api_plugins.py` with `"provider": "lidar-driver"`. The remote plugin host must implement a system-describe endpoint that returns the same service names.

**Step 4 — Regenerate stubs and use:**

```python
robot.enable_plugin_zmq("lidar-driver", endpoint="tcp://192.168.1.200:50700")
scan = robot.lidar.get_scan()
```

---

## Frame Types

The `FRAME_TYPE_REGISTRY` in [api_factory.py](src/luxai/robot/core/api_factory.py) maps IDL `frame_type` strings to Python classes. This controls both runtime type enforcement in `TypedStreamReader` and the stub type annotation.

| `frame_type` string | Class | `.value` type | Typical use |
|---|---|---|---|
| `"Frame"` | `Frame` | `bytes` | Generic binary |
| `"BoolFrame"` | `BoolFrame` | `bool` | Single boolean |
| `"IntFrame"` | `IntFrame` | `int` | Single integer |
| `"FloatFrame"` | `FloatFrame` | `float` | Single float |
| `"StringFrame"` | `StringFrame` | `str` | Text events |
| `"BytesFrame"` | `BytesFrame` | `bytes` | Raw bytes |
| `"DictFrame"` | `DictFrame` | `dict` | Structured data, events |
| `"ListFrame"` | `ListFrame` | `list` | Arrays (IMU, etc.) |
| `"AudioFrameRaw"` | `AudioFrameRaw` | `bytes` | PCM audio; also has `.channels`, `.sample_rate`, `.bit_depth` |
| `"AudioFrameFlac"` | `AudioFrameFlac` | `bytes` | FLAC-compressed audio |
| `"ImageFrameRaw"` | `ImageFrameRaw` | `bytes` | Raw image; also `.width`, `.height`, `.channels`, `.pixel_format` |
| `"ImageFrameCV"` | `ImageFrameCV` | `np.ndarray` | OpenCV-compatible image |
| `"ImageFrameJpeg"` | `ImageFrameJpeg` | `bytes` | JPEG-compressed image |
| `"JointStateFrame"` | `JointStateFrame` | `dict` | Joint positions/velocities; use `.joints()`, `.position(name)`, etc. |
| `"JointCommandFrame"` | `JointCommandFrame` | `dict` | Joint position commands; use `.set_joint(name, position, velocity)` |
| `"JointTrajectoryFrame"` | `JointTrajectoryFrame` | `dict` | Multi-point trajectory |
| `"LedColorFrame"` | `LedColorFrame` | — | LED color control |

`AudioFrameRaw` and `ImageFrameRaw` also carry a `.gid` (group/stream ID) and `.id` (frame sequence number) — useful when multiplexing multiple streams on the same topic.

**To add a new frame type:** Implement the class in `src/luxai/robot/core/frames/` (or in magpie), then add it to `FRAME_TYPE_REGISTRY` in `api_factory.py`.

---

## Design Decisions and Rationale

### Why IDL-driven codegen instead of hand-written methods?

With ~50+ RPC services and ~20 streams, hand-writing every method would mean 70+ identical boilerplate functions. The IDL approach:
- Eliminates the boilerplate entirely — adding an API is 8 lines in a dict.
- Keeps method signatures, docstrings, and type stubs in perfect sync.
- Makes the full API surface visible at a glance without reading implementation code.
- Allows the same spec to drive both the runtime method and the `.pyi` stub.

### Why sync *and* `_async`, not a `blocking=` parameter?

The original design had `method(blocking=True/False)` returning `Union[value, ActionHandle]`. Problems:
- Every sync call still spawned a thread (even when blocking=True) — wasteful.
- The return type was `Union[T, ActionHandle]`, requiring `.result()` on every blocking call.
- IDEs couldn't infer whether the return was `T` or `ActionHandle`.

The current design:
- Sync: no thread, returns `T` directly — ergonomic and efficient.
- `_async`: spawns a thread, returns `ActionHandle` — explicit opt-in.
- Return types are unambiguous in stubs.

### Why `cancel_service_name` as the signal for `_async`?

Every long-running RPC that makes sense to cancel already has a cancel service. Using that as the heuristic avoids an extra IDL field for the common case, while the `async_variant` override handles edge cases.

### Why Transport as a Protocol, not an ABC?

`@runtime_checkable Protocol` enables structural subtyping — any object implementing the three methods is a valid Transport without needing to import from this package. This is useful for testing (mock transports) and for third-party transport implementations.

### Why is the API attachment at module level (`attach_core_apis(Robot, QTROBOT_APIS)`) instead of in `__init__`?

Running it at module import time means:
- The `Robot` class is fully typed at class creation — no mutable state per-instance.
- `Robot.__init__` is fast: it only does the handshake, not method generation.
- All instances share the same generated methods (they're class attributes, not instance attributes).

### Why does `_StreamSubscription` swallow callback exceptions?

A buggy user callback should not crash the subscription's background thread and stop all future frames from arriving. The exception is logged at DEBUG level — users can always add their own try/except inside the callback.

---

## Development Setup

```bash
git clone https://github.com/luxai-robot/robot-sdk-python
cd robot-sdk-python

# Create a venv and install in editable mode with dev extras
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"            # installs pytest + coverage
pip install -e ".[asr-azure]"      # if testing ASR plugin

# Run tests
pytest tests/

# Regenerate the type stub after any IDL change
python scrtipts/gen_robot_stubs.py

# Check the stub was generated correctly
python -c "from luxai.robot.core import Robot; print(Robot.tts)"
```

**Version management:** The SDK version is read dynamically from `luxai.robot.__version__` (defined in `src/luxai/robot/__init__.py`). Update it there before releasing.

**Releasing to PyPI:**
```bash
pip install build twine
python -m build
twine upload dist/*
```
