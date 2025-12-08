from __future__ import annotations

from typing import Any, Dict, List, Type

QTROBOT_API_DOCS: Dict[str, str] = {
    # =========================
    # RPCs – SPEECH
    # =========================

    "speech.say": (
        "Speak the given text using the robot's Text-to-Speech engine.\n"
        "\n"
        "This RPC can run in blocking or non-blocking mode. In the default case\n"
        "(blocking=True), the call waits until the speech action finishes and\n"
        "returns a completed ActionHandle. With blocking=False, the method\n"
        "returns immediately with a running ActionHandle that you can manage.\n"
        "\n"
        "Blocking example:\n"
        "    # Wait until speech finishes, then continue\n"
        "    robot.speech.say(\"Hello!\")\n"
        "\n"
        "Non-blocking example:\n"
        "    handle = robot.speech.say(\"Hello!\", blocking=False)\n"
        "    # do other work...\n"
        "    handle.wait()            # or handle.result(), handle.cancel()\n"
        "\n"
        "Args:\n"
        "    message (str): Text to synthesize.\n"
        "    blocking (bool): If True, wait for completion before returning.\n"
        "\n"
        "Returns:\n"
        "    ActionHandle: Handle representing the speech action.\n"
        "\n"
        "Notes:\n"
        "    - Speech configuration (language, pitch, speed) is controlled via\n"
        "      speech.config().\n"
        "    - A new speech.say() or speech.talk() call will typically interrupt\n"
        "      any ongoing speech.\n"
    ),

    "speech.talk": (
        "Trigger a behavior-level speaking action using the given text.\n"
        "Compared to speech.say(), this may involve additional behavior logic\n"
        "such as coordinated gestures or timing.\n"
        "\n"
        "Blocking example:\n"
        "    robot.speech.talk(\"Welcome to the session.\")\n"
        "\n"
        "Non-blocking example:\n"
        "    handle = robot.speech.talk(\"Welcome!\", blocking=False)\n"
        "    # do other work...\n"
        "    if not handle.done():\n"
        "        handle.cancel()\n"
        "\n"
        "Args:\n"
        "    message (str): Text for the high-level talk behavior.\n"
        "    blocking (bool): If True, wait for completion before returning.\n"
        "\n"
        "Returns:\n"
        "    ActionHandle: Handle representing the behavior-level speech action.\n"
    ),

    "speech.stop": (
        "Request cancellation of any ongoing speech or talk action.\n"
        "\n"
        "Use this when you want to interrupt speech.say() or speech.talk()\n"
        "before it finishes.\n"
        "\n"
        "Example:\n"
        "    handle = robot.speech.say(\"This is a long sentence...\", blocking=False)\n"
        "    # ... decide to interrupt\n"
        "    robot.speech.stop()\n"
        "    # handle.result() will then raise ActionCancelledError\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    "speech.config": (
        "Configure the TTS engine used by speech.say() and speech.talk().\n"
        "\n"
        "Any parameter set to None leaves the existing value unchanged.\n"
        "\n"
        "Example:\n"
        "    # Switch to US English and slightly faster speech\n"
        "    robot.speech.config(language=\"en-US\", pitch=100, speed=120)\n"
        "\n"
        "Args:\n"
        "    language (str | None): Language code, e.g. 'en-US', or None to keep current.\n"
        "    pitch (int): Pitch level (backend-specific range).\n"
        "    speed (int): Speaking speed (backend-specific range).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    # =========================
    # RPCs – EMOTION
    # =========================

    "emotion.look": (
        "Move the robot's eyes to the specified positions over the given duration.\n"
        "\n"
        "The eye_l and eye_r arguments are lists of servo target values (int or float)\n"
        "for the left and right eye motors.\n"
        "\n"
        "Example (simple eye movement):\n"
        "    robot.emotion.look(\n"
        "        eye_l=[10, 20],\n"
        "        eye_r=[10, 20],\n"
        "        duration=0.5,\n"
        "    )\n"
        "\n"
        "Args:\n"
        "    eye_l (List[int | float]): Left eye servo positions.\n"
        "    eye_r (List[int | float]): Right eye servo positions.\n"
        "    duration (float): Duration of the movement in seconds.\n"
        "\n"
        "Returns:\n"
        "    ActionHandle: Handle for the eye movement action.\n"
    ),

    "emotion.show": (
        "Display a named facial emotion on the robot (e.g. 'happy', 'sad').\n"
        "\n"
        "Example:\n"
        "    robot.emotion.show(\"happy\")\n"
        "\n"
        "Args:\n"
        "    name (str): Emotion identifier (implementation-specific list).\n"
        "\n"
        "Returns:\n"
        "    ActionHandle: Handle representing the emotion display action.\n"
    ),

    "emotion.stop": (
        "Stop any active facial expression or eye animation.\n"
        "\n"
        "Typical usage:\n"
        "    robot.emotion.show(\"surprised\")\n"
        "    # later...\n"
        "    robot.emotion.stop()\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    # =========================
    # RPCs – GESTURE
    # =========================

    "gesture.get_all": (
        "Return a list of all gesture names stored on the robot.\n"
        "\n"
        "Example:\n"
        "    names = robot.gesture.get_all()\n"
        "    for name in names:\n"
        "        print(\"Gesture:\", name)\n"
        "\n"
        "Returns:\n"
        "    List[str]: Names of available gestures.\n"
    ),

    "gesture.play": (
        "Play a stored gesture animation at the given speed.\n"
        "\n"
        "Example (play at normal speed):\n"
        "    robot.gesture.play(\"QT/bye\")\n"
        "\n"
        "Example (play slower):\n"
        "    robot.gesture.play(\"QT/bye\", speed=0.5)\n"
        "\n"
        "Args:\n"
        "    name (str): Gesture name.\n"
        "    speed (float): Playback speed multiplier (1.0 = normal).\n"
        "    blocking (bool): If True, wait until completion.\n"
        "\n"
        "Returns:\n"
        "    ActionHandle: Handle for the gesture playback.\n"
        "\n"
        "Notes:\n"
        "    - A new gesture.play() call will typically interrupt an ongoing one.\n"
    ),

    "gesture.stop": (
        "Stop any active gesture playback or gesture recording.\n"
        "\n"
        "Example:\n"
        "    robot.gesture.play(\"QT/bye\", blocking=False)\n"
        "    # later...\n"
        "    robot.gesture.stop()\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    "gesture.record": (
        "Start recording a gesture for the specified body parts.\n"
        "\n"
        "Recording continues until gesture.stop() is called or a timeout is reached.\n"
        "\n"
        "Example:\n"
        "    # Record a gesture on the right arm for up to 10 seconds\n"
        "    handle = robot.gesture.record(parts=[\"right_arm\"], timeout=10)\n"
        "    # Move the arm manually...\n"
        "    handle.wait()  # or robot.gesture.stop() to end early\n"
        "\n"
        "Args:\n"
        "    parts (List[str]): Body parts to record, e.g. ['left_arm'].\n"
        "    idle_parts (bool): If True, keep non-recorded parts idle.\n"
        "    wait (int): Delay in seconds before recording starts.\n"
        "    timeout (int): Maximum recording duration in seconds (0 = no limit).\n"
        "\n"
        "Returns:\n"
        "    ActionHandle: Handle representing the recording action.\n"
    ),

    "gesture.save": (
        "Save the last recorded gesture under a specified name and path.\n"
        "\n"
        "Example:\n"
        "    robot.gesture.save(name=\"QT/bye_custom\", path=\"/data/gestures\")\n"
        "\n"
        "Args:\n"
        "    name (str): Gesture name.\n"
        "    path (str): Directory or file path to store the gesture.\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    # =========================
    # RPCs – MOTORS
    # =========================

    "motors.home": (
        "Move one or more motor groups to their home (reference) positions.\n"
        "\n"
        "Example:\n"
        "    # Home the head motors\n"
        "    robot.motors.home([\"head\"])\n"
        "\n"
        "Args:\n"
        "    parts (List[str]): Motor groups to home, e.g. ['head', 'right_arm'].\n"
        "    blocking (bool): If True, wait until homing completes.\n"
        "\n"
        "Returns:\n"
        "    ActionHandle: Handle for the homing action.\n"
    ),

    "motors.set_mode": (
        "Set the control mode for the given motor groups.\n"
        "\n"
        "Typical modes are:\n"
        "    0 = ON (torque enabled)\n"
        "    1 = OFF (torque disabled)\n"
        "    2 = BRAKE\n"
        "\n"
        "Example:\n"
        "    # Enable torque on both arms\n"
        "    robot.motors.set_mode([\"left_arm\", \"right_arm\"], mode=0)\n"
        "\n"
        "Args:\n"
        "    parts (List[str]): Motor groups to configure.\n"
        "    mode (int): Control mode constant (implementation-specific mapping).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    "motors.set_velocity": (
        "Set the default movement velocity for one or more motor groups.\n"
        "This velocity is typically used as a scaling factor for future motion.\n"
        "\n"
        "Example:\n"
        "    # Slow movements on the head\n"
        "    robot.motors.set_velocity([\"head\"], velocity=50)\n"
        "\n"
        "Args:\n"
        "    parts (List[str]): Motor groups to affect.\n"
        "    velocity (int): Velocity scalar (e.g. 0–255, implementation-specific).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    # =========================
    # RPCs – AUDIO
    # =========================

    "audio.play": (
        "Play an audio file through the robot's speakers.\n"
        "\n"
        "Example:\n"
        "    robot.audio.play(filename=\"hello.wav\", filepath=\"/data/sounds\")\n"
        "\n"
        "Args:\n"
        "    filename (str): Name of the audio file.\n"
        "    filepath (str): Directory or full path where the file is located.\n"
        "    blocking (bool): If True, wait until playback completes.\n"
        "\n"
        "Returns:\n"
        "    ActionHandle: Handle for the playback action.\n"
    ),

    "audio.stop": (
        "Stop any audio currently playing on the robot.\n"
        "\n"
        "Example:\n"
        "    handle = robot.audio.play(\"music.wav\", \"/data/sounds\", blocking=False)\n"
        "    # later...\n"
        "    robot.audio.stop()\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    "audio.talk": (
        "Trigger a higher-level behavior that plays an audio file as part of a\n"
        "scripted behavior (e.g., pre-recorded prompts).\n"
        "\n"
        "Example:\n"
        "    robot.audio.talk(filename=\"prompt.wav\", filepath=\"/data/prompts\")\n"
        "\n"
        "Args:\n"
        "    filename (str): Audio file for the behavior.\n"
        "    filepath (str): Directory or full path to the file.\n"
        "    blocking (bool): If True, wait until the behavior finishes.\n"
        "\n"
        "Returns:\n"
        "    ActionHandle: Handle for the behavior action.\n"
    ),

    # =========================
    # RPCs – SPEAKER
    # =========================

    "speaker.set_volume": (
        "Set the master speaker output volume (0–100).\n"
        "This affects both speech and audio playback.\n"
        "\n"
        "Example:\n"
        "    robot.speaker.set_volume(80)\n"
        "\n"
        "Args:\n"
        "    volume (int): Volume percentage (0 = mute, 100 = max).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    # =========================
    # RPCs – MICROPHONE TUNING
    # =========================

    "microphone.get_tuning": (
        "Get a tuning parameter value from the microphone front-end.\n"
        "\n"
        "Example:\n"
        "    gain = robot.microphone.get_tuning(\"gain\")\n"
        "    print(\"Current gain:\", gain)\n"
        "\n"
        "Args:\n"
        "    param (str): Parameter name, e.g. 'gain', 'noise_suppression'.\n"
        "\n"
        "Returns:\n"
        "    float: Current parameter value.\n"
    ),

    "microphone.set_tuning": (
        "Set a tuning parameter value on the microphone front-end.\n"
        "\n"
        "Example:\n"
        "    robot.microphone.set_tuning(\"gain\", 0.8)\n"
        "\n"
        "Args:\n"
        "    param (str): Parameter name.\n"
        "    value (float): New parameter value.\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    # =========================
    # STREAMS – MOTORS
    # =========================

    "motors.joints": (
        "Joint-related streaming APIs.\n"
        "\n"
        "motors.joints can be used as:\n"
        "  - An output stream of joint states (JointStateFrame) from the robot.\n"
        "  - An input channel for joint commands (JointCommandFrame) to the robot.\n"
        "\n"
        "Typical usage for JOINT STATE STREAM (JointStateFrame):\n"
        "\n"
        "Callback subscription:\n"
        "    def on_joints(frame: JointStateFrame) -> None:\n"
        "        # frame.value is your joint_state dict\n"
        "        Logger.info(frame.value)\n"
        "\n"
        "    sub = robot.motors.stream.on_joints(on_joints, queue_size=10)\n"
        "    # Later: sub.cancel() to unsubscribe\n"
        "\n"
        "Reader API:\n"
        "    reader = robot.motors.stream.open_joints_reader(queue_size=10)\n"
        "    frame = reader.read(timeout=None)  # -> JointStateFrame\n"
        "\n"
        "In the reader API, read(timeout=...) raises TimeoutError if no frame arrives.\n"
        "\n"
        "Typical usage for JOINT COMMAND INPUT (JointCommandFrame):\n"
        "    joints_writer = robot.motors.stream.open_joints_writer()\n"
        "    cmd = JointCommandFrame()\n"
        "    cmd.set_joint('HeadYaw', position=20)\n"
        "    joints_writer.write(cmd)\n"        
    ),

    "motors.state": (
        "Stream of motor diagnostic state (temperature, voltage) as MotorStateFrame.\n"
        "\n"
        "Callback subscription:\n"
        "    def on_state(frame: MotorStateFrame) -> None:\n"
        "        Logger.info(frame.value)\n"
        "\n"
        "    sub = robot.motors.stream.on_state(on_state, queue_size=10)\n"
        "\n"
        "Reader API:\n"
        "    reader = robot.motors.stream.open_state_reader(queue_size=10)\n"
        "    frame = reader.read(timeout=1.0)  # -> MotorStateFrame\n"
        "\n"
        "read(timeout=...) raises TimeoutError if no frame arrives in time.\n"
    ),

    # =========================
    # STREAMS – MICROPHONE (activity & direction)
    # =========================

    "microphone.activity": (
        "Boolean activity detection stream (sound present or not) as BoolFrame.\n"
        "\n"
        "Callback subscription:\n"
        "    def on_activity(frame: BoolFrame) -> None:\n"
        "        if frame.value:\n"
        "            Logger.info(\"Sound detected\")\n"
        "\n"
        "    sub = robot.microphone.stream.on_activity(on_activity, queue_size=10)\n"
        "\n"
        "Reader API:\n"
        "    reader = robot.microphone.stream.open_activity_reader(queue_size=10)\n"
        "    frame = reader.read(timeout=0.5)  # -> BoolFrame\n"
        "\n"
        "TimeoutError is raised if no frame arrives before the timeout.\n"
    ),

    "microphone.direction": (
        "Estimated sound direction stream as IntFrame (e.g. angle in degrees).\n"
        "\n"
        "Callback subscription:\n"
        "    def on_direction(frame: IntFrame) -> None:\n"
        "        Logger.info(f\"Sound from {frame.value} degrees\")\n"
        "\n"
        "    sub = robot.microphone.stream.on_direction(on_direction, queue_size=10)\n"
        "\n"
        "Reader API:\n"
        "    reader = robot.microphone.stream.open_direction_reader(queue_size=10)\n"
        "    frame = reader.read(timeout=1.0)  # -> IntFrame\n"
    ),

    # =========================
    # STREAMS – MICROPHONE (raw audio channels)
    # =========================

    "microphone.channel0": (
        "Raw audio stream from microphone channel 0 as AudioFrameFlac.\n"
        "\n"
        "Callback subscription:\n"
        "    def on_channel0(frame: AudioFrameFlac) -> None:\n"
        "        Logger.info(f\"channel0: {len(frame.data)} bytes\")\n"
        "\n"
        "    sub = robot.microphone.stream.on_channel0(on_channel0, queue_size=10)\n"
        "\n"
        "Reader API:\n"
        "    reader = robot.microphone.stream.open_channel0_reader(queue_size=10)\n"
        "    frame = reader.read(timeout=None)  # -> AudioFrameFlac\n"
        "\n"
        "read(timeout=...) raises TimeoutError on timeout.\n"
    ),

    "microphone.channel1": (
        "Raw audio stream from microphone channel 1 as AudioFrameFlac.\n"
        "\n"
        "Callback subscription:\n"
        "    def on_channel1(frame: AudioFrameFlac) -> None:\n"
        "        Logger.info(f\"channel1: {len(frame.data)} bytes\")\n"
        "\n"
        "    sub = robot.microphone.stream.on_channel1(on_channel1, queue_size=10)\n"
        "\n"
        "Reader API:\n"
        "    reader = robot.microphone.stream.open_channel1_reader(queue_size=10)\n"
        "    frame = reader.read(timeout=None)  # -> AudioFrameFlac\n"
    ),

    "microphone.channel2": (
        "Raw audio stream from microphone channel 2 as AudioFrameFlac.\n"
        "\n"
        "Callback subscription:\n"
        "    def on_channel2(frame: AudioFrameFlac) -> None:\n"
        "        Logger.info(f\"channel2: {len(frame.data)} bytes\")\n"
        "\n"
        "    sub = robot.microphone.stream.on_channel2(on_channel2, queue_size=10)\n"
        "\n"
        "Reader API:\n"
        "    reader = robot.microphone.stream.open_channel2_reader(queue_size=10)\n"
        "    frame = reader.read(timeout=None)  # -> AudioFrameFlac\n"
    ),

    "microphone.channel3": (
        "Raw audio stream from microphone channel 3 as AudioFrameFlac.\n"
        "\n"
        "Callback subscription:\n"
        "    def on_channel3(frame: AudioFrameFlac) -> None:\n"
        "        Logger.info(f\"channel3: {len(frame.data)} bytes\")\n"
        "\n"
        "    sub = robot.microphone.stream.on_channel3(on_channel3, queue_size=10)\n"
        "\n"
        "Reader API:\n"
        "    reader = robot.microphone.stream.open_channel3_reader(queue_size=10)\n"
        "    frame = reader.read(timeout=None)  # -> AudioFrameFlac\n"
    ),

    "microphone.channel4": (
        "Raw audio stream from microphone channel 4 as AudioFrameFlac.\n"
        "\n"
        "Callback subscription:\n"
        "    def on_channel4(frame: AudioFrameFlac) -> None:\n"
        "        Logger.info(f\"channel4: {len(frame.data)} bytes\")\n"
        "\n"
        "    sub = robot.microphone.stream.on_channel4(on_channel4, queue_size=10)\n"
        "\n"
        "Reader API:\n"
        "    reader = robot.microphone.stream.open_channel4_reader(queue_size=10)\n"
        "    frame = reader.read(timeout=None)  # -> AudioFrameFlac\n"
    ),

    "microphone.external1": (
        "Raw audio stream from the external microphone (channel 1) as AudioFrameFlac.\n"
        "\n"
        "Callback subscription:\n"
        "    def on_external1(frame: AudioFrameFlac) -> None:\n"
        "        Logger.info(f\"external1: {len(frame.data)} bytes\")\n"
        "\n"
        "    sub = robot.microphone.stream.on_external1(on_external1, queue_size=10)\n"
        "\n"
        "Reader API:\n"
        "    reader = robot.microphone.stream.open_external1_reader(queue_size=10)\n"
        "    frame = reader.read(timeout=None)  # -> AudioFrameFlac\n"
    ),

    "microphone.led": (
        "Output stream controlling the ReSpeaker status LED via LedColorFrame.\n"
        "\n"
        "Typical usage (publishing LED color):\n"
        "    frame = LedColorFrame(r=0, g=255, b=0, a=1.0)\n"
        "    led_writer = robot.microphone.stream.open_led_writer() \n"
        "    led_writer.write(color)\n"
        "\n"        
    ),
}
