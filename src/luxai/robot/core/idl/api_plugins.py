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
            "doc": "Get Camera color intrinsics parameters."
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
            "doc": "Get Camera depth intrinsics parameters."
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
            "doc": "Get Camera depth scale value."
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
            "doc": "configure Azure ASR"
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
            "doc":  "Perform one-shot recognition with Azure ASR.",
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
            "doc": "Camera color image streaming"
        },
        "camera.depth": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "topic": "/camera/depth/image",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "realsense-driver",            
            "doc": "Camera depth image streaming"
        },
        "camera.depth_aligned": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "topic": "/camera/depth/aligned/image",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "realsense-driver",
            "doc": "Camera aligned depth image streaming"
        },
        "camera.depth_color": {
            "direction": "out",
            "frame_type": "ImageFrameRaw",
            "topic": "/camera/depth/color/image",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "realsense-driver",
            "doc": "Camera colorized depth image streaming"
        },
        "camera.gyro": {
            "direction": "out",
            "frame_type": "ListFrame",
            "topic": "/camera/gyro",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "realsense-driver",
            "doc": "Camera gyro streaming"
        },
        "camera.acceleration": {
            "direction": "out",
            "frame_type": "ListFrame",
            "topic": "/camera/acceleration",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "provider": "realsense-driver",
            "doc": "Camera acceleration streaming"
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
            "doc": "Recognized speech segments from Azure ASR.",
        },        
        "asr.azure_event": {
            "direction": "out",
            "frame_type": "StringFrame",
            "topic": "/asr-azure/event",
            "local": True,
            "provider": "asr-azure",
            "install_hint": "pip install luxai-robot[asr-azure]",
            "doc": "Speech recognition events from Azure ASR.",
        },

    }
}