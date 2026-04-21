# Plugin System Guide

The `luxai-robot` SDK plugin system lets you extend a robot with additional hardware and services — a depth camera, a custom speech recogniser, a lidar scanner, a cloud AI module — and call them through the same clean API used for the robot's built-in capabilities.

What makes the system powerful is that plugins are **transport-agnostic and location-agnostic**. A plugin can run:

- **In the same Python process** (local USB camera, local ML model)
- **On the same LAN** over ZMQ
- **Anywhere on the internet** over MQTT or WebRTC

In every case the user API is identical: `robot.camera.get_color_intrinsics()` works the same whether the camera node is running on the robot itself, on a laptop on the same network, or on a cloud server ten thousand kilometres away.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Available Transports](#available-transports)
- [Enabling Plugins](#enabling-plugins)
  - [Local Plugin (same process)](#local-plugin-same-process)
  - [ZMQ Plugin (LAN)](#zmq-plugin-lan)
  - [MQTT Plugin (internet-ready)](#mqtt-plugin-internet-ready)
  - [WebRTC Plugin (P2P, lowest latency)](#webrtc-plugin-p2p-lowest-latency)
- [Disabling Plugins](#disabling-plugins)
- [Built-in Plugins](#built-in-plugins)
  - [Camera — RealSense](#camera--realsense)
  - [ASR — Azure Speech](#asr--azure-speech)
  - [ASR — Nvidia Riva](#asr--nvidia-riva)
  - [ASR — Groq (Whisper)](#asr--groq-whisper)
- [The Distributed Robot Architecture](#the-distributed-robot-architecture)

---

## How It Works

Every plugin is **self-describing**. When you call `enable_plugin_*()`, the SDK connects to the plugin service and asks it to describe itself — exactly the same handshake used to connect to the robot itself. The plugin responds with a routing table of all its RPC services and data streams. The SDK merges these routes into the `Robot` object, making the plugin's APIs instantly available.

```
robot.enable_plugin_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")
     │
     ├─ connect to plugin's MQTT namespace
     ├─ send SYSTEM_DESCRIBE_SERVICE
     ├─ receive { rpcs: [...], streams: [...] }
     └─ merge routes into robot._rpc_routes / robot._stream_routes

robot.camera.get_color_intrinsics()   ← dispatched via plugin's transport
```

Because the robot and each plugin can use **different transports**, you can mix and match freely:

```python
robot = Robot.connect_webrtc_mqtt("mqtt://broker.example.com", "QTRD000320")

# Plugin on the same LAN — no need for WebRTC for this one
robot.enable_plugin_zmq("lidar-driver", endpoint="tcp://192.168.1.200:50700")

# Plugin exposed via the same MQTT gateway — reuses the connection
robot.enable_plugin_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")
```

---

## Available Transports

| Method | Where the plugin runs | Connection type |
|---|---|---|
| `enable_plugin_local(name)` | Same Python process | In-process (ZMQ inproc) |
| `enable_plugin_zmq(name, ...)` | Same LAN | Direct TCP/ZMQ |
| `enable_plugin_mqtt(name, node_id)` | Anywhere with broker access | MQTT topics |
| `enable_plugin_webrtc_mqtt(name, node_id)` | Anywhere (internet) | P2P WebRTC, MQTT signaling |
| `enable_plugin_webrtc_zmq(name, node_id)` | LAN, broker-less | P2P WebRTC, ZMQ signaling |

---

## Enabling Plugins

### Local Plugin (same process)

The plugin node runs inside your Python process, communicating over an in-process ZMQ channel. This is used for local hardware (USB mic, local ASR engine) where low latency and no network overhead are important.

```python
robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")
robot.enable_plugin_local("asr-azure")

robot.asr.configure_azure(region="westeurope", subscription="<key>")
result = robot.asr.recognize_azure()
```

---

### ZMQ Plugin (LAN)

The plugin runs on a separate host or process on the same network. Use either the plugin's direct TCP endpoint or its Zeroconf-discoverable `node_id`.

```python
robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")

# By explicit endpoint
robot.enable_plugin_zmq("realsense-driver", endpoint="tcp://192.168.1.150:50655")

# By node_id — discovered automatically via Zeroconf/mDNS (no IP needed)
robot.enable_plugin_zmq("realsense-driver", robot_id="qtrobot-realsense-driver")

intrinsics = robot.camera.get_color_intrinsics()
reader = robot.camera.stream.open_color_reader()
frame = reader.read(timeout=3.0)
```

---

### MQTT Plugin (internet-ready)

The plugin is exposed through the **same MQTT gateway** that bridges the robot's services. The plugin's `node_id` becomes its MQTT topic namespace (e.g., `qtrobot-realsense-driver/camera/color/intrinsics`).

When the robot is connected via `connect_mqtt()`, the **broker connection is shared** automatically — no extra configuration needed.

```python
robot = Robot.connect_mqtt("mqtt://10.231.0.2:1883", "QTRD000320")

# Reuses the robot's existing broker connection
robot.enable_plugin_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")

intrinsics = robot.camera.get_color_intrinsics()
```

Over the internet via a cloud broker:

```python
robot = Robot.connect_mqtt("mqtt://broker.example.com:1883", "QTRD000320")
robot.enable_plugin_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")
# The plugin is now reachable from anywhere in the world
```

The MQTT plugin can also have its own independent broker (e.g., if the plugin is managed by a different gateway):

```python
from luxai.robot.core.transport import MqttTransport
from luxai.magpie.transport.mqtt import MqttConnection

conn = MqttConnection("mqtt://other-broker:1883")
conn.connect(timeout=10.0)
transport = MqttTransport(conn, "qtrobot-realsense-driver")
robot.enable_plugin("realsense-driver", transport)
```

---

### WebRTC Plugin (P2P, lowest latency)

Each plugin gets its own independent **WebRTC peer connection** — with a dedicated data channel and its own video/audio media tracks. This means the robot's media tracks and the plugin's media tracks never conflict, even when both stream video simultaneously.

When the robot is connected via `connect_webrtc_mqtt()` or `connect_webrtc_zmq()`, all signaling parameters (broker URL, options, timeout) are **inherited automatically**.

**MQTT signaling:**

```python
robot = Robot.connect_webrtc_mqtt("mqtt://broker.example.com:1883", "QTRD000320")

# Uses the same broker and options as the robot connection — zero config
robot.enable_plugin_webrtc_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")

# Or override to use a different broker for the plugin
robot.enable_plugin_webrtc_mqtt(
    "realsense-driver",
    node_id="qtrobot-realsense-driver",
    broker_url="mqtt://other-broker:1883",
)
```

**ZMQ signaling (broker-less LAN):**

```python
robot = Robot.connect_webrtc_zmq("tcp://192.168.1.10:5555", "QTRD000320")

# Inherits signaling endpoint from the robot connection
robot.enable_plugin_webrtc_zmq("realsense-driver", node_id="qtrobot-realsense-driver")

# Or specify a different endpoint for the plugin
robot.enable_plugin_webrtc_zmq(
    "realsense-driver",
    node_id="qtrobot-realsense-driver",
    endpoint="tcp://192.168.1.10:5556",
)
```

**With STUN/TURN for NAT traversal:**

```python
from luxai.robot import WebRTCOptions, WebRTCTurnServer

robot = Robot.connect_webrtc_mqtt(
    "mqtt://broker.example.com:1883",
    "QTRD000320",
    webrtc_options=WebRTCOptions(
        stun_servers=["stun:stun.l.google.com:19302"],
        turn_servers=[WebRTCTurnServer(url="turn:turn.example.com:3478",
                                       username="user", credential="pass")],
    ),
)
# Plugin peer inherits the same STUN/TURN configuration
robot.enable_plugin_webrtc_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")
```

---

## Disabling Plugins

Call `disable_plugin(name)` to cleanly shut down a plugin and release its resources. The plugin's APIs are removed from the robot immediately.

```python
robot.enable_plugin_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")
frame = robot.camera.stream.open_color_reader().read(timeout=3.0)

robot.disable_plugin("realsense-driver")
# robot.camera.* calls will now raise UnsupportedAPIError
```

When `robot.close()` is called, all active plugins are stopped automatically.

---

## Built-in Plugins

### Camera — RealSense

Requires the `realsense-driver` service running on the robot or a separate host.

**RPC methods:**

| Method | Returns | Description |
|---|---|---|
| `camera.get_color_intrinsics()` | `dict` | RGB camera intrinsic parameters |
| `camera.get_depth_intrinsics()` | `dict` | Depth camera intrinsic parameters |
| `camera.get_depth_scale()` | `float` | Depth scale factor (metres per unit) |

**Stream methods:**

| Method | Frame type | Description |
|---|---|---|
| `camera.stream.open_color_reader()` | `ImageFrameCV` | RGB video frames |
| `camera.stream.open_depth_reader()` | `ImageFrameCV` | Depth frames |
| `camera.stream.on_acceleration(callback)` | `ListFrame` | IMU acceleration events |

**Example (ZMQ):**

```python
robot.enable_plugin_zmq("realsense-driver", endpoint="tcp://10.231.0.2:50655")

scale = robot.camera.get_depth_scale()
reader = robot.camera.stream.open_color_reader()
frame = reader.read(timeout=3.0)   # frame.value is a np.ndarray (BGR)
```

**Example (MQTT — over internet):**

```python
robot = Robot.connect_mqtt("mqtt://broker.example.com:1883", "QTRD000320")
robot.enable_plugin_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")

intrinsics = robot.camera.get_color_intrinsics()
```

---

### ASR — Azure Speech

Runs locally in the same Python process. Requires `pip install luxai-robot[asr-azure]`.

```python
robot.enable_plugin_local("asr-azure")
robot.asr.configure_azure(
    region="westeurope",
    subscription="<your-key>",
    continuous_mode=True,
    use_vad=True,
)

def on_speech(frame):
    print("Recognized:", frame.value)

robot.asr.stream.on_azure_speech(on_speech)
result = robot.asr.recognize_azure()   # blocking single-shot
```

---

### ASR — Nvidia Riva

Runs locally. Requires `pip install luxai-robot[asr-riva]` and a running Riva ASR Docker server.

```python
robot.enable_plugin_local("asr-riva")
robot.asr.configure_riva(server="localhost:50051", language="en-US", continuous_mode=True)

robot.asr.stream.on_riva_speech(lambda f: print(f.value))
```

---

### ASR — Groq (Whisper)

Runs locally via the Groq REST API. Requires `pip install luxai-robot[asr-groq]` and a Groq API key.

```python
robot.enable_plugin_local("asr-groq")
robot.asr.configure_groq(api_key="<your-key>", language="en", continuous_mode=True)

robot.asr.stream.on_groq_speech(lambda f: print(f.value))
```

---

## The Distributed Robot Architecture

The plugin system, combined with MQTT and WebRTC transports, enables a genuinely distributed robot service architecture.

A single `Robot` object can simultaneously use:

```
robot = Robot.connect_webrtc_mqtt("mqtt://cloud-broker.example.com:1883", "QTRD000320")
         │
         ├─ Core robot services     → WebRTC P2P to QTRD000320 gateway
         │   robot.tts.say_text()
         │   robot.face.show_emotion()
         │   robot.motor.home_all()
         │
         ├─ RealSense camera        → WebRTC P2P to realsense-driver
         │   robot.enable_plugin_webrtc_mqtt("realsense-driver", node_id="qtrobot-realsense-driver")
         │   robot.camera.stream.open_color_reader()
         │
         ├─ Custom LiDAR scanner    → ZMQ on LAN (direct TCP)
         │   robot.enable_plugin_zmq("lidar-driver", endpoint="tcp://192.168.1.200:50700")
         │   robot.lidar.get_scan()
         │
         └─ Cloud ASR (in-process)  → local plugin, no network
             robot.enable_plugin_local("asr-azure")
             robot.asr.recognize_azure()
```

Each component is:
- **Independently deployable** — run the camera driver on the robot, the lidar on a separate PC, the ASR in the cloud
- **Independently scalable** — swap one plugin for another without touching the rest
- **Internet-ready** — MQTT and WebRTC plugins work through NATs and firewalls with no VPN required
- **Uniformly addressable** — `robot.camera`, `robot.lidar`, `robot.asr` all look the same regardless of where the service runs

This makes it straightforward to build robotics applications where perception, actuation, and intelligence are distributed across edge devices, local servers, and cloud services — all controlled through a single clean Python API.
