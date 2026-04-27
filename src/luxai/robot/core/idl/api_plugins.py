from __future__ import annotations

from typing import Any, Dict, List, Type

QTROBOT_PLUGINS_APIS: Dict[str, Dict[str, Any]] = {
    "rpc": {
        # =========================
        # Camera Realsense RPCs
        # =========================
        "camera.get_color_intrinsics": {
            "service_name": "/camera/color/intrinsics",
            "cancel_service_name": None,
            "params": [],
            "response_type": dict,            
            "provider": "realsense-driver",
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,            
            "robots": ["qtrobot-v3"],
            "doc": (
                "Get color camera intrinsic parameters.\n"
                "\n"
                "Returns:\n"
                "    dict: Intrinsics dict (fx, fy, ppx, ppy, width, height, model, coeffs).\n"
                "\n"
                "Example:\n"
                "    intr = robot.camera.get_color_intrinsics()\n"
            )
        },
        "camera.get_depth_intrinsics": {
            "service_name": "/camera/depth/intrinsics",
            "cancel_service_name": None,
            "params": [],
            "response_type": dict,            
            "provider": "realsense-driver",
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,            
            "robots": ["qtrobot-v3"],
            "doc": (
                "Get depth camera intrinsic parameters.\n"
                "\n"
                "Returns:\n"
                "    dict: Intrinsics dict (fx, fy, ppx, ppy, width, height, model, coeffs).\n"
                "\n"
                "Example:\n"
                "    intr = robot.camera.get_depth_intrinsics()\n"
            )
        },
        "camera.get_depth_scale": {
            "service_name": "/camera/depth/scale",
            "cancel_service_name": None,
            "params": [],
            "response_type": dict,            
            "provider": "realsense-driver",
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,            
            "robots": ["qtrobot-v3"],
            "doc": (
                "Get the depth scale factor (metres per depth unit).\n"
                "\n"
                "Returns:\n"
                "    dict: {'scale': float} where scale converts raw depth units to metres.\n"
                "\n"
                "Example:\n"
                "    info = robot.camera.get_depth_scale()\n"
                "    scale = info['scale']\n"
            )
        },

        # =========================
        # ASR Azure RPCs
        # =========================
        "asr.configure_azure": {
            "service_name": "/asr-azure/configure",
            "cancel_service_name": None,
            "params": [
                ("subscription", str),
                ("region", str),
                ("languages", List[str], ["en-US"]),
                ("silence_timeout", float, 0.2),
                ("use_vad", bool, False),
                ("continuous_mode", bool, False)
            ],
            "response_type": bool,
            "local": True,
            "provider": "asr-azure",
            "install_hint": "pip install luxai-robot[asr-azure]",
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,            
            "robots": ["qtrobot-v3"],
            "doc": (
                "Configure the Azure ASR engine with credentials and recognition settings.\n"
                "\n"
                "Must be called once before using ``recognize_azure()`` or subscribing\n"
                "to the ``asr.azure_speech`` / ``asr.azure_event`` streams.\n"
                "\n"
                "Args:\n"
                "    subscription (str): Azure Speech subscription key.\n"
                "    region (str): Azure Speech region (e.g. 'westeurope').\n"
                "    languages (list): Language codes to recognise (default ['en-US']).\n"
                "    silence_timeout (float): Silence end-of-speech threshold in seconds (default 0.2).\n"
                "    use_vad (bool): Enable voice-activity detection (default False).\n"
                "    continuous_mode (bool): Enable continuous recognition mode (default False).\n"
                "\n"
                "Returns:\n"
                "    bool: True if configured successfully.\n"
                "\n"
                "Example:\n"
                "    ok = robot.asr.configure_azure(\n"
                "        subscription='<key>',\n"
                "        region='westeurope',\n"
                "        continuous_mode=True,\n"
                "        use_vad=True,\n"
                "    )\n"
            )
        },
        "asr.recognize_azure": {
            "service_name": "/asr-azure/recognize",
            "cancel_service_name": "/asr-azure/recognize/cancel",
            "params": [],
            "response_type": dict,
            "local": True,
            "provider": "asr-azure",
            "install_hint": "pip install luxai-robot[asr-azure]",
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,            
            "robots": ["qtrobot-v3"],
            "doc": (
                "Perform a single speech recognition with the Azure ASR engine.\n"
                "\n"
                "Blocks until a complete utterance is recognised and returns the result.\n"
                "For non-blocking use, call ``recognize_azure_async()`` which returns an\n"
                ":class:`ActionHandle` — call ``.cancel()`` on it to abort recognition.\n"
                "\n"
                "Returns:\n"
                "    dict: Recognition result with fields such as 'text', 'confidence', etc.\n"
                "\n"
                "Examples:\n"
                "    # Blocking\n"
                "    result = robot.asr.recognize_azure()\n"
                "    print(result.get('text'))\n"
                "\n"
                "    # Non-blocking\n"
                "    h = robot.asr.recognize_azure_async()\n"
                "    result = h.result()\n"
                "    print(result.get('text'))\n"
            ),
        },
        # =========================
        # ASR Riva RPCs
        # =========================
        "asr.configure_riva": {
            "service_name": "/asr-riva/configure",
            "cancel_service_name": None,
            "params": [
                ("server", str, "localhost:50051"),
                ("language", str, "en-US"),
                ("use_ssl", bool, False),
                ("ssl_cert", str, None),
                ("profanity_filter", bool, False),
                ("automatic_punctuation", bool, True),
                ("use_vad", bool, False),
                ("continuous_mode", bool, False),
            ],
            "response_type": bool,
            "local": True,
            "provider": "asr-riva",
            "install_hint": "pip install luxai-robot[asr-riva]",
            "since": "0.5.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Configure the Nvidia Riva ASR engine with server address and recognition settings.\n"
                "\n"
                "Must be called once before using ``recognize_riva()`` or subscribing\n"
                "to the ``asr.riva_speech`` / ``asr.riva_event`` streams.\n"
                "\n"
                "Args:\n"
                "    server (str): Riva server address (default 'localhost:50051').\n"
                "    language (str): BCP-47 language code (default 'en-US').\n"
                "    use_ssl (bool): Use SSL/TLS for the gRPC connection (default False).\n"
                "    ssl_cert (str): Path to SSL certificate file (default None).\n"
                "    profanity_filter (bool): Enable profanity filtering (default False).\n"
                "    automatic_punctuation (bool): Enable automatic punctuation (default True).\n"
                "    use_vad (bool): Enable client-side voice-activity detection (default False).\n"
                "    continuous_mode (bool): Enable continuous recognition mode (default False).\n"
                "\n"
                "Returns:\n"
                "    bool: True if configured successfully.\n"
                "\n"
                "Example:\n"
                "    ok = robot.asr.configure_riva(\n"
                "        server='localhost:50051',\n"
                "        language='en-US',\n"
                "        continuous_mode=True,\n"
                "        use_vad=True,\n"
                "    )\n"
            ),
        },
        "asr.recognize_riva": {
            "service_name": "/asr-riva/recognize",
            "cancel_service_name": "/asr-riva/recognize/cancel",
            "params": [],
            "response_type": dict,
            "local": True,
            "provider": "asr-riva",
            "install_hint": "pip install luxai-robot[asr-riva]",
            "since": "0.5.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Perform a single speech recognition with the Nvidia Riva ASR engine.\n"
                "\n"
                "Blocks until a complete utterance is recognised and returns the result.\n"
                "For non-blocking use, call ``recognize_riva_async()`` which returns an\n"
                ":class:`ActionHandle` — call ``.cancel()`` on it to abort recognition.\n"
                "\n"
                "Returns:\n"
                "    dict: Recognition result with fields 'text' and 'language'.\n"
                "\n"
                "Examples:\n"
                "    # Blocking\n"
                "    result = robot.asr.recognize_riva()\n"
                "    print(result.get('text'))\n"
                "\n"
                "    # Non-blocking\n"
                "    h = robot.asr.recognize_riva_async()\n"
                "    result = h.result()\n"
                "    print(result.get('text'))\n"
            ),
        },

        # =========================
        # ASR Groq RPCs
        # =========================
        "asr.configure_groq": {
            "service_name": "/asr-groq/configure",
            "cancel_service_name": None,
            "params": [
                ("api_key", str),
                ("language", str, "en"),
                ("context_prompt", str, None),
                ("silence_timeout", float, 0.5),
                ("use_vad", bool, True),
                ("continuous_mode", bool, False),
            ],
            "response_type": bool,
            "local": True,
            "provider": "asr-groq",
            "install_hint": "pip install luxai-robot[asr-groq]",
            "since": "0.5.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Configure the Groq Whisper ASR engine.\n"
                "\n"
                "Must be called once before using ``recognize_groq()`` or subscribing\n"
                "to the ``asr.groq_speech`` / ``asr.groq_event`` streams.\n"
                "\n"
                "Args:\n"
                "    api_key (str): Groq API key.\n"
                "    language (str): ISO-639-1 language code (e.g. 'en', 'fr'). Default 'en'.\n"
                "    context_prompt (str): Optional domain hint for Whisper (max 224 chars).\n"
                "    silence_timeout (float): Seconds of silence that end an utterance (default 0.5).\n"
                "    use_vad (bool): Enable client-side voice-activity detection (default True).\n"
                "    continuous_mode (bool): Enable continuous recognition mode (default False).\n"
                "\n"
                "Returns:\n"
                "    bool: True if configured successfully.\n"
                "\n"
                "Example:\n"
                "    ok = robot.asr.configure_groq(\n"
                "        api_key='<your-groq-api-key>',\n"
                "        language='en',\n"
                "        continuous_mode=True,\n"
                "    )\n"
            ),
        },
        "asr.recognize_groq": {
            "service_name": "/asr-groq/recognize",
            "cancel_service_name": "/asr-groq/recognize/cancel",
            "params": [],
            "response_type": dict,
            "local": True,
            "provider": "asr-groq",
            "install_hint": "pip install luxai-robot[asr-groq]",
            "since": "0.5.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Perform a single speech recognition with the Groq Whisper ASR engine.\n"
                "\n"
                "Blocks until voice activity is detected, one utterance is captured\n"
                "(ended by silence), and Groq transcribes it via the Whisper API.\n"
                "For non-blocking use, call ``recognize_groq_async()`` which returns an\n"
                ":class:`ActionHandle` — call ``.cancel()`` on it to abort recognition.\n"
                "\n"
                "Returns:\n"
                "    dict: Recognition result with fields 'text' and 'language'.\n"
                "\n"
                "Examples:\n"
                "    # Blocking\n"
                "    result = robot.asr.recognize_groq()\n"
                "    print(result.get('text'))\n"
                "\n"
                "    # Non-blocking\n"
                "    h = robot.asr.recognize_groq_async()\n"
                "    result = h.result()\n"
                "    print(result.get('text'))\n"
            ),
        },
        # =========================
        # Kinematics RPCs
        # =========================
        "kinematics.configure": {
            "service_name": "/kinematics/configure",
            "cancel_service_name": None,
            "params": [
                ("fx",             float, 419.76220703125),
                ("fy",             float, 419.3450927734375),
                ("ppx",            float, 421.1879577636719),
                ("ppy",            float, 247.27752685546875),
                ("img_cx",         float, 424.0),
                ("img_cy",         float, 240.0),
                ("camera_height",  float, 0.6),
                ("motor_timeout",  float, 20.0),
            ],
            "response_type": bool,
            "local": True,
            "provider": "kinematics",
            "since": "0.6.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Configure the kinematics plugin (optional — defaults match the QTrobot hardware).\n"
                "\n"
                "Args:\n"
                "    fx (float): Camera focal length x (default 376.4).\n"
                "    fy (float): Camera focal length y (default 376.1).\n"
                "    ppx (float): Camera principal point x (default 314.6).\n"
                "    ppy (float): Camera principal point y (default 255.6).\n"
                "    camera_height (float): Camera height above robot base frame in metres (default 0.6).\n"
                "    motor_timeout (float): Hard-cap wait time in seconds for joint motion to complete (default 20.0).\n"
                "\n"
                "Returns:\n"
                "    bool: True if configured successfully.\n"
                "\n"
                "Example:\n"
                "    robot.kinematics.configure(motor_timeout=15.0)\n"
            ),
        },
        "kinematics.look_at_point": {
            "service_name": "/kinematics/look_at_point",
            "cancel_service_name": "/kinematics/look_at_point/cancel",
            "params": [
                ("x",          float),
                ("y",          float),
                ("z",          float),
                ("only_gaze",  bool,  False),
                ("velocity",   float, 0.0),
            ],
            "response_type": bool,
            "local": True,
            "provider": "kinematics",
            "since": "0.6.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Move the robot head to look at a 3-D point in the robot base frame.\n"
                "\n"
                "The robot base frame origin is at the bottom of the robot.\n"
                "Sends an eye-gaze command and (unless only_gaze=True) a head joint command,\n"
                "then blocks until the head motors stop.\n"
                "\n"
                "Args:\n"
                "    x (float): Forward distance from robot base (metres).\n"
                "    y (float): Lateral distance (positive = left, negative = right).\n"
                "    z (float): Height above base (metres).\n"
                "    only_gaze (bool): If True, move eyes only — do not move the head (default False).\n"
                "    velocity (float): Joint velocity override in motor units; 0 = use robot default (default 0).\n"
                "\n"
                "Returns:\n"
                "    bool: True on completion.\n"
                "\n"
                "Examples:\n"
                "    # Blocking\n"
                "    robot.kinematics.look_at_point(0.8, 0.0, 1.2)\n"
                "\n"
                "    # Non-blocking\n"
                "    h = robot.kinematics.look_at_point_async(0.8, 0.0, 1.2)\n"
                "    h.wait()\n"
                "\n"
                "    # Eyes only\n"
                "    robot.kinematics.look_at_point(0.8, 0.3, 1.0, only_gaze=True)\n"
            ),
        },
        "kinematics.look_at_pixel": {
            "service_name": "/kinematics/look_at_pixel",
            "cancel_service_name": "/kinematics/look_at_pixel/cancel",
            "params": [
                ("u",          int),
                ("v",          int),
                ("depth",      float, 1.0),
                ("only_gaze",  bool,  False),
                ("velocity",   float, 0.0),
            ],
            "response_type": bool,
            "local": True,
            "provider": "kinematics",
            "since": "0.6.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Move the robot head to look at a camera pixel.\n"
                "\n"
                "Converts the pixel (u, v) and depth into a 3-D point using the current\n"
                "head joint angles and the camera intrinsics, then calls look_at_point.\n"
                "\n"
                "Args:\n"
                "    u (int): Pixel column (horizontal).\n"
                "    v (int): Pixel row (vertical).\n"
                "    depth (float): Distance to the pixel in metres (default 1.0).\n"
                "    only_gaze (bool): If True, move eyes only (default False).\n"
                "    velocity (float): Joint velocity override; 0 = robot default (default 0).\n"
                "\n"
                "Returns:\n"
                "    bool: True on completion.\n"
                "\n"
                "Example:\n"
                "    robot.kinematics.look_at_pixel(320, 240, depth=1.5)\n"
            ),
        },
        "kinematics.reach_right": {
            "service_name": "/kinematics/reach_right",
            "cancel_service_name": "/kinematics/reach_right/cancel",
            "params": [
                ("x",        float),
                ("y",        float),
                ("z",        float),
                ("velocity", float, 0.0),
            ],
            "response_type": bool,
            "local": True,
            "provider": "kinematics",
            "since": "0.6.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Move the right arm to reach a 3-D point in the robot base frame.\n"
                "\n"
                "Solves inverse kinematics for the right arm and blocks until the arm motors stop.\n"
                "If the point is outside the reachable workspace the arm moves to the closest\n"
                "reachable configuration (joint limits are clamped automatically).\n"
                "\n"
                "Args:\n"
                "    x (float): Forward distance from robot base (metres).\n"
                "    y (float): Lateral distance (negative = right side).\n"
                "    z (float): Height above base (metres).\n"
                "    velocity (float): Joint velocity override; 0 = robot default (default 0).\n"
                "\n"
                "Returns:\n"
                "    bool: True on completion.\n"
                "\n"
                "Example:\n"
                "    robot.kinematics.reach_right(0.3, -0.2, 0.5)\n"
            ),
        },
        "kinematics.reach_left": {
            "service_name": "/kinematics/reach_left",
            "cancel_service_name": "/kinematics/reach_left/cancel",
            "params": [
                ("x",        float),
                ("y",        float),
                ("z",        float),
                ("velocity", float, 0.0),
            ],
            "response_type": bool,
            "local": True,
            "provider": "kinematics",
            "since": "0.6.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Move the left arm to reach a 3-D point in the robot base frame.\n"
                "\n"
                "Solves inverse kinematics for the left arm and blocks until the arm motors stop.\n"
                "If the point is outside the reachable workspace the arm moves to the closest\n"
                "reachable configuration (joint limits are clamped automatically).\n"
                "\n"
                "Args:\n"
                "    x (float): Forward distance from robot base (metres).\n"
                "    y (float): Lateral distance (positive = left side).\n"
                "    z (float): Height above base (metres).\n"
                "    velocity (float): Joint velocity override; 0 = robot default (default 0).\n"
                "\n"
                "Returns:\n"
                "    bool: True on completion.\n"
                "\n"
                "Example:\n"
                "    robot.kinematics.reach_left(0.3, 0.2, 0.5)\n"
            ),
        },
        "kinematics.aim_at_point": {
            "service_name": "/kinematics/aim_at_point",
            "cancel_service_name": "/kinematics/aim_at_point/cancel",
            "params": [
                ("x",        float),
                ("y",        float),
                ("z",        float),
                ("velocity", float, 0.0),
            ],
            "response_type": bool,
            "local": True,
            "provider": "kinematics",
            "since": "0.6.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Point at a 3-D location in the robot base frame, auto-selecting the arm.\n"
                "\n"
                "The arm is chosen automatically: left arm if y >= 0, right arm if y < 0.\n"
                "Blocks until the arm motors stop.\n"
                "\n"
                "Args:\n"
                "    x (float): Forward distance from robot base (metres).\n"
                "    y (float): Lateral distance (positive = left, negative = right).\n"
                "    z (float): Height above base (metres).\n"
                "    velocity (float): Joint velocity override; 0 = robot default (default 0).\n"
                "\n"
                "Returns:\n"
                "    bool: True on completion.\n"
                "\n"
                "Example:\n"
                "    robot.kinematics.aim_at_point(0.5, 0.0, 1.0)\n"
            ),
        },
        "kinematics.aim_at_pixel": {
            "service_name": "/kinematics/aim_at_pixel",
            "cancel_service_name": "/kinematics/aim_at_pixel/cancel",
            "params": [
                ("u",        int),
                ("v",        int),
                ("depth",    float, 1.0),
                ("velocity", float, 0.0),
            ],
            "response_type": bool,
            "local": True,
            "provider": "kinematics",
            "since": "0.6.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Point at a camera pixel, auto-selecting the arm.\n"
                "\n"
                "Converts the pixel (u, v) and depth into a 3-D point using the current\n"
                "head joint angles and camera intrinsics, then calls aim_at_point.\n"
                "\n"
                "Args:\n"
                "    u (int): Pixel column (horizontal).\n"
                "    v (int): Pixel row (vertical).\n"
                "    depth (float): Distance to the pixel in metres (default 1.0).\n"
                "    velocity (float): Joint velocity override; 0 = robot default (default 0).\n"
                "\n"
                "Returns:\n"
                "    bool: True on completion.\n"
                "\n"
                "Example:\n"
                "    robot.kinematics.aim_at_pixel(320, 240, depth=1.0)\n"
            ),
        },
        "kinematics.pixel_to_point": {
            "service_name": "/kinematics/pixel_to_point",
            "cancel_service_name": None,
            "params": [
                ("u",     int),
                ("v",     int),
                ("depth", float, 1.0),
            ],
            "response_type": dict,
            "local": True,
            "provider": "kinematics",
            "since": "0.6.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": (
                "Convert a camera pixel to a 3-D point in the robot base frame.\n"
                "\n"
                "Uses the current head joint angles and the configured camera intrinsics.\n"
                "Returns immediately — this is a pure computation with no motor movement.\n"
                "\n"
                "Args:\n"
                "    u (int): Pixel column (horizontal).\n"
                "    v (int): Pixel row (vertical).\n"
                "    depth (float): Distance to the pixel in metres (default 1.0).\n"
                "\n"
                "Returns:\n"
                "    dict: {'x': float, 'y': float, 'z': float} in robot base frame (metres).\n"
                "\n"
                "Example:\n"
                "    pt = robot.kinematics.pixel_to_point(320, 240, depth=1.2)\n"
                "    print(pt['x'], pt['y'], pt['z'])\n"
            ),
        },

    },  # end of rpc

    # STREAM SECTION
    "stream": {
        # -----------------------------------
        #  Reaslsense Camera streams
        # -----------------------------------
        "camera.color": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "topic": "/camera/color/image",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "realsense-driver",            
            "doc": (
                "Outbound color image stream from the RealSense camera.\n"
                "\n"
                "Frame type is ImageFrameRaw (BGR, width x height x 3).\n"
                "\n"
                "Typical usage:\n"
                "    reader = robot.camera.stream.open_color_reader()\n"
                "    frame = reader.read(timeout=3.0)\n"
            )
        },
        "camera.depth": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "topic": "/camera/depth/image",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "realsense-driver",            
            "doc": (
                "Outbound depth image stream from the RealSense camera.\n"
                "\n"
                "Frame type is ImageFrameRaw (16-bit depth, width x height).\n"
                "\n"
                "Typical usage:\n"
                "    reader = robot.camera.stream.open_depth_reader()\n"
                "    frame = reader.read(timeout=3.0)\n"
            )
        },
        "camera.depth_aligned": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "topic": "/camera/depth/aligned/image",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "realsense-driver",
            "doc": (
                "Outbound depth image aligned to the color frame from the RealSense camera.\n"
                "\n"
                "Frame type is ImageFrameRaw (16-bit depth, same resolution as color).\n"
                "\n"
                "Typical usage:\n"
                "    reader = robot.camera.stream.open_depth_aligned_reader()\n"
                "    frame = reader.read(timeout=3.0)\n"
            )
        },
        "camera.depth_color": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "topic": "/camera/depth/color/image",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "realsense-driver",
            "doc": (
                "Outbound false-colour depth image stream from the RealSense camera.\n"
                "\n"
                "Frame type is ImageFrameRaw (BGR, colourised for visualisation).\n"
                "\n"
                "Typical usage:\n"
                "    reader = robot.camera.stream.open_depth_color_reader()\n"
                "    frame = reader.read(timeout=3.0)\n"
            )
        },
        "camera.gyro": {
            "direction": "out",
            "frame_type": "ListFrame",
            "topic": "/camera/gyro",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "realsense-driver",
            "doc": (
                "Outbound gyroscope stream from the RealSense IMU.\n"
                "\n"
                "Frame type is ListFrame: [x, y, z] angular velocity (rad/s).\n"
                "\n"
                "Typical usage:\n"
                "    def on_gyro(frame):\n"
                "        print(frame.value)  # [x, y, z]\n"
                "    sub = robot.camera.stream.on_gyro(on_gyro)\n"
            )
        },
        "camera.acceleration": {
            "direction": "out",
            "frame_type": "ListFrame",
            "topic": "/camera/acceleration",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "realsense-driver",
            "doc": (
                "Outbound accelerometer stream from the RealSense IMU.\n"
                "\n"
                "Frame type is ListFrame: [x, y, z] linear acceleration (m/s²).\n"
                "\n"
                "Typical usage:\n"
                "    def on_accel(frame):\n"
                "        print(frame.value)  # [x, y, z]\n"
                "    sub = robot.camera.stream.on_acceleration(on_accel)\n"
            )
        },


        # -----------------------------------
        #  ASR Azure streams
        # -----------------------------------
        "asr.azure_speech": {
            "direction": "out",
            "frame_type": "DictFrame",
            "topic": "/asr-azure/speech",
            "local": True,
            "provider": "asr-azure",
            "install_hint": "pip install luxai-robot[asr-azure]",
            "doc": (
                "Outbound stream of recognised speech segments from Azure ASR.\n"
                "\n"
                "Published in both one-shot (``recognize_azure()``) and continuous modes.\n"
                "Frame type is DictFrame with fields: 'text', 'confidence', 'language', etc.\n"
                "\n"
                "Typical usage:\n"
                "    def on_speech(frame):\n"
                "        print(frame.value.get('text'))\n"
                "    sub = robot.asr.stream.on_azure_speech(on_speech)\n"
            ),
        },        
        "asr.azure_event": {
            "direction": "out",
            "frame_type": "StringFrame",
            "topic": "/asr-azure/event",
            "local": True,
            "provider": "asr-azure",
            "install_hint": "pip install luxai-robot[asr-azure]",
            "doc": (
                "Outbound stream of speech recognition lifecycle events from Azure ASR.\n"
                "\n"
                "Frame type is StringFrame. Possible values include:\n"
                "  'recognizing', 'recognized', 'canceled', 'session_started', 'session_stopped'.\n"
                "\n"
                "Typical usage:\n"
                "    def on_event(frame):\n"
                "        print(frame.value)  # e.g. 'recognized'\n"
                "    sub = robot.asr.stream.on_azure_event(on_event)\n"
            ),
        },

        # -----------------------------------
        #  ASR Riva streams
        # -----------------------------------
        "asr.riva_speech": {
            "direction": "out",
            "frame_type": "DictFrame",
            "topic": "/asr-riva/speech",
            "local": True,
            "provider": "asr-riva",
            "install_hint": "pip install luxai-robot[asr-riva]",
            "doc": (
                "Outbound stream of recognised speech segments from Nvidia Riva ASR.\n"
                "\n"
                "Published in both one-shot (``recognize_riva()``) and continuous modes.\n"
                "Frame type is DictFrame with fields: 'text' and 'language'.\n"
                "\n"
                "Typical usage:\n"
                "    def on_speech(frame):\n"
                "        print(frame.value.get('text'))\n"
                "    sub = robot.asr.stream.on_riva_speech(on_speech)\n"
            ),
        },
        "asr.riva_event": {
            "direction": "out",
            "frame_type": "StringFrame",
            "topic": "/asr-riva/event",
            "local": True,
            "provider": "asr-riva",
            "install_hint": "pip install luxai-robot[asr-riva]",
            "doc": (
                "Outbound stream of speech recognition lifecycle events from Nvidia Riva ASR.\n"
                "\n"
                "Frame type is StringFrame. Possible values:\n"
                "  'STARTED', 'RECOGNIZING', 'RECOGNIZED', 'STOPPED', 'CANCELED'.\n"
                "\n"
                "Typical usage:\n"
                "    def on_event(frame):\n"
                "        print(frame.value)  # e.g. 'RECOGNIZED'\n"
                "    sub = robot.asr.stream.on_riva_event(on_event)\n"
            ),
        },

        # -----------------------------------
        #  ASR Groq streams
        # -----------------------------------
        "asr.groq_speech": {
            "direction": "out",
            "frame_type": "DictFrame",
            "topic": "/asr-groq/speech",
            "local": True,
            "provider": "asr-groq",
            "install_hint": "pip install luxai-robot[asr-groq]",
            "doc": (
                "Outbound stream of transcribed speech segments from Groq Whisper ASR.\n"
                "\n"
                "Published in both one-shot (``recognize_groq()``) and continuous modes.\n"
                "Frame type is DictFrame with fields: 'text' and 'language'.\n"
                "\n"
                "Typical usage:\n"
                "    def on_speech(frame):\n"
                "        print(frame.value.get('text'))\n"
                "    sub = robot.asr.stream.on_groq_speech(on_speech)\n"
            ),
        },
        "asr.groq_event": {
            "direction": "out",
            "frame_type": "StringFrame",
            "topic": "/asr-groq/event",
            "local": True,
            "provider": "asr-groq",
            "install_hint": "pip install luxai-robot[asr-groq]",
            "doc": (
                "Outbound stream of speech recognition lifecycle events from Groq Whisper ASR.\n"
                "\n"
                "Frame type is StringFrame. Possible values:\n"
                "  'STARTED', 'RECOGNIZING', 'RECOGNIZED', 'STOPPED', 'CANCELED'.\n"
                "\n"
                "Typical usage:\n"
                "    def on_event(frame):\n"
                "        print(frame.value)  # e.g. 'RECOGNIZED'\n"
                "    sub = robot.asr.stream.on_groq_event(on_event)\n"
            ),
        },

        # -----------------------------------
        #  Human Detector streams
        # -----------------------------------
        "perception.human_presence": {
            "direction": "out",
            "frame_type": "DictFrame",
            "topic": "/human/presence",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "human-detector",
            "doc": (
                "Outbound stream of detected human presence data.\n"
                "\n"
                "Frame type is DictFrame with field 'persons': a dict keyed by person ID,\n"
                "each containing body, face, voice, and engagement information.\n"
                "\n"
                "Typical usage:\n"
                "    def on_presence(frame):\n"
                "        persons = frame.value.get('persons', {})\n"
                "    sub = robot.perception.stream.on_human_presence(on_presence)\n"
            ),
        },
        "perception.human_annotated_image": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "topic": "/human/annotated_image",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "human-detector",
            "doc": (
                "Outbound annotated image stream from the human detector.\n"
                "\n"
                "Frame type is ImageFrameRaw (BGR, same resolution as color camera).\n"
                "Annotations include YOLO pose skeleton, head orientation arrow, and 3D position label.\n"
                "Only published when stream_annotated_image=true in the detector config.\n"
                "\n"
                "Typical usage:\n"
                "    reader = robot.perception.stream.open_human_annotated_image_reader()\n"
                "    frame = reader.read(timeout=3.0)\n"
            ),
        },

    }
}