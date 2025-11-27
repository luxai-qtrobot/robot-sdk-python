# src/luxai/robot/core/config.py
from __future__ import annotations

from typing import Any, Dict, List, Type

from .. import __version__ as SDK_VERSION

# Service used for system/robot description
SYSTEM_DESCRIBE_SERVICE = "/robot/system/describe"

QTROBOT_CORE_APIS: Dict[str, Dict[str, Any]] = {
    # say_text
    "say_text": {
        "service_name": "/qt_robot/speech/say",
        "cancel_service_name": "/qt_robot/speech/stop",  # or None if unsupported
        "params": [
            # (param_name, type, default) – default is optional
            ("message", str),                        # required
        ],
        # Optional: purely for docs/type hints; we unwrap "response"
        "response_type": type(None),
        "since": "0.1.0",
        "deprecated": False,
        "deprecated_message": None,
        "robots": ["qtrobot-v3"],
        "doc": "Make Robot say the given text using TTS without lip movement.",
    },

    # configure speech
    "configure_speech": {
        "service_name": "/qt_robot/speech/config",
        "cancel_service_name": None,             # no cancel
        "params": [
            ("language", str, None),
            ("pitch", int, 100),
            ("speed", int, 100),
        ],
        "response_type": type(None),
        "since": "0.1.0",
        "deprecated": False,
        "deprecated_message": None,
        "robots": ["qtrobot-v3"],
        "doc": "Configure Robot speech parameters (language, pitch, speed).",
    },

    # You can add more later, e.g. show_emotion, play_gesture, etc.
    # "show_emotion": {...}
}

__all__ = [
    "SDK_VERSION",
    "QTROBOT_CORE_APIS",
    "SYSTEM_DESCRIBE_SERVICE",
]
