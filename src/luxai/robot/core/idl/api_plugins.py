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

    }
}