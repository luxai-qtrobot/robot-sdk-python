from __future__ import annotations

from typing import Dict

QTROBOT_CORE_API_DOCS: Dict[str, str] = {
    # ===========================================================
    # RPC APIs — MEDIA
    # ===========================================================

    "media.play_fg_audio_file": (
        "Play an audio file on the foreground (FG) audio lane.\n"
        "\n"
        "This plays the given URI via the media audio engine FG file player.\n"
        "Use the cancel RPC (cancel_service_name) to stop playback.\n"
        "\n"
        "Args:\n"
        "    uri (str): Audio file URI/path supported by the engine.\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback started successfully, False otherwise.\n"
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
    ),
    "media.get_fg_audio_volume": (
        "Get foreground (FG) audio lane volume.\n"
        "\n"
        "Returns:\n"
        "    float: Volume in range [0.0, 1.0].\n"
    ),

    "media.play_bg_audio_file": (
        "Play an audio file on the background (BG) audio lane.\n"
        "\n"
        "Args:\n"
        "    uri (str): Audio file URI/path supported by the engine.\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback started successfully, False otherwise.\n"
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
    ),
    "media.get_bg_audio_volume": (
        "Get background (BG) audio lane volume.\n"
        "\n"
        "Returns:\n"
        "    float: Volume in range [0.0, 1.0].\n"
    ),

    "media.play_fg_video_file": (
        "Play a video file on the foreground (FG) video lane.\n"
        "\n"
        "Args:\n"
        "    uri (str): Video file URI/path supported by the engine.\n"
        "    speed (float): Playback speed factor (default 1.0).\n"
        "    with_audio (bool): If True, play embedded audio track (default False).\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback started successfully, False otherwise.\n"
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
        "    value (float): Alpha in range [0.0, 1.0].\n"
        "\n"
        "Returns:\n"
        "    None\n"
    ),

    "media.play_bg_video_file": (
        "Play a video file on the background (BG) video lane.\n"
        "\n"
        "Args:\n"
        "    uri (str): Video file URI/path supported by the engine.\n"
        "    speed (float): Playback speed factor (default 1.0).\n"
        "    with_audio (bool): If True, play embedded audio track (default False).\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback started successfully, False otherwise.\n"
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
    ),
    "speaker.get_volume": (
        "Get the master speaker volume.\n"
        "\n"
        "Returns:\n"
        "    float: Volume in range [0.0, 1.0].\n"
    ),
    "speaker.mute": (
        "Mute the speaker output.\n"
        "\n"
        "Returns:\n"
        "    bool: True if succeeded, False otherwise.\n"
    ),
    "speaker.unmute": (
        "Unmute the speaker output.\n"
        "\n"
        "Returns:\n"
        "    bool: True if succeeded, False otherwise.\n"
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
    ),
    "face.show_emotion": (
        "Play an emotion video on the face background lane.\n"
        "\n"
        "Emotion resolves to an .avi file (emotion + '.avi' if not provided).\n"
        "Use cancel_service_name to stop the emotion playback.\n"
        "\n"
        "Args:\n"
        "    emotion (str): Emotion name or relative path (with/without .avi).\n"
        "    speed (float): Optional playback speed factor.\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback started, False otherwise.\n"
    ),
    "face.list_emotions": (
        "List available emotion video files under the emotions directory.\n"
        "\n"
        "Scans recursively and returns relative paths for .avi/.AVI files.\n"
        "\n"
        "Returns:\n"
        "    list: List[str] of emotion file paths.\n"
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
    ),
    "motor.set_calib": (
        "Set calibration offset for a motor.\n"
        "\n"
        "Args:\n"
        "    motor (str): Motor name.\n"
        "    offset (float): Offset in degrees.\n"
        "    store (bool): If True, persist to config (default False).\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
    ),
    "motor.calib_all": (
        "Run manual calibration procedure for all motors (writes offsets and stores them).\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
    ),
    "motor.set_velocity": (
        "Set default velocity for a motor (deg/s).\n"
        "\n"
        "Args:\n"
        "    motor (str): Motor name.\n"
        "    velocity (int): Velocity value; clamped/validated against motor max.\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
    ),
    "motor.on": (
        "Enable torque for a motor.\n"
        "\n"
        "Args:\n"
        "    motor (str): Motor name.\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
    ),
    "motor.off": (
        "Disable torque for a motor.\n"
        "\n"
        "Args:\n"
        "    motor (str): Motor name.\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
    ),
    "motor.on_all": (
        "Enable torque for all motors.\n"
        "\n"
        "Returns:\n"
        "    bool: True\n"
    ),
    "motor.off_all": (
        "Disable torque for all motors.\n"
        "\n"
        "Returns:\n"
        "    bool: True\n"
    ),
    "motor.home": (
        "Move a motor to its configured home position.\n"
        "\n"
        "Args:\n"
        "    motor (str): Motor name.\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
    ),
    "motor.home_all": (
        "Move all motors to their configured home positions.\n"
        "\n"
        "Returns:\n"
        "    bool: True\n"
    ),

    # ===========================================================
    # RPC APIs — GESTURE
    # ===========================================================

    "gesture.record": (
        "Start recording a gesture trajectory for selected motors.\n"
        "\n"
        "Records time-stamped joint positions and returns a trajectory dict.\n"
        "Use cancel_service_name to stop recording early.\n"
        "\n"
        "Args:\n"
        "    motors (list): List[str] motor names (order preserved).\n"
        "    release_motors (bool): If True, torque is disabled during recording.\n"
        "    delay_start_ms (int): Optional delay before recording starts.\n"
        "    timeout_ms (int): Optional max duration (ms).\n"
        "    refine_keyframe (bool): If True, compress to keyframes.\n"
        "    keyframe_pos_eps (float): Keyframe compression epsilon (deg).\n"
        "    keyframe_max_gap_us (int): Max allowed gap for compression (us).\n"
        "\n"
        "Returns:\n"
        "    dict: Trajectory dict with 'meta' and 'points'.\n"
    ),
    "gesture.stop_record": (
        "Stop recording a gesture trajectory.\n"
        "\n"
        "Args:\n"
        "    None\n"
        "\n"
        "Returns:\n"
        "    bool: True if recording was stopped, False if no recording in progress.\n"
    ),    
    "gesture.store_record": (
        "Store the last recorded gesture trajectory to an XML file.\n"
        "\n"
        "Args:\n"
        "    gesture (str): Gesture name/path (saved as <gesture>.xml).\n"
        "\n"
        "Returns:\n"
        "    bool: True if saved successfully.\n"
    ),
    "gesture.play": (
        "Play a gesture trajectory (keyframes dict).\n"
        "\n"
        "Use cancel_service_name to stop playback.\n"
        "\n"
        "Args:\n"
        "    keyframes (dict): Trajectory dict.\n"
        "    resample (bool): If True, resample for smooth playback.\n"
        "    rate_hz (float): Resample rate.\n"
        "    speed_factor (float): Playback speed multiplier.\n"
        "\n"
        "Returns:\n"
        "    bool: True if playback ran (or started) successfully.\n"
        "\n"
        "Notes:\n"
        "    Progress is published on the gesture.progress stream.\n"
    ),
    "gesture.play_file": (
        "Load a gesture XML file and play it.\n"
        "\n"
        "Use cancel_service_name to stop playback.\n"
        "\n"
        "Args:\n"
        "    gesture (str): Gesture name/path (with/without .xml).\n"
        "    speed_factor (float): Playback speed multiplier.\n"
        "\n"
        "Returns:\n"
        "    bool: True if loaded and played successfully.\n"
    ),
    "gesture.list_files": (
        "List available gesture XML files under the configured gesture directory.\n"
        "\n"
        "Returns:\n"
        "    list: List[str] of gesture file paths.\n"
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
    ),
    "tts.get_default_engine": (
        "Get the current default TTS engine id.\n"
        "\n"
        "Returns:\n"
        "    str: Default engine id.\n"
    ),
    "tts.list_engines": (
        "List loaded/available TTS engine ids.\n"
        "\n"
        "Returns:\n"
        "    list: List[str] of engine ids.\n"
    ),
    "tts.say_text": (
        "Synthesize and play plain text using a selected TTS engine.\n"
        "\n"
        "This call blocks until playback finishes (current implementation).\n"
        "Use cancel_service_name to interrupt playback.\n"
        "\n"
        "Args:\n"
        "    engine (str): Engine id to use.\n"
        "    text (str): Text to synthesize.\n"
        "    lang (str): Optional language code.\n"
        "    voice (str): Optional voice id/name.\n"
        "    rate (float): Optional speaking rate.\n"
        "    pitch (float): Optional pitch.\n"
        "    volume (float): Optional volume.\n"
        "    style (str): Optional style (engine dependent).\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
        "\n"
        "Notes:\n"
        "    Visemes may be scheduled to the FaceNode if connected.\n"
    ),
    "tts.say_ssml": (
        "Synthesize and play SSML using a selected TTS engine.\n"
        "\n"
        "This call blocks until playback finishes (current implementation).\n"
        "Use cancel_service_name to interrupt playback.\n"
        "\n"
        "Args:\n"
        "    engine (str): Engine id to use.\n"
        "    ssml (str): SSML markup.\n"
        "\n"
        "Returns:\n"
        "    bool: True on success.\n"
    ),
    "tts.set_config": (
        "Set engine-specific configuration parameters.\n"
        "\n"
        "Args:\n"
        "    engine (str): Engine id.\n"
        "    config (dict): Key/value config map.\n"
        "\n"
        "Returns:\n"
        "    bool: True if engine accepted configuration.\n"
    ),
    "tts.get_config": (
        "Get engine-specific configuration parameters.\n"
        "\n"
        "Args:\n"
        "    engine (str): Engine id.\n"
        "\n"
        "Returns:\n"
        "    dict: Current engine configuration map.\n"
    ),
    "tts.get_languages": (
        "Get supported language codes for a TTS engine.\n"
        "\n"
        "Args:\n"
        "    engine (str): Engine id.\n"
        "\n"
        "Returns:\n"
        "    list: List[str] language codes.\n"
    ),
    "tts.get_voices": (
        "Get supported voices for a TTS engine.\n"
        "\n"
        "Args:\n"
        "    engine (str): Engine id.\n"
        "\n"
        "Returns:\n"
        "    list: List[dict] voice info dicts (id, lang, gender, display_name, ...).\n"
    ),
    "tts.supports_ssml": (
        "Check whether the selected TTS engine supports SSML.\n"
        "\n"
        "Args:\n"
        "    engine (str): Engine id.\n"
        "\n"
        "Returns:\n"
        "    bool: True if SSML is supported.\n"
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
        "    Use media.cancel_fg_audio_stream / pause / resume to control the pipeline.\n"
    ),
    "media.bg_audio_stream": (
        "Inbound audio stream to the media BG audio lane.\n"
        "\n"
        "Send AudioFrameRaw frames to this topic to play streamed background audio.\n"
        "\n"
        "Notes:\n"
        "    Use media.cancel_bg_audio_stream / pause / resume to control the pipeline.\n"
    ),
    "media.fg_video_stream": (
        "Inbound video stream to the media FG video lane.\n"
        "\n"
        "Send ImageFrameRaw frames to this topic to render streamed foreground video.\n"
    ),
    "media.bg_video_stream": (
        "Inbound video stream to the media BG video lane.\n"
        "\n"
        "Send ImageFrameRaw frames to this topic to render streamed background video.\n"
    ),

    "motor.joints_state": (
        "Outbound stream of joint states.\n"
        "\n"
        "Frame payload is a DictFrame mapping motor_name -> state dict:\n"
        "  {position, velocity, effort, voltage, temprature}\n"
        "\n"
        "Typical usage:\n"
        "    sub = robot.motor.stream.on_joints_state(callback)\n"
        "    reader = robot.motor.stream.open_joints_state_reader()\n"
    ),
    "motor.joints_error": (
        "Outbound stream of motor error flags (when present).\n"
        "\n"
        "Frame payload is a DictFrame mapping motor_name -> error flags:\n"
        "  {overload_limit?, voltage_limit?, temperature_limit?, sensor_failure?}\n"
    ),
    "gesture.progress": (
        "Outbound stream of gesture playback progress.\n"
        "\n"
        "Publishes a DictFrame with fields:\n"
        "  percentage (float), time_us (int)\n"
    ),
    "motor.joints_command": (
        "Inbound stream of joint commands.\n"
        "\n"
        "Send DictFrame mapping motor_name -> command dict:\n"
        "  {'position': float, 'velocity': float(optional)}\n"
        "\n"
        "Typical usage:\n"
        "    writer = robot.motor.stream.open_joints_command_writer()\n"
        "    writer.write(DictFrame({...}))\n"
    ),
}