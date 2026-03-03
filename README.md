# luxai-robot — Python Robot SDK

[![PyPI version](https://img.shields.io/pypi/v/luxai-robot)](https://pypi.org/project/luxai-robot/)
[![Python](https://img.shields.io/pypi/pyversions/luxai-robot)](https://pypi.org/project/luxai-robot/)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](LICENSE)

A Python SDK for communicating with [LuxAI](https://luxai.com) robots. It provides a clean, transport-agnostic API for controlling robot hardware — speech synthesis, face animations, gestures, motors, audio/video playback, camera, and microphone — from any Python environment over a network connection.

> **Primary target:** QTrobot v3 (`QTRD` series). The SDK is designed to be robot-agnostic; future robot models can be supported by extending the API definitions.

---

## Table of Contents

- [Installation](#installation)
- [Connecting to the Robot](#connecting-to-the-robot)
- [API Concepts](#api-concepts)
  - [RPC APIs — sync and async](#rpc-apis--sync-and-async)
  - [Stream APIs](#stream-apis)
  - [ActionHandle](#actionhandle)
  - [Coordinating multiple actions](#coordinating-multiple-actions)
- [API Reference](#api-reference)
  - [TTS — Text-to-Speech](#tts--text-to-speech)
  - [Face](#face)
  - [Gesture](#gesture)
  - [Motor](#motor)
  - [Media — Audio](#media--audio)
  - [Media — Video](#media--video)
  - [Speaker](#speaker)
  - [Microphone](#microphone)
- [Plugin System](#plugin-system)
  - [Camera (RealSense)](#camera-realsense)
  - [ASR — Azure Speech](#asr--azure-speech)
- [Examples](#examples)
- [License](#license)

---

## Installation

```bash
pip install luxai-robot
```

**Optional plugin extras:**

| Extra | Installs |
|---|---|
| `luxai-robot[asr-azure]` | Azure Cognitive Services Speech SDK + PyTorch VAD |

Python **≥ 3.7.3** is required.

---

## Connecting to the Robot

```python
from luxai.robot.core import Robot

# By serial number (auto-discovered over the local network)
robot = Robot.connect_zmq(node_id="QTRD000310")

# By explicit IP address and port
robot = Robot.connect_zmq(endpoint="tcp://192.168.1.100:50500")

print(f"Connected to {robot._robot_serial} ({robot._robot_type}), SDK: {robot._sdk_version}")

# ... use the robot ...

robot.close()
```

Always call `robot.close()` when done (or use a `try/finally` block, as shown in the examples).

---

## API Concepts

The SDK exposes two categories of APIs, accessible through namespace views on the `Robot` object (`robot.tts`, `robot.face`, `robot.gesture`, …).

### RPC APIs — sync and async

**Sync** (blocking): calls the robot, waits for the response, and returns the value directly.

```python
# Blocks until the robot finishes speaking; returns None
robot.tts.say_text("acapela", "Hello world!")

# Returns a list immediately after the robot responds
engines = robot.tts.list_engines()
```

**Async** (non-blocking): fires the request and returns an `ActionHandle` immediately. Only available for long-running operations that support cancellation (methods named `*_async`).

```python
# Returns immediately — the robot speaks in the background
h = robot.tts.say_text_async("acapela", "This is a long sentence...")
time.sleep(1)
h.cancel()   # stop early
```

### Stream APIs

Streams let you push data *to* the robot (writers) or receive data *from* the robot (readers and callbacks).

**Writer** — push frames to the robot:

```python
writer = robot.media.stream.open_fg_audio_stream_writer()
writer.write(audio_frame)
```

**Reader** — pull frames one at a time (blocking with timeout):

```python
reader = robot.microphone.stream.open_int_audio_ch0_reader()
frame = reader.read(timeout=3.0)   # returns None on timeout
```

**Callback** — receive frames in a background thread:

```python
def on_joint_state(frame):
    print(frame.value)

robot.motor.stream.on_joints_state(on_joint_state)
```

### ActionHandle

`robot.*_async()` calls return an `ActionHandle` object.

| Method / Property | Description |
|---|---|
| `.result()` | Block and return the response value (raises on error) |
| `.wait()` | Block until the action completes (no return value) |
| `.cancel()` | Request cancellation |
| `.done` | `True` if completed or cancelled |
| `.add_done_callback(fn)` | Call `fn(handle)` when done |

```python
h = robot.face.show_emotion_async("QT/surprise")

# Option 1 — wait and get the return value
result = h.result()

# Option 2 — just wait
h.wait()

# Option 3 — fire-and-forget with callback
h.add_done_callback(lambda h: print("done:", h.done))

# Cancel a running action
h.cancel()
```

### Coordinating multiple actions

```python
from luxai.robot.core import wait_all_actions, wait_any_action

h1 = robot.tts.say_text_async("acapela", "Playing audio at the same time.")
h2 = robot.media.play_fg_audio_file_async("/path/to/file.wav")

wait_all_actions([h1, h2])   # wait for both to finish
# wait_any_action([h1, h2]) # wait for whichever finishes first
```

---

## API Reference

### TTS — Text-to-Speech

```python
robot.tts.<method>(...)
```

| Method | Returns | Description |
|---|---|---|
| `list_engines()` | `list[str]` | All loaded TTS engine IDs |
| `get_default_engine()` | `str` | Current default engine ID |
| `set_default_engine(engine)` | — | Set the default engine |
| `get_languages(engine)` | `list[str]` | Supported language codes |
| `get_voices(engine)` | `list[dict]` | Available voices |
| `supports_ssml(engine)` | `bool` | Whether the engine accepts SSML |
| `get_config(engine)` | `dict` | Current engine configuration |
| `set_config(engine, config)` | — | Update engine configuration |
| `say_text(engine, text, *, lang, voice, rate, pitch, volume, style)` | — | Speak plain text (blocking) |
| `say_text_async(engine, text, ...)` | `ActionHandle` | Speak plain text (non-blocking) |
| `say_ssml(engine, ssml)` | — | Speak SSML markup (blocking) |
| `say_ssml_async(engine, ssml)` | `ActionHandle` | Speak SSML markup (non-blocking) |

**Examples:**

```python
# List engines and voices
engines = robot.tts.list_engines()         # e.g. ['acapela', 'azure']
voices  = robot.tts.get_voices("acapela")

# Speak synchronously
robot.tts.say_text("acapela", "Hello!")
robot.tts.say_text("acapela", "Slower and higher.", rate=0.8, pitch=1.2)

# Speak asynchronously and cancel mid-sentence
h = robot.tts.say_text_async("acapela", "This is a very long sentence that will be cut short.")
time.sleep(1)
h.cancel()

# SSML (Azure example)
robot.tts.say_ssml("azure", '<speak version="1.0" ...> ... </speak>')
```

---

### Face

```python
robot.face.<method>(...)
```

| Method | Returns | Description |
|---|---|---|
| `list_emotions()` | `list[str]` | Available emotion animation files |
| `show_emotion(emotion, *, speed)` | — | Play an emotion animation (blocking) |
| `show_emotion_async(emotion, *, speed)` | `ActionHandle` | Play an emotion animation (non-blocking) |
| `look(l_eye, r_eye, *, duration)` | — | Move eye pupils; auto-reset if `duration > 0` |

**Examples:**

```python
emotions = robot.face.list_emotions()      # e.g. ['QT/kiss', 'QT/surprise', ...]

# Blocking — waits until animation finishes
robot.face.show_emotion("QT/surprise")
robot.face.show_emotion("QT/surprise", speed=2.0)   # 2× speed

# Non-blocking — cancel after 3 seconds
h = robot.face.show_emotion_async("QT/breathing_exercise")
time.sleep(3)
h.cancel()

# Move eyes: [dx, dy] pixel offset from center
robot.face.look(l_eye=[30, 0], r_eye=[30, 0])           # look right
robot.face.look(l_eye=[0, 20], r_eye=[0, 20], duration=2.0)  # look down, reset after 2 s
```

---

### Gesture

```python
robot.gesture.<method>(...)
```

| Method | Returns | Description |
|---|---|---|
| `list_files()` | `list[str]` | Available gesture file names |
| `play_file(gesture, *, speed_factor)` | `bool` | Play a gesture file (blocking) |
| `play_file_async(gesture, *, speed_factor)` | `ActionHandle` | Play a gesture file (non-blocking) |
| `play(keyframes, *, resample, rate_hz, speed_factor)` | — | Play in-memory keyframes (blocking) |
| `play_async(keyframes, ...)` | `ActionHandle` | Play in-memory keyframes (non-blocking) |
| `record_async(motors, *, release_motors, delay_start_ms, timeout_ms, ...)` | `ActionHandle[dict]` | Record a gesture; `.result()` → keyframes |
| `stop_record()` | `bool` | Stop an in-progress recording |
| `store_record(gesture)` | — | Persist the last recording to a named file |

**Examples:**

```python
gestures = robot.gesture.list_files()     # e.g. ['QT/bye', 'QT/happy', ...]

# Play a named gesture (blocking)
robot.gesture.play_file("QT/bye")

# Play non-blocking, cancel on keypress
h = robot.gesture.play_file_async("QT/bye")
input("Press Enter to cancel...")
h.cancel()
robot.motor.home_all()

# Record a gesture, play it back, then save it
h = robot.gesture.record_async(
    motors=["RightShoulderPitch", "RightShoulderRoll", "RightElbowRoll"],
    release_motors=True,
    delay_start_ms=2000,
    timeout_ms=20000,
)
input("Press Enter to stop recording...")
robot.gesture.stop_record()
keyframes = h.result()                    # dict of recorded trajectory

robot.gesture.play(keyframes)             # play it back
robot.gesture.store_record("my_gesture") # save as a named file
```

---

### Motor

```python
robot.motor.<method>(...)
robot.motor.stream.<stream_method>(...)
```

**RPC methods:**

| Method | Returns | Description |
|---|---|---|
| `list()` | `dict` | All motor names and their configuration |
| `on(motor)` | — | Enable torque on a single motor |
| `off(motor)` | — | Disable torque on a single motor |
| `on_all()` | — | Enable torque on all motors |
| `off_all()` | — | Disable torque on all motors |
| `home(motor)` | — | Move a single motor to its home position |
| `home_all()` | — | Move all motors to their home positions |
| `set_velocity(motor, velocity)` | — | Set the default velocity for a motor |
| `set_calib(motor, offset, *, store)` | — | Apply a calibration offset (optionally persist) |
| `calib_all()` | — | Re-apply stored calibration offsets to all motors |

**Stream methods:**

| Method | Description |
|---|---|
| `stream.on_joints_state(callback)` | Subscribe to joint position/velocity/effort/temp/voltage |
| `stream.on_joints_error(callback)` | Subscribe to motor fault events |
| `stream.open_joints_command_writer()` | Open a writer to send direct joint position commands |

**Examples:**

```python
from luxai.robot.core.frames import JointStateFrame, JointCommandFrame

motors = robot.motor.list()   # {'HeadYaw': {'position_min': -90, ...}, ...}

robot.motor.home_all()
robot.motor.off("RightShoulderPitch")   # release for manual positioning
robot.motor.set_velocity("HeadYaw", 50)

# Real-time joint state via callback
def on_state(frame: JointStateFrame):
    for joint in frame.joints():
        print(f"{joint}: pos={frame.position(joint):.1f}°")

robot.motor.stream.on_joints_state(on_state)

# Direct joint commands via stream
writer = robot.motor.stream.open_joints_command_writer()
cmd = JointCommandFrame()
cmd.set_joint("HeadYaw", position=30, velocity=40)
writer.write(cmd)
```

---

### Media — Audio

The media subsystem provides two independent audio lanes: **Foreground (FG)** for primary content and **Background (BG)** for ambient/music. Each lane supports file playback and raw PCM streaming.

```python
robot.media.<method>(...)
robot.media.stream.<stream_method>(...)
```

**Volume:**

| Method | Returns | Description |
|---|---|---|
| `get_fg_audio_volume()` | `float` | FG lane volume `[0.0, 1.0]` |
| `set_fg_audio_volume(value)` | — | Set FG lane volume |
| `get_bg_audio_volume()` | `float` | BG lane volume |
| `set_bg_audio_volume(value)` | — | Set BG lane volume |

**File playback (FG):**

| Method | Returns | Description |
|---|---|---|
| `play_fg_audio_file(uri)` | `bool` | Play file or URL (blocking) |
| `play_fg_audio_file_async(uri)` | `ActionHandle` | Play file or URL (non-blocking) |
| `pause_fg_audio_file()` | — | Pause current FG file |
| `resume_fg_audio_file()` | — | Resume paused FG file |

**File playback (BG):** same pattern — `play_bg_audio_file`, `play_bg_audio_file_async`, `pause_bg_audio_file`, `resume_bg_audio_file`.

**PCM streaming:**

| Method | Description |
|---|---|
| `stream.open_fg_audio_stream_writer()` | Stream raw PCM frames to the FG lane |
| `stream.open_bg_audio_stream_writer()` | Stream raw PCM frames to the BG lane |
| `cancel_fg_audio_stream()` | Stop a running FG stream |
| `cancel_bg_audio_stream()` | Stop a running BG stream |

**Examples:**

```python
robot.media.set_fg_audio_volume(1.0)

# Blocking playback (local file or URL)
robot.media.play_fg_audio_file("/home/qtrobot/audio/hello.wav")
robot.media.play_fg_audio_file("https://example.com/song.mp3")

# Non-blocking with cancel
h = robot.media.play_fg_audio_file_async("/home/qtrobot/audio/hello.wav")
time.sleep(3)
h.cancel()

# Pause and resume
h = robot.media.play_fg_audio_file_async("/home/qtrobot/audio/long.wav")
time.sleep(5)
robot.media.pause_fg_audio_file()
time.sleep(2)
robot.media.resume_fg_audio_file()
h.wait()

# Stream raw PCM (16-bit mono 16 kHz sine wave)
from luxai.magpie.frames import AudioFrameRaw

writer = robot.media.stream.open_fg_audio_stream_writer()
frame = AudioFrameRaw(channels=1, sample_rate=16000, bit_depth=16, data=pcm_bytes)
writer.write(frame)
```

---

### Media — Video

Two video lanes (**FG** and **BG**) for file playback or raw RGBA frame streaming. FG supports a transparency alpha channel.

```python
robot.media.<method>(...)
robot.media.stream.<stream_method>(...)
```

| Method | Returns | Description |
|---|---|---|
| `play_fg_video_file(uri, *, speed, with_audio)` | `bool` | Play FG video file (blocking) |
| `play_fg_video_file_async(uri, ...)` | `ActionHandle` | Play FG video file (non-blocking) |
| `pause_fg_video_file()` / `resume_fg_video_file()` | — | Pause / resume FG file |
| `set_fg_video_alpha(value)` | — | FG transparency `[0.0 transparent … 1.0 opaque]` |
| `cancel_fg_video_stream()` | — | Stop the FG stream |
| `play_bg_video_file(uri, ...)` | `bool` | Play BG video file (blocking) |
| `play_bg_video_file_async(uri, ...)` | `ActionHandle` | Play BG video file (non-blocking) |
| `stream.open_fg_video_stream_writer()` | writer | Stream RGBA frames to FG lane |
| `stream.open_bg_video_stream_writer()` | writer | Stream RGBA frames to BG lane |

**Example:**

```python
from luxai.magpie.frames import ImageFrameRaw

# Play a video file non-blocking
h = robot.media.play_bg_video_file_async("/home/qtrobot/video/intro.avi")
time.sleep(3)
h.cancel()

# Stream custom RGBA frames
robot.media.set_fg_video_alpha(0.0)  # start transparent
writer = robot.media.stream.open_fg_video_stream_writer()

frame = ImageFrameRaw(data=rgba_bytes, format="raw",
                      width=400, height=280, channels=4, pixel_format="RGBA")
writer.write(frame)
robot.media.set_fg_video_alpha(1.0)  # fade in
```

---

### Speaker

Master speaker volume control (affects all audio output).

```python
robot.speaker.<method>(...)
```

| Method | Returns | Description |
|---|---|---|
| `get_volume()` | `float` | Current master volume `[0.0, 1.0]` |
| `set_volume(value)` | `bool` | Set master volume |
| `mute()` | `bool` | Mute the speaker |
| `unmute()` | `bool` | Unmute the speaker |

```python
robot.speaker.set_volume(0.8)
vol = robot.speaker.get_volume()
robot.speaker.mute()
robot.speaker.unmute()
```

---

### Microphone

Access to the internal mic array (up to 5 processed channels) and an external mic. Includes VAD (voice activity detection) events and DSP tuning parameters.

```python
robot.microphone.<method>(...)
robot.microphone.stream.<stream_method>(...)
```

**Tuning:**

| Method | Returns | Description |
|---|---|---|
| `get_int_tuning()` | `dict` | All readable Respeaker DSP parameters |
| `set_int_tuning(name, value)` | `bool` | Set a single DSP parameter |

**Audio streams** (outbound — robot sends audio to you):

| Stream method | Frame type | Description |
|---|---|---|
| `stream.open_int_audio_ch0_reader(...)` | `AudioFrameRaw` | Internal mic channel 0 (processed/ASR) |
| `stream.open_int_audio_ch1_reader(...)` | `AudioFrameRaw` | Channel 1 |
| `stream.open_int_audio_ch2_reader(...)` | `AudioFrameRaw` | Channel 2 |
| `stream.open_int_audio_ch3_reader(...)` | `AudioFrameRaw` | Channel 3 |
| `stream.open_int_audio_ch4_reader(...)` | `AudioFrameRaw` | Channel 4 |
| `stream.open_ext_audio_ch0_reader(...)` | `AudioFrameRaw` | External mic channel 0 |
| `stream.on_int_event(callback, ...)` | `DictFrame` | VAD + direction-of-arrival events |

**Examples:**

```python
import wave
from luxai.magpie.frames import AudioFrameRaw, DictFrame

# Read DSP tuning params
params = robot.microphone.get_int_tuning()
robot.microphone.set_int_tuning("AGCONOFF", 1.0)   # enable AGC

# Record microphone audio to a .wav file
reader = robot.microphone.stream.open_int_audio_ch0_reader(queue_size=10)
first: AudioFrameRaw = reader.read(timeout=3.0)

with wave.open("recording.wav", "wb") as wf:
    wf.setnchannels(first.channels)
    wf.setsampwidth(first.bit_depth // 8)
    wf.setframerate(first.sample_rate)
    wf.writeframes(first.data)
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        frame = reader.read(timeout=1.0)
        if frame:
            wf.writeframes(frame.data)

# VAD + direction-of-arrival events
def on_event(frame: DictFrame):
    evt = frame.value
    if evt.get("activity"):
        print(f"Voice detected — DOA: {evt.get('direction')}°")

robot.microphone.stream.on_int_event(on_event)
```

---

## Plugin System

Plugins extend the SDK with additional hardware or services that are not part of the robot's core firmware. Enable a plugin before using its API.

```python
# Load a plugin running locally on the same machine
robot.enable_plugin_local("asr-azure")

# Load a plugin running on another host (e.g. a camera node)
robot.enable_plugin_zmq("realsense-driver", endpoint="tcp://192.168.1.150:50655")
```

Once enabled, the plugin's APIs are available under the corresponding namespace (`robot.asr`, `robot.camera`).

---

### Camera (RealSense)

Requires the `realsense-driver` plugin running on the robot or a separate host.

```python
robot.enable_plugin_zmq("realsense-driver", endpoint="tcp://<host>:50655")
```

**RPC methods:**

| Method | Returns | Description |
|---|---|---|
| `camera.get_color_intrinsics()` | `dict` | RGB camera intrinsics |
| `camera.get_depth_intrinsics()` | `dict` | Depth camera intrinsics |
| `camera.get_depth_scale()` | `float` | Depth scale factor (m/unit) |

**Stream methods:**

| Method | Description |
|---|---|
| `camera.stream.open_color_reader(...)` | Read RGB frames |
| `camera.stream.open_depth_reader(...)` | Read depth frames |
| `camera.stream.on_acceleration(callback)` | Subscribe to IMU acceleration events |

**Example:**

```python
robot.enable_plugin_zmq("realsense-driver", endpoint="tcp://192.168.1.150:50655")

intrinsics = robot.camera.get_color_intrinsics()
scale = robot.camera.get_depth_scale()
print(f"Depth scale: {scale} m/unit")

color_reader = robot.camera.stream.open_color_reader()
frame = color_reader.read(timeout=3.0)
```

---

### ASR — Azure Speech

Requires the `asr-azure` plugin and the `luxai-robot[asr-azure]` extras to be installed.

```bash
pip install "luxai-robot[asr-azure]"
```

```python
robot.enable_plugin_local("asr-azure")
```

**RPC methods:**

| Method | Returns | Description |
|---|---|---|
| `asr.configure_azure(region, subscription, *, continuous_mode, use_vad)` | `bool` | Configure Azure Speech credentials |
| `asr.recognize_azure()` | `dict` | Single recognition (blocking) |
| `asr.recognize_azure_async()` | `ActionHandle[dict]` | Single recognition (non-blocking) |

**Stream methods:**

| Method | Description |
|---|---|
| `asr.stream.on_azure_event(callback)` | Subscribe to recognition lifecycle events |
| `asr.stream.on_azure_speech(callback)` | Subscribe to recognized speech results |

**Example:**

```python
from luxai.magpie.frames import StringFrame, DictFrame

robot.enable_plugin_local("asr-azure")
robot.asr.configure_azure(
    region="westeurope",
    subscription="<your-key>",
    continuous_mode=True,
    use_vad=True,
)

def on_event(frame: StringFrame):
    print("ASR event:", frame.value)

def on_speech(frame: DictFrame):
    print("Recognized:", frame.value)

robot.asr.stream.on_azure_event(on_event)
robot.asr.stream.on_azure_speech(on_speech)

# Or use a single blocking recognition
result = robot.asr.recognize_azure()
print(result)
```

---

## Examples

Ready-to-run examples are in the [`examples/`](examples/) directory:

| File | Demonstrates |
|---|---|
| [`tts_examples.py`](examples/tts_examples.py) | List engines, say text, cancel speech, SSML, voices |
| [`face_examples.py`](examples/face_examples.py) | List emotions, play animations, control eye gaze |
| [`gesture_examples.py`](examples/gesture_examples.py) | List gestures, play, record, and store gesture files |
| [`motor_examples.py`](examples/motor_examples.py) | List motors, torque on/off, homing, joint streams |
| [`media_audio_examples.py`](examples/media_audio_examples.py) | File playback, online radio, raw PCM streaming |
| [`media_video_examples.py`](examples/media_video_examples.py) | Video file playback, RGBA frame streaming |
| [`speaker_examples.py`](examples/speaker_examples.py) | Volume control, mute/unmute |
| [`microphone_example.py`](examples/microphone_example.py) | Record to WAV, VAD events, DSP tuning |
| [`camera_example.py`](examples/camera_example.py) | Camera intrinsics, color stream (RealSense plugin) |
| [`asr_azure_example.py`](examples/asr_azure_example.py) | Continuous speech recognition (Azure plugin) |

Each example connects to the robot, demonstrates a set of APIs, and exits cleanly on `Ctrl+C`.

---

## License

This project is licensed under the **GNU Lesser General Public License v3.0** (LGPL-3.0).
See the [LICENSE](LICENSE) file for the full text.

© LuxAI S.A.
