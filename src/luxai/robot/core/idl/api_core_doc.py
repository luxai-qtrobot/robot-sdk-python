from __future__ import annotations

from typing import Dict

QTROBOT_CORE_API_DOCS: Dict[str, str] = {
    # ===========================================================
    # RPC APIs — MEDIA
    # ===========================================================

    "media.play_fg_audio_file": (
        "Play an audio file on the foreground (FG) audio lane.\n"
        "\n"
        "Blocks until playback finishes and returns the result.\n"
        "For non-blocking use, call ``play_fg_audio_file_async()`` which returns\n"
        "an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.\n"
        "\n"
        "Args:\n"
        "    uri (str): Audio file URI/path supported by the engine.\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback completed successfully, False otherwise.\n"
        "\n"
        "Examples:\n"
        "    # Blocking — wait for file to finish\n"
        "    ok = robot.media.play_fg_audio_file('/data/audio/hello.wav')\n"
        "\n"
        "    # Non-blocking — cancel after 3 seconds\n"
        "    h = robot.media.play_fg_audio_file_async('/data/audio/hello.wav')\n"
        "    time.sleep(3)\n"
        "    h.cancel()\n"
    ),
    "media.pause_fg_audio_file": (
        "Pause current foreground (FG) audio file playback.\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.resume_fg_audio_file": (
        "Resume foreground (FG) audio file playback after pause.\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.cancel_fg_audio_stream": (
        "Cancel / stop the current foreground (FG) audio stream pipeline.\n"
        "\n"
        "This is for streamed audio frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.pause_fg_audio_stream": (
        "Pause foreground (FG) audio stream processing.\n"
        "\n"
        "This is for streamed audio frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.resume_fg_audio_stream": (
        "Resume foreground (FG) audio stream processing.\n"
        "\n"
        "This is for streamed audio frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.set_fg_audio_volume": (
        "Set foreground (FG) audio lane volume.\n"
        "\n"
        "Args:\n"
        "    value (float): Volume in range [0.0, 1.0].\n"
        "\n"
        "Returns:\n"
        "    None\n"
        "\n"
        "Example:\n"
        "    robot.media.set_fg_audio_volume(0.8)\n"
    ),
    "media.get_fg_audio_volume": (
        "Get foreground (FG) audio lane volume.\n"
        "\n"
        "Returns:\n"
        "    float: Volume in range [0.0, 1.0].\n"
        "\n"
        "Example:\n"
        "    vol = robot.media.get_fg_audio_volume()\n"
    ),

    "media.play_bg_audio_file": (
        "Play an audio file on the background (BG) audio lane.\n"
        "\n"
        "Blocks until playback finishes and returns the result.\n"
        "For non-blocking use, call ``play_bg_audio_file_async()`` which returns\n"
        "an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.\n"
        "\n"
        "Args:\n"
        "    uri (str): Audio file URI/path supported by the engine.\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback completed successfully, False otherwise.\n"
        "\n"
        "Examples:\n"
        "    # Blocking — wait for file to finish\n"
        "    ok = robot.media.play_bg_audio_file('/data/audio/music.wav')\n"
        "\n"
        "    # Non-blocking — cancel after 5 seconds\n"
        "    h = robot.media.play_bg_audio_file_async('/data/audio/music.wav')\n"
        "    time.sleep(5)\n"
        "    h.cancel()\n"
    ),
    "media.pause_bg_audio_file": (
        "Pause current background (BG) audio file playback.\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.resume_bg_audio_file": (
        "Resume background (BG) audio file playback after pause.\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.cancel_bg_audio_stream": (
        "Cancel / stop the current background (BG) audio stream pipeline.\n"
        "\n"
        "This is for streamed audio frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.pause_bg_audio_stream": (
        "Pause background (BG) audio stream processing.\n"
        "\n"
        "This is for streamed audio frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.resume_bg_audio_stream": (
        "Resume background (BG) audio stream processing.\n"
        "\n"
        "This is for streamed audio frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.set_bg_audio_volume": (
        "Set background (BG) audio lane volume.\n"
        "\n"
        "Args:\n"
        "    value (float): Volume in range [0.0, 1.0].\n"
        "\n"
        "Returns:\n"
        "    None\n"
        "\n"
        "Example:\n"
        "    robot.media.set_bg_audio_volume(0.5)\n"
    ),
    "media.get_bg_audio_volume": (
        "Get background (BG) audio lane volume.\n"
        "\n"
        "Returns:\n"
        "    float: Volume in range [0.0, 1.0].\n"
        "\n"
        "Example:\n"
        "    vol = robot.media.get_bg_audio_volume()\n"
    ),

    "media.play_fg_video_file": (
        "Play a video file on the foreground (FG) video lane.\n"
        "\n"
        "Blocks until playback finishes and returns the result.\n"
        "For non-blocking use, call ``play_fg_video_file_async()`` which returns\n"
        "an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.\n"
        "\n"
        "Args:\n"
        "    uri (str): Video file URI/path supported by the engine.\n"
        "    speed (float): Playback speed factor (default 1.0).\n"
        "    with_audio (bool): If True, play embedded audio track (default False).\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback completed successfully, False otherwise.\n"
        "\n"
        "Examples:\n"
        "    # Blocking\n"
        "    ok = robot.media.play_fg_video_file('/data/video/intro.mp4')\n"
        "\n"
        "    # Non-blocking\n"
        "    h = robot.media.play_fg_video_file_async('/data/video/intro.mp4')\n"
        "    h.cancel()\n"
    ),
    "media.pause_fg_video_file": (
        "Pause current foreground (FG) video file playback.\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.resume_fg_video_file": (
        "Resume foreground (FG) video file playback after pause.\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.cancel_fg_video_stream": (
        "Cancel / stop the current foreground (FG) video stream pipeline.\n"
        "\n"
        "This is for streamed video frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.pause_fg_video_stream": (
        "Pause foreground (FG) video stream processing.\n"
        "\n"
        "This is for streamed video frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.resume_fg_video_stream": (
        "Resume foreground (FG) video stream processing.\n"
        "\n"
        "This is for streamed video frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.set_fg_video_alpha": (
        "Set foreground (FG) video alpha (transparency).\n"
        "\n"
        "Args:\n"
        "    value (float): Alpha in range [0.0, 1.0] where 0.0 is fully transparent.\n"
        "\n"
        "Returns:\n"
        "    None\n"
        "\n"
        "Example:\n"
        "    robot.media.set_fg_video_alpha(0.8)\n"
    ),

    "media.play_bg_video_file": (
        "Play a video file on the background (BG) video lane.\n"
        "\n"
        "Blocks until playback finishes and returns the result.\n"
        "For non-blocking use, call ``play_bg_video_file_async()`` which returns\n"
        "an :class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.\n"
        "\n"
        "Args:\n"
        "    uri (str): Video file URI/path supported by the engine.\n"
        "    speed (float): Playback speed factor (default 1.0).\n"
        "    with_audio (bool): If True, play embedded audio track (default False).\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback completed successfully, False otherwise.\n"
        "\n"
        "Examples:\n"
        "    # Blocking\n"
        "    ok = robot.media.play_bg_video_file('/data/emotions/QT/kiss.avi')\n"
        "\n"
        "    # Non-blocking — pause, then resume\n"
        "    h = robot.media.play_bg_video_file_async('/data/emotions/QT/kiss.avi')\n"
        "    time.sleep(2)\n"
        "    robot.media.pause_bg_video_file()\n"
        "    time.sleep(3)\n"
        "    robot.media.resume_bg_video_file()\n"
        "    h.wait()\n"
    ),
    "media.pause_bg_video_file": (
        "Pause current background (BG) video file playback.\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.resume_bg_video_file": (
        "Resume background (BG) video file playback after pause.\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.cancel_bg_video_stream": (
        "Cancel / stop the current background (BG) video stream pipeline.\n"
        "\n"
        "This is for streamed video frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.pause_bg_video_stream": (
        "Pause background (BG) video stream processing.\n"
        "\n"
        "This is for streamed video frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),
    "media.resume_bg_video_stream": (
        "Resume background (BG) video stream processing.\n"
        "\n"
        "This is for streamed video frames (not file playback).\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    # ===========================================================
    # RPC APIs — SPEAKER
    # ===========================================================

    "speaker.set_volume": (
        "Set the master speaker volume.\n"
        "\n"
        "Args:\n"
        "    value (float): Volume in range [0.0, 1.0].\n"
        "\n"
        "Returns:\n"
        "    bool: True if mixer control succeeded, False otherwise.\n"
        "\n"
        "Example:\n"
        "    robot.speaker.set_volume(0.8)\n"
    ),
    "speaker.get_volume": (
        "Get the master speaker volume.\n"
        "\n"
        "Returns:\n"
        "    float: Volume in range [0.0, 1.0].\n"
        "\n"
        "Example:\n"
        "    vol = robot.speaker.get_volume()\n"
    ),
    "speaker.mute": (
        "Mute the speaker output.\n"
        "\n"
        "Returns:\n"
        "    bool: True if succeeded, False otherwise.\n"
        "\n"
        "Example:\n"
        "    robot.speaker.mute()\n"
    ),
    "speaker.unmute": (
        "Unmute the speaker output.\n"
        "\n"
        "Returns:\n"
        "    bool: True if succeeded, False otherwise.\n"
        "\n"
        "Example:\n"
        "    robot.speaker.unmute()\n"
    ),

    # ===========================================================
    # RPC APIs — FACE
    # ===========================================================

    "face.look": (
        "Move (offset) the eyes on the face display.\n"
        "\n"
        "Offsets are applied relative to the configured center positions.\n"
        "If duration > 0, eyes reset back to center after the given seconds.\n"
        "\n"
        "Args:\n"
        "    l_eye (list): [dx, dy] offset for left eye (pixels).\n"
        "    r_eye (list): [dx, dy] offset for right eye (pixels).\n"
        "    duration (float): Optional reset delay in seconds (default 0.0).\n"
        "\n"
        "Returns:\n"
        "    None\n"
        "\n"
        "Examples:\n"
        "    robot.face.look(l_eye=[30, 0], r_eye=[30, 0])          # look right\n"
        "    robot.face.look(l_eye=[0, 0], r_eye=[0, 0], duration=2) # center, auto-reset\n"
    ),
    "face.show_emotion": (
        "Play an emotion video on the face background lane.\n"
        "\n"
        "Blocks until the emotion finishes playing and returns the result.\n"
        "For non-blocking use, call ``show_emotion_async()`` which returns\n"
        "an :class:`ActionHandle` — call ``.cancel()`` on it to stop the emotion early.\n"
        "\n"
        "Args:\n"
        "    emotion (str): Emotion name or relative path (with/without .avi).\n"
        "    speed (float): Optional playback speed factor.\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback completed, False otherwise.\n"
        "\n"
        "Examples:\n"
        "    # Blocking\n"
        "    robot.face.show_emotion('QT/kiss')\n"
        "    robot.face.show_emotion('QT/surprise', speed=2.0)\n"
        "\n"
        "    # Non-blocking — cancel after 3 seconds\n"
        "    h = robot.face.show_emotion_async('QT/breathing_exercise')\n"
        "    time.sleep(3)\n"
        "    h.cancel()\n"
    ),
    "face.list_emotions": (
        "List available emotion video files under the emotions directory.\n"
        "\n"
        "Scans recursively and returns relative paths for .avi/.AVI files.\n"
        "\n"
        "Returns:\n"
        "    list: List[str] of emotion file paths.\n"
        "\n"
        "Example:\n"
        "    emotions = robot.face.list_emotions()\n"
        "    for e in emotions:\n"
        "        print(e)\n"
    ),

    # ===========================================================
    # RPC APIs — MOTOR
    # ===========================================================

    "motor.list": (
        "List configured motors and their parameters.\n"
        "\n"
        "Returns:\n"
        "    dict: {motor_name: {part, position_min, position_max, position_home,\n"
        "          velocity_max, calibration_offset, overload_threshold, ...}}\n"
        "\n"
        "Example:\n"
        "    motors = robot.motor.list()\n"
        "    for name, info in motors.items():\n"
        "        print(name, info)\n"
    ),
    "motor.set_calib": (
        "Set calibration parameters for a motor.\n"
        "\n"
        "Args:\n"
        "    motor (str): Motor name.\n"
        "    offset (float): Optional calibration offset in degrees.\n"
        "    overload_threshold (int): Optional overload threshold value.\n"
        "    velocity_max (int): Optional maximum velocity value.\n"
        "    store (bool): If True, persist changes to config (default False).\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
        "\n"
        "Example:\n"
        "    robot.motor.set_calib('HeadYaw', offset=2.5, store=True)\n"
        "    robot.motor.set_calib('HeadYaw', overload_threshold=80.0, velocity_max=100.0)\n"
    ),
    "motor.calib_all": (
        "Run manual calibration procedure for all motors (writes offsets and stores them).\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
    ),
    "motor.set_velocity": (
        "Set default velocity for a motor.\n"
        "\n"
        "Args:\n"
        "    motor (str): Motor name.\n"
        "    velocity (int): Velocity value; validated against the motor's max.\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
        "\n"
        "Example:\n"
        "    robot.motor.set_velocity('HeadYaw', 50)\n"
    ),
    "motor.on": (
        "Enable torque for a motor.\n"
        "\n"
        "Args:\n"
        "    motor (str): Motor name.\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
        "\n"
        "Example:\n"
        "    robot.motor.on('HeadYaw')\n"
    ),
    "motor.off": (
        "Disable torque for a motor.\n"
        "\n"
        "Args:\n"
        "    motor (str): Motor name.\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
        "\n"
        "Example:\n"
        "    robot.motor.off('HeadYaw')\n"
    ),
    "motor.on_all": (
        "Enable torque for all motors.\n"
        "\n"
        "Returns:\n"
        "    bool: True\n"
        "\n"
        "Example:\n"
        "    robot.motor.on_all()\n"
    ),
    "motor.off_all": (
        "Disable torque for all motors.\n"
        "\n"
        "Returns:\n"
        "    bool: True\n"
        "\n"
        "Example:\n"
        "    robot.motor.off_all()\n"
    ),
    "motor.home": (
        "Move a motor to its configured home position.\n"
        "\n"
        "Args:\n"
        "    motor (str): Motor name.\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
        "\n"
        "Example:\n"
        "    robot.motor.home('HeadYaw')\n"
    ),
    "motor.home_all": (
        "Move all motors to their configured home positions.\n"
        "\n"
        "Returns:\n"
        "    bool: True\n"
        "\n"
        "Example:\n"
        "    robot.motor.home_all()\n"
    ),

    # ===========================================================
    # RPC APIs — GESTURE
    # ===========================================================

    "gesture.record": (
        "Start recording a gesture trajectory for selected motors.\n"
        "\n"
        "Blocks until recording finishes (timeout or manual stop) and returns\n"
        "the captured trajectory dict.\n"
        "For non-blocking use (e.g. stop recording on user input), call\n"
        "``record_async()`` which returns an :class:`ActionHandle`, then call\n"
        "``gesture.stop_record()`` to end recording and ``handle.result()`` to\n"
        "retrieve the trajectory.\n"
        "\n"
        "Args:\n"
        "    motors (list): List[str] of motor names to record.\n"
        "    release_motors (bool): If True, torque is disabled during recording.\n"
        "    delay_start_ms (int): Delay before recording starts (ms, default 0).\n"
        "    timeout_ms (int): Max recording duration (ms, default 60000).\n"
        "    refine_keyframe (bool): If True, compress redundant keyframes.\n"
        "    keyframe_pos_eps (float): Position epsilon for keyframe compression (deg).\n"
        "    keyframe_max_gap_us (int): Max gap for keyframe compression (μs).\n"
        "\n"
        "Returns:\n"
        "    dict: Trajectory dict with 'meta' and 'points'.\n"
        "\n"
        "Examples:\n"
        "    # Non-blocking — stop on user input\n"
        "    h = robot.gesture.record_async(\n"
        "        motors=['RightShoulderPitch', 'RightElbowRoll'],\n"
        "        release_motors=True,\n"
        "        delay_start_ms=2000,\n"
        "        timeout_ms=20000,\n"
        "    )\n"
        "    input('Press Enter to stop...')\n"
        "    robot.gesture.stop_record()\n"
        "    keyframes = h.result()\n"
    ),
    "gesture.stop_record": (
        "Stop an in-progress gesture recording.\n"
        "\n"
        "Returns:\n"
        "    bool: True if a recording was stopped, False if none was in progress.\n"
        "\n"
        "Example:\n"
        "    robot.gesture.stop_record()\n"
    ),
    "gesture.store_record": (
        "Store the last recorded gesture trajectory to an XML file.\n"
        "\n"
        "Args:\n"
        "    gesture (str): Gesture name/path (saved as <gesture>.xml).\n"
        "\n"
        "Returns:\n"
        "    bool: True if saved successfully.\n"
        "\n"
        "Example:\n"
        "    robot.gesture.store_record('my_wave')\n"
    ),
    "gesture.play": (
        "Play a gesture trajectory (keyframes dict).\n"
        "\n"
        "Blocks until playback finishes and returns the result.\n"
        "For non-blocking use, call ``play_async()`` which returns an\n"
        ":class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.\n"
        "\n"
        "Args:\n"
        "    keyframes (dict): Trajectory dict (as returned by ``gesture.record()``).\n"
        "    resample (bool): If True, resample for smooth playback (default True).\n"
        "    rate_hz (float): Resample rate in Hz (default 100.0).\n"
        "    speed_factor (float): Playback speed multiplier (default 1.0).\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback completed successfully.\n"
        "\n"
        "Notes:\n"
        "    Progress is published on the ``gesture.progress`` stream.\n"
        "\n"
        "Examples:\n"
        "    # Blocking\n"
        "    robot.gesture.play(keyframes)\n"
        "\n"
        "    # Non-blocking — cancel on demand\n"
        "    h = robot.gesture.play_async(keyframes)\n"
        "    h.cancel()\n"
    ),
    "gesture.play_file": (
        "Load a gesture XML file and play it.\n"
        "\n"
        "Blocks until playback finishes and returns the result.\n"
        "For non-blocking use, call ``play_file_async()`` which returns an\n"
        ":class:`ActionHandle` — call ``.cancel()`` on it to stop playback early.\n"
        "\n"
        "Args:\n"
        "    gesture (str): Gesture name/path (with/without .xml).\n"
        "    speed_factor (float): Playback speed multiplier (default 1.0).\n"
        "\n"
        "Returns:\n"
        "    bool: True if loaded and played successfully.\n"
        "\n"
        "Examples:\n"
        "    # Blocking — wait for gesture to complete\n"
        "    robot.gesture.play_file('QT/wave')\n"
        "\n"
        "    # Non-blocking — cancel on user input\n"
        "    h = robot.gesture.play_file_async('QT/bye')\n"
        "    input('Press Enter to cancel...')\n"
        "    h.cancel()\n"
    ),
    "gesture.list_files": (
        "List available gesture XML files under the configured gesture directory.\n"
        "\n"
        "Returns:\n"
        "    list: List[str] of gesture file paths.\n"
        "\n"
        "Example:\n"
        "    gestures = robot.gesture.list_files()\n"
        "    for g in gestures:\n"
        "        print(g)\n"
    ),

    # ===========================================================
    # RPC APIs — TTS
    # ===========================================================

    "tts.set_default_engine": (
        "Set the default TTS engine id.\n"
        "\n"
        "Args:\n"
        "    engine (str): Engine id (e.g. 'acapela', 'azure', or custom).\n"
        "\n"
        "Returns:\n"
        "    None\n"
        "\n"
        "Example:\n"
        "    robot.tts.set_default_engine('acapela')\n"
    ),
    "tts.get_default_engine": (
        "Get the current default TTS engine id.\n"
        "\n"
        "Returns:\n"
        "    str: Default engine id.\n"
        "\n"
        "Example:\n"
        "    engine = robot.tts.get_default_engine()\n"
    ),
    "tts.list_engines": (
        "List loaded/available TTS engine ids.\n"
        "\n"
        "Returns:\n"
        "    list: List[str] of engine ids.\n"
        "\n"
        "Example:\n"
        "    engines = robot.tts.list_engines()\n"
    ),
    "tts.say_text": (
        "Synthesize and play plain text using a selected TTS engine.\n"
        "\n"
        "Blocks until audio playback finishes and returns the result.\n"
        "For non-blocking use, call ``say_text_async()`` which returns an\n"
        ":class:`ActionHandle` — call ``.cancel()`` on it to interrupt speech.\n"
        "\n"
        "Args:\n"
        "    text (str): Text to synthesize.\n"
        "    engine (str): Optional engine id to use (uses default if omitted).\n"
        "    lang (str): Optional language code (e.g. 'en-US').\n"
        "    voice (str): Optional voice id/name.\n"
        "    rate (float): Optional speaking rate multiplier.\n"
        "    pitch (float): Optional pitch adjustment.\n"
        "    volume (float): Optional volume level.\n"
        "    style (str): Optional speaking style (engine-dependent).\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
        "\n"
        "Notes:\n"
        "    Visemes may be scheduled to the FaceNode if connected.\n"
        "\n"
        "Examples:\n"
        "    # Blocking — uses default engine\n"
        "    robot.tts.say_text('Hello world!')\n"
        "    robot.tts.say_text('Slower speech', engine='acapela', rate=0.8, pitch=1.1)\n"
        "\n"
        "    # Non-blocking — cancel after 2 seconds\n"
        "    h = robot.tts.say_text_async('This is a very long sentence...')\n"
        "    time.sleep(2)\n"
        "    h.cancel()\n"
    ),
    "tts.say_ssml": (
        "Synthesize and play SSML markup using a selected TTS engine.\n"
        "\n"
        "Blocks until audio playback finishes and returns the result.\n"
        "For non-blocking use, call ``say_ssml_async()`` which returns an\n"
        ":class:`ActionHandle` — call ``.cancel()`` on it to interrupt speech.\n"
        "\n"
        "Args:\n"
        "    ssml (str): SSML markup string.\n"
        "    engine (str): Optional engine id to use (uses default if omitted).\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
        "\n"
        "Example:\n"
        "    robot.tts.say_ssml('<speak>Hello!</speak>')\n"
        "    robot.tts.say_ssml('<speak>Hello!</speak>', engine='azure')\n"
    ),
    "tts.set_config": (
        "Set engine-specific configuration parameters.\n"
        "\n"
        "Args:\n"
        "    config (dict): Key/value config map.\n"
        "    engine (str): Optional engine id (uses default if omitted).\n"
        "\n"
        "Returns:\n"
        "    bool: True if engine accepted configuration.\n"
        "\n"
        "Example:\n"
        "    robot.tts.set_config(config={'pitch': 1.0, 'rate': 0.8})\n"
        "    robot.tts.set_config(engine='acapela', config={'pitch': 1.0, 'rate': 0.8})\n"
    ),
    "tts.get_config": (
        "Get engine-specific configuration parameters.\n"
        "\n"
        "Args:\n"
        "    engine (str): Optional engine id (uses default if omitted).\n"
        "\n"
        "Returns:\n"
        "    dict: Current engine configuration map.\n"
        "\n"
        "Example:\n"
        "    cfg = robot.tts.get_config()\n"
        "    cfg = robot.tts.get_config(engine='acapela')\n"
    ),
    "tts.get_languages": (
        "Get supported language codes for a TTS engine.\n"
        "\n"
        "Args:\n"
        "    engine (str): Optional engine id (uses default if omitted).\n"
        "\n"
        "Returns:\n"
        "    list: List[str] language codes.\n"
        "\n"
        "Example:\n"
        "    langs = robot.tts.get_languages()\n"
        "    langs = robot.tts.get_languages(engine='acapela')\n"
    ),
    "tts.get_voices": (
        "Get supported voices for a TTS engine.\n"
        "\n"
        "Args:\n"
        "    engine (str): Optional engine id (uses default if omitted).\n"
        "\n"
        "Returns:\n"
        "    list: List[dict] voice info dicts (id, lang, gender, display_name, ...).\n"
        "\n"
        "Example:\n"
        "    voices = robot.tts.get_voices()\n"
        "    voices = robot.tts.get_voices(engine='acapela')\n"
        "    for v in voices:\n"
        "        print(v['display_name'], v['lang'])\n"
    ),
    "tts.supports_ssml": (
        "Check whether a TTS engine supports SSML.\n"
        "\n"
        "Args:\n"
        "    engine (str): Optional engine id (uses default if omitted).\n"
        "\n"
        "Returns:\n"
        "    bool: True if SSML is supported.\n"
        "\n"
        "Example:\n"
        "    if robot.tts.supports_ssml():\n"
        "        robot.tts.say_ssml('<speak>Hello!</speak>')\n"
        "    if robot.tts.supports_ssml(engine='azure'):\n"
        "        robot.tts.say_ssml('<speak>Hello!</speak>', engine='azure')\n"
    ),

    # ===========================================================
    # STREAM APIs
    # ===========================================================

    "media.fg_audio_stream": (
        "Inbound audio stream to the media FG audio lane.\n"
        "\n"
        "Send AudioFrameRaw frames to this topic to play streamed audio.\n"
        "\n"
        "Typical usage:\n"
        "    writer = robot.media.stream.open_fg_audio_stream_writer()\n"
        "    writer.write(AudioFrameRaw(...))\n"
        "\n"
        "Notes:\n"
        "    Use ``media.cancel_fg_audio_stream()`` / ``pause`` / ``resume`` to control the pipeline.\n"
    ),
    "media.bg_audio_stream": (
        "Inbound audio stream to the media BG audio lane.\n"
        "\n"
        "Send AudioFrameRaw frames to this topic to play streamed background audio.\n"
        "\n"
        "Typical usage:\n"
        "    writer = robot.media.stream.open_bg_audio_stream_writer()\n"
        "    writer.write(AudioFrameRaw(...))\n"
        "\n"
        "Notes:\n"
        "    Use ``media.cancel_bg_audio_stream()`` / ``pause`` / ``resume`` to control the pipeline.\n"
    ),
    "media.fg_video_stream": (
        "Inbound video stream to the media FG video lane.\n"
        "\n"
        "Send ImageFrameRaw frames to this topic to render streamed foreground video.\n"
        "\n"
        "Typical usage:\n"
        "    writer = robot.media.stream.open_fg_video_stream_writer()\n"
        "    writer.write(ImageFrameRaw(...))\n"
    ),
    "media.bg_video_stream": (
        "Inbound video stream to the media BG video lane.\n"
        "\n"
        "Send ImageFrameRaw frames to this topic to render streamed background video.\n"
        "\n"
        "Typical usage:\n"
        "    writer = robot.media.stream.open_bg_video_stream_writer()\n"
        "    writer.write(ImageFrameRaw(...))\n"
    ),

    "motor.joints_state": (
        "Outbound stream of joint states.\n"
        "\n"
        "Frame type is JointStateFrame mapping motor_name -> state:\n"
        "  {position, velocity, effort, voltage, temperature}\n"
        "\n"
        "Typical usage:\n"
        "    # Callback-based\n"
        "    def on_state(frame: JointStateFrame):\n"
        "        print(frame.position('HeadYaw'))\n"
        "    sub = robot.motor.stream.on_joints_state(on_state)\n"
        "\n"
        "    # Reader-based\n"
        "    reader = robot.motor.stream.open_joints_state_reader()\n"
        "    frame = reader.read()\n"
    ),
    "motor.joints_error": (
        "Outbound stream of motor error flags (when present).\n"
        "\n"
        "Frame payload is a DictFrame mapping motor_name -> error flags:\n"
        "  {overload_limit?, voltage_limit?, temperature_limit?, sensor_failure?}\n"
        "\n"
        "Typical usage:\n"
        "    def on_error(frame):\n"
        "        print('Motor error:', frame.value)\n"
        "    sub = robot.motor.stream.on_joints_error(on_error)\n"
    ),
    "gesture.progress": (
        "Outbound stream of gesture playback progress.\n"
        "\n"
        "Publishes a DictFrame with fields:\n"
        "  percentage (float), time_us (int)\n"
        "\n"
        "Typical usage:\n"
        "    def on_progress(frame):\n"
        "        print(f\"{frame.value['percentage']:.1f}%\")\n"
        "    sub = robot.gesture.stream.on_progress(on_progress)\n"
    ),
    "motor.joints_command": (
        "Inbound stream of joint commands.\n"
        "\n"
        "Send JointCommandFrame mapping motor_name -> command:\n"
        "  {'position': float, 'velocity': float (optional)}\n"
        "\n"
        "Typical usage:\n"
        "    writer = robot.motor.stream.open_joints_command_writer()\n"
        "    cmd = JointCommandFrame()\n"
        "    cmd.set_joint('HeadYaw', position=30, velocity=40)\n"
        "    writer.write(cmd)\n"
    ),

    # ===========================================================
    # RPCs — MICROPHONE
    # ===========================================================

    "microphone.get_int_tuning": (
        "Get all readable Respeaker (internal mic array) tuning parameters.\n"
        "\n"
        "Returns a dictionary of every readable parameter exposed by the\n"
        "Respeaker controller (keys are parameter names, values are numeric).\n"
        "\n"
        "Returns:\n"
        "    dict: Mapping {param_name: value} for all readable params.\n"
        "\n"
        "Example:\n"
        "    params = robot.microphone.get_int_tuning()\n"
        "    print(params.get('AECNORM'))\n"
        "\n"
        "Notes:\n"
        "    If the Respeaker device is not available, may return an empty dict.\n"
    ),
    "microphone.set_int_tuning": (
        "Set a Respeaker (internal mic array) tuning parameter.\n"
        "\n"
        "Args:\n"
        "    name (str): Parameter name (e.g. 'AECNORM', 'AGCONOFF', ...).\n"
        "    value (float): Value to set.\n"
        "\n"
        "Returns:\n"
        "    bool: True if the parameter was set successfully.\n"
        "\n"
        "Example:\n"
        "    ok = robot.microphone.set_int_tuning(name='AGCONOFF', value=1.0)\n"
        "\n"
        "Notes:\n"
        "    Persistence is handled via config (microphone.tunning.*) applied at startup.\n"
    ),

    # ===========================================================
    # STREAMS — MICROPHONE
    # ===========================================================

    "microphone.int_audio_ch0": (
        "Internal microphone audio stream channel 0 (mono).\n"
        "\n"
        "AudioFrameRaw stream published by MicrophoneNode.\n"
        "Channel 0 is the processed/ASR channel.\n"
        "\n"
        "Typical usage:\n"
        "    def on_audio(frame: AudioFrameRaw):\n"
        "        process(frame.data)\n"
        "    sub = robot.microphone.stream.on_int_audio_ch0(on_audio, queue_size=10)\n"
        "\n"
        "    # Or use a reader directly\n"
        "    reader = robot.microphone.stream.open_int_audio_ch0_reader(queue_size=10)\n"
        "    frame = reader.read(timeout=3.0)\n"
    ),
    "microphone.int_audio_ch1": (
        "Internal microphone audio stream channel 1 (mono).\n"
        "\n"
        "AudioFrameRaw stream published by MicrophoneNode.\n"
        "Typically corresponds to physical mic 1 (raw), depending on ALSA layout.\n"
    ),
    "microphone.int_audio_ch2": (
        "Internal microphone audio stream channel 2 (mono).\n"
        "\n"
        "AudioFrameRaw stream published by MicrophoneNode.\n"
    ),
    "microphone.int_audio_ch3": (
        "Internal microphone audio stream channel 3 (mono).\n"
        "\n"
        "AudioFrameRaw stream published by MicrophoneNode.\n"
    ),
    "microphone.int_audio_ch4": (
        "Internal microphone audio stream channel 4 (mono).\n"
        "\n"
        "AudioFrameRaw stream published by MicrophoneNode.\n"
    ),
    "microphone.int_event": (
        "Internal microphone event stream (VAD + direction-of-arrival).\n"
        "\n"
        "Publishes DictFrame events when voice activity changes.\n"
        "Payload fields:\n"
        "    activity (bool): True when voice is detected.\n"
        "    direction (int): Estimated direction-of-arrival in degrees.\n"
        "\n"
        "Typical usage:\n"
        "    def on_evt(frame):\n"
        "        evt = frame.value\n"
        "        if evt.get('activity'):\n"
        "            print('Voice detected — DOA:', evt.get('direction'))\n"
        "    sub = robot.microphone.stream.on_int_event(on_evt, queue_size=2)\n"
        "\n"
        "Notes:\n"
        "    Stream delivery is 'latest' — events may be dropped if the consumer is slow.\n"
    ),
    "microphone.ext_audio_ch0": (
        "External microphone audio stream channel 0 (mono).\n"
        "\n"
        "AudioFrameRaw stream published only if microphone.external.enabled is True.\n"
        "\n"
        "Typical usage:\n"
        "    sub = robot.microphone.stream.on_ext_audio_ch0(cb, queue_size=10)\n"
    ),
}
