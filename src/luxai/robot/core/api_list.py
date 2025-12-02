from __future__ import annotations

from typing import Any, Dict, List, Type


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
            "response_type": type(None),   # bool status in ROS, mapped to success/exception
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Say a text using TTS.",
        },

        # qtrobot.speech.talk()  (behavior-level talk)
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
            "doc": "Trigger a higher-level talking behavior with the given text.",
        },

        # qtrobot.speech.stop()
        "speech.stop": {
            "service_name": "/qt_robot/speech/stop",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Stop any ongoing speech or talk behavior.",
        },
        # qtrobot.speech.config()
        "speech.config": {
            "service_name": "/qt_robot/speech/config",
            "cancel_service_name": None,
            "params": [
                ("language", str, None),   # e.g. "en-US", "fr-FR", None = keep current
                ("pitch", int, 100),       # int16 in ROS
                ("speed", int, 100),       # int16 in ROS
            ],
            "response_type": type(None),   # bool status internally
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Configure TTS parameters (language, pitch, speed).",
        },

        # =========================
        # EMOTION  -> qtrobot.emotion.*
        # =========================

        # qtrobot.emotion.look()
        "emotion.look": {
            "service_name": "/qt_robot/emotion/look",
            "cancel_service_name": "/qt_robot/emotion/stop",
            "params": [
                ("eye_l", list),          # left eye positions (int16[])
                ("eye_r", list),          # right eye positions (int16[])
                ("duration", float, 1.0),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Move the robot eyes to the given positions over a duration.",
        },

        # qtrobot.emotion.show()
        "emotion.show": {
            "service_name": "/qt_robot/emotion/show",
            "cancel_service_name": "/qt_robot/emotion/stop",
            "params": [
                ("name", str),  # e.g. 'happy', 'sad', 'surprised'
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Show a named facial emotion on the robot.",
        },

        # qtrobot.emotion.stop()
        "emotion.stop": {
            "service_name": "/qt_robot/emotion/stop",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Stop any active emotion or eye animation.",
        },

        # =========================
        # GESTURE  -> qtrobot.gesture.*
        # =========================

        # qtrobot.gesture.get_all()
        "gesture.get_all": {
            "service_name": "/qt_robot/gesture/list",
            "cancel_service_name": None,
            "params": [],
            # ROS: string[] gestures + bool status; exposed as List[str]
            "response_type": list,
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Return the list of available gesture names.",
        },

        # qtrobot.gesture.play()
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
            "doc": "Play a stored gesture by name at the given speed.",
        },

        # qtrobot.gesture.stop()
        "gesture.stop": {
            "service_name": "/qt_robot/gesture/stop",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Stop any ongoing gesture playback or recording.",
        },

        # qtrobot.gesture.record()
        "gesture.record": {
            "service_name": "/qt_robot/gesture/record",
            "cancel_service_name": "/qt_robot/gesture/stop",
            "params": [
                ("parts", list),          # e.g. ['left_arm'], ['head', 'right_arm']
                ("idle_parts", bool, True),
                ("wait", int, 0),
                ("timeout", int, 0),
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Start recording a gesture for the given body parts.",
        },

        # qtrobot.gesture.save()
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
            "doc": "Save the last recorded gesture under the given name and path.",
        },

        # =========================
        # MOTORS  -> qtrobot.motors.*
        # =========================

        # qtrobot.motors.home()
        "motors.home": {
            "service_name": "/qt_robot/motors/home",
            "cancel_service_name": None,
            "params": [
                ("parts", list),  # e.g. ['head'], ['right_arm', 'left_arm']
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Move the specified motor groups to their home positions.",
        },

        # qtrobot.motors.set_mode()
        "motors.set_mode": {
            "service_name": "/qt_robot/motors/setControlMode",
            "cancel_service_name": None,
            "params": [
                ("parts", list),
                ("mode", int),  # ROS constants: 0=ON, 1=OFF, 2=BRAKE
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Set control mode for the specified motors (ON, OFF, BRAKE).",
        },

        # qtrobot.motors.set_velocity()
        "motors.set_velocity": {
            "service_name": "/qt_robot/motors/setVelocity",
            "cancel_service_name": None,
            "params": [
                ("parts", list),
                ("velocity", int),  # 0-255 or implementation-specific
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Set movement velocity for the specified motor groups.",
        },

        # =========================
        # AUDIO CORE  -> qtrobot.audio.*
        # =========================

        # qtrobot.audio.play()
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
            "doc": "Play an audio file on the robot speakers.",
        },

        # qtrobot.audio.stop()
        "audio.stop": {
            "service_name": "/qt_robot/audio/stop",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Stop any audio currently playing.",
        },

        # qtrobot.audio.talk()
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
            "doc": "Trigger a higher-level audio-based talking behavior.",
        },

        # =========================
        # SPEAKER  -> qtrobot.speaker.*
        # =========================

        # qtrobot.speaker.set_volume()
        "speaker.set_volume": {
            "service_name": "/qt_robot/setting/setVolume",
            "cancel_service_name": None,
            "params": [
                ("volume", int),  # 0-100
            ],
            "response_type": type(None),
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Set the master speaker output volume (0-100).",
        },

        # =========================
        # MICROPHONE TUNING  -> qtrobot.microphone.*
        # =========================

        # qtrobot.microphone.get_tuning()
        "microphone.get_tuning": {
            "service_name": "/qt_respeaker_app/tuning/get",
            "cancel_service_name": None,
            "params": [
                ("param", str),  # e.g. 'gain', 'noise_suppression'
            ],
            # ROS: float32 value + bool status
            "response_type": float,
            "since": "0.1.0",
            "deprecated": False,
            "deprecated_message": None,
            "robots": ["qtrobot-v3"],
            "doc": "Get a tuning parameter value from the microphone front-end.",
        },

        # qtrobot.microphone.set_tuning()
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
            "doc": "Set a tuning parameter value on the microphone front-end.",
        },
    }, # end of rpc

    "stream": {
        "motors.joints_state": {
            "direction": "out",                # robot -> SDK
            "frame_type": "Frame",
            "topic": "/qt_robot/joints/state",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": "Robot joint states (pos/vel/effort).",
        },

        "microphone.channel0": {
            "direction": "out",
            "frame_type": "AudioFrameFlac",
            "topic": "/qt_respeaker_app/channel0",
            "deprecated": False,
            "experimental": False,
            "robots": ["qtrobot-v3"],
            "doc": "Respeaker microphone audio channel 0",
        },        
    }
}
