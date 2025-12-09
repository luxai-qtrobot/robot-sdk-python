from __future__ import annotations

from typing import Any, Dict, List, Type

from .api_doc import QTROBOT_API_DOCS

QTROBOT_CORE_APIS: Dict[str, Dict[str, Any]] = {
    # =========================
    # SPEECH  -> qtrobot.speech.*
    # =========================
    "rpc": {
        # qtrobot.speech.say()
        "speech.say": {
            "service_name": "/qt_robot/speech/say",
            "cancel_service_name": "/qt_robot/speech/stop",
            "params": [
                ("message", str),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("speech.say", ""),
        },

        "speech.talk": {
            "service_name": "/qt_robot/behavior/talkText",
            "cancel_service_name": "/qt_robot/speech/stop",
            "params": [
                ("message", str),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("speech.talk", ""),
        },

        "speech.stop": {
            "service_name": "/qt_robot/speech/stop",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("speech.stop", ""),
        },

        "speech.config": {
            "service_name": "/qt_robot/speech/config",
            "cancel_service_name": None,
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
            "doc": QTROBOT_API_DOCS.get("speech.config", ""),
        },

        # =========================
        # EMOTION
        # =========================
        "emotion.look": {
            "service_name": "/qt_robot/emotion/look",
            "cancel_service_name": "/qt_robot/emotion/stop",
            "params": [
                ("eye_l", list),
                ("eye_r", list),
                ("duration", float, 1.0),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("emotion.look", ""),
        },

        "emotion.show": {
            "service_name": "/qt_robot/emotion/show",
            "cancel_service_name": "/qt_robot/emotion/stop",
            "params": [
                ("name", str),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("emotion.show", ""),
        },

        "emotion.stop": {
            "service_name": "/qt_robot/emotion/stop",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("emotion.stop", ""),
        },

        # =========================
        # GESTURE
        # =========================
        "gesture.get_all": {
            "service_name": "/qt_robot/gesture/list",
            "cancel_service_name": None,
            "params": [],
            "response_type": List[str],
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("gesture.get_all", ""),
        },

        "gesture.play": {
            "service_name": "/qt_robot/gesture/play",
            "cancel_service_name": "/qt_robot/gesture/stop",
            "params": [
                ("name", str),
                ("speed", float, 1.0),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("gesture.play", ""),
        },

        "gesture.stop": {
            "service_name": "/qt_robot/gesture/stop",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("gesture.stop", ""),
        },

        "gesture.record": {
            "service_name": "/qt_robot/gesture/record",
            "cancel_service_name": "/qt_robot/gesture/stop",
            "params": [
                ("parts", list),
                ("idle_parts", bool, True),
                ("wait", int, 0),
                ("timeout", int, 0),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("gesture.record", ""),
        },

        "gesture.save": {
            "service_name": "/qt_robot/gesture/save",
            "cancel_service_name": None,
            "params": [
                ("name", str),
                ("path", str),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("gesture.save", ""),
        },

        # =========================
        # MOTORS
        # =========================
        "motors.home": {
            "service_name": "/qt_robot/motors/home",
            "cancel_service_name": None,
            "params": [
                ("parts", list),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("motors.home", ""),
        },

        "motors.set_mode": {
            "service_name": "/qt_robot/motors/setControlMode",
            "cancel_service_name": None,
            "params": [
                ("parts", list),
                ("mode", int),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("motors.set_mode", ""),
        },

        "motors.set_velocity": {
            "service_name": "/qt_robot/motors/setVelocity",
            "cancel_service_name": None,
            "params": [
                ("parts", list),
                ("velocity", int),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("motors.set_velocity", ""),
        },

        # =========================
        # AUDIO CORE
        # =========================
        "audio.play": {
            "service_name": "/qt_robot/audio/play",
            "cancel_service_name": "/qt_robot/audio/stop",
            "params": [
                ("filename", str),
                ("filepath", str),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("audio.play", ""),
        },

        "audio.stop": {
            "service_name": "/qt_robot/audio/stop",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("audio.stop", ""),
        },

        "audio.talk": {
            "service_name": "/qt_robot/behavior/talkAudio",
            "cancel_service_name": "/qt_robot/audio/stop",
            "params": [
                ("filename", str),
                ("filepath", str),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("audio.talk", ""),
        },

        # =========================
        # SPEAKER
        # =========================
        "speaker.set_volume": {
            "service_name": "/qt_robot/setting/setVolume",
            "cancel_service_name": None,
            "params": [
                ("volume", int),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("speaker.set_volume", ""),
        },

        # =========================
        # MICROPHONE TUNING
        # =========================
        "microphone.get_tuning": {
            "service_name": "/qt_respeaker_app/tuning/get",
            "cancel_service_name": None,
            "params": [
                ("param", str),
            ],
            "response_type": float,
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("microphone.get_tuning", ""),
        },

        "microphone.set_tuning": {
            "service_name": "/qt_respeaker_app/tuning/set",
            "cancel_service_name": None,
            "params": [
                ("param", str),
                ("value", float),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("microphone.set_tuning", ""),
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
                ("continuous_mode", bool, False)
            ],
            "response_type": bool,
            "local": True,
            "transports": {
                "zmq": {
                    "endpoint": "inproc://asr-azure-rpc",
                },
            },            
            "extra": "asr-azure",
            "install_hint": "pip install luxai-robot[asr-azure]",
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,            
            "robots": ["qtrobot-v3"],
            "doc": "configure Azure ASR"#QTROBOT_API_DOCS.get("microphone.set_tuning", ""),
        },
        "asr.recognize_azure": {
            "service_name": "/asr-azure/recognize",
            "cancel_service_name": "/asr-azure/recognize/cancel",
            "params": [],
            "response_type": dict,
            "local": True,
            "transports": {
                "zmq": {
                    "endpoint": "inproc://asr-azure-rpc",
                },
            },            
            "extra": "asr-azure",
            "install_hint": "pip install luxai-robot[asr-azure]",
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,            
            "robots": ["qtrobot-v3"],
            "doc":  "Perform one-shot recognition with Azure ASR.",  #QTROBOT_API_DOCS.get("microphone.set_tuning", ""),
        },

    },  # end of rpc

    # STREAM SECTION
    "stream": {
        "motors.joints": {
            "direction": "out",
            "frame_type": "JointStateFrame",
            "topic": "/qt_robot/joints/state",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("motors.joints", ""),
        },
        "motors.state": {
            "direction": "out",
            "frame_type": "MotorStateFrame",
            "topic": "/qt_robot/motors/states",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("motors.state", ""),
        },
        "motors.joints": {
            "direction": "in",
            "frame_type": "JointCommandFrame",
            "topic": "/qt_robot/joints/command",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("motors.joints", ""),
        },

        "microphone.activity": {
            "direction": "out",
            "frame_type": "BoolFrame",
            "topic": "/qt_respeaker_app/is_speaking",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("microphone.activity", ""),
        },
        "microphone.direction": {
            "direction": "out",
            "frame_type": "IntFrame",
            "topic": "/qt_respeaker_app/sound_direction",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("microphone.direction", ""),
        },

        "microphone.channel0": {
            "direction": "out",
            "frame_type": "AudioFrameFlac",
            "topic": "/qt_respeaker_app/channel0",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("microphone.channel0", ""),
        },
        "microphone.channel1": {
            "direction": "out",
            "frame_type": "AudioFrameFlac",
            "topic": "/qt_respeaker_app/channel1",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("microphone.channel1", ""),
        },
        "microphone.channel2": {
            "direction": "out",
            "frame_type": "AudioFrameFlac",
            "topic": "/qt_respeaker_app/channel",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("microphone.channel2", ""),
        },
        "microphone.channel3": {
            "direction": "out",
            "frame_type": "AudioFrameFlac",
            "topic": "/qt_respeaker_app/channel3",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("microphone.channel3", ""),
        },
        "microphone.channel4": {
            "direction": "out",
            "frame_type": "AudioFrameFlac",
            "topic": "/qt_respeaker_app/channel4",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("microphone.channel4", ""),
        },
        "microphone.external1": {
            "direction": "out",
            "frame_type": "AudioFrameFlac",
            "topic": "/qt_respeaker_app/external1",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("microphone.external1", ""),
        },
        "microphone.led": {
            "direction": "in",
            "frame_type": "LedColorFrame",
            "topic": "/qt_respeaker_app/status_led",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_API_DOCS.get("microphone.led", ""),
        },
        # -----------------------------------
        #  ASR Azure streams
        # -----------------------------------
        "asr.azure_speech": {
            "direction": "out",
            "frame_type": "DictFrame",
            "topic": "/asr-azure/speech",
            "local": True,
            "extra": "asr-azure",
            "install_hint": "pip install luxai-robot[asr-azure]",
            "doc": "Recognized speech segments from Azure ASR.",
            "transports": {
                "zmq": {
                    "endpoint": "inproc://asr-azure-stream",
                    "queue_size": 10,
                },
            },
        },        
        "asr.azure_event": {
            "direction": "out",
            "frame_type": "StringFrame",
            "topic": "/asr-azure/event",
            "local": True,
            "extra": "asr-azure",
            "install_hint": "pip install luxai-robot[asr-azure]",
            "doc": "Speech recognition events from Azure ASR.",
            "transports": {
                "zmq": {
                    "endpoint": "inproc://asr-azure-stream",
                    "queue_size": 10,
                },
            },
        },        
    }
}