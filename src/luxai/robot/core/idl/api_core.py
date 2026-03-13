from typing import Any, Dict

from .api_core_doc import QTROBOT_CORE_API_DOCS

QTROBOT_CORE_APIS: Dict[str, Dict[str, Any]] = {

    # ===========================================================
    # RPC APIs
    # ===========================================================
    "rpc": {

        # -------------------------------------------------------
        # MEDIA  ->  Audio Foreground
        # -------------------------------------------------------
        "media.play_fg_audio_file": {
            "service_name": "/media/audio/fg/file/play",
            "cancel_service_name": "/media/audio/fg/file/cancel",
            "params": [
                ("uri", str),
            ],
            "response_type": bool,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.play_fg_audio_file", ""),
        },
        "media.pause_fg_audio_file": {
            "service_name": "/media/audio/fg/file/pause",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.pause_fg_audio_file", ""),
        },
        "media.resume_fg_audio_file": {
            "service_name": "/media/audio/fg/file/resume",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.resume_fg_audio_file", ""),
        },
        "media.cancel_fg_audio_stream": {
            "service_name": "/media/audio/fg/stream/cancel",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.cancel_fg_audio_stream", ""),
        },
        "media.pause_fg_audio_stream": {
            "service_name": "/media/audio/fg/stream/pause",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.pause_fg_audio_stream", ""),
        },
        "media.resume_fg_audio_stream": {
            "service_name": "/media/audio/fg/stream/resume",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.resume_fg_audio_stream", ""),
        },
        "media.set_fg_audio_volume": {
            "service_name": "/media/audio/fg/volume/set",
            "cancel_service_name": None,
            "params": [
                ("value", float),           # volume in [0.0, 1.0]
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.set_fg_audio_volume", ""),
        },
        "media.get_fg_audio_volume": {
            "service_name": "/media/audio/fg/volume/get",
            "cancel_service_name": None,
            "params": [],
            "response_type": float,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.get_fg_audio_volume", ""),
        },

        # -------------------------------------------------------
        # MEDIA  ->  Audio Background
        # -------------------------------------------------------
        "media.play_bg_audio_file": {
            "service_name": "/media/audio/bg/file/play",
            "cancel_service_name": "/media/audio/bg/file/cancel",
            "params": [
                ("uri", str),
            ],
            "response_type": bool,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.play_bg_audio_file", ""),
        },
        "media.pause_bg_audio_file": {
            "service_name": "/media/audio/bg/file/pause",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.pause_bg_audio_file", ""),
        },
        "media.resume_bg_audio_file": {
            "service_name": "/media/audio/bg/file/resume",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.resume_bg_audio_file", ""),
        },
        "media.cancel_bg_audio_stream": {
            "service_name": "/media/audio/bg/stream/cancel",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.cancel_bg_audio_stream", ""),
        },
        "media.pause_bg_audio_stream": {
            "service_name": "/media/audio/bg/stream/pause",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.pause_bg_audio_stream", ""),
        },
        "media.resume_bg_audio_stream": {
            "service_name": "/media/audio/bg/stream/resume",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.resume_bg_audio_stream", ""),
        },
        "media.set_bg_audio_volume": {
            "service_name": "/media/audio/bg/volume/set",
            "cancel_service_name": None,
            "params": [
                ("value", float),           # volume in [0.0, 1.0]
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.set_bg_audio_volume", ""),
        },
        "media.get_bg_audio_volume": {
            "service_name": "/media/audio/bg/volume/get",
            "cancel_service_name": None,
            "params": [],
            "response_type": float,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.get_bg_audio_volume", ""),
        },

        # -------------------------------------------------------
        # MEDIA  ->  Video Foreground
        # -------------------------------------------------------
        "media.play_fg_video_file": {
            "service_name": "/media/video/fg/file/play",
            "cancel_service_name": "/media/video/fg/file/cancel",
            "params": [
                ("uri", str),
                ("speed", float, 1.0),          # optional; playback speed multiplier
                ("with_audio", bool, False),     # optional; play embedded audio track
            ],
            "response_type": bool,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.play_fg_video_file", ""),
        },
        "media.pause_fg_video_file": {
            "service_name": "/media/video/fg/file/pause",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.pause_fg_video_file", ""),
        },
        "media.resume_fg_video_file": {
            "service_name": "/media/video/fg/file/resume",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.resume_fg_video_file", ""),
        },
        "media.cancel_fg_video_stream": {
            "service_name": "/media/video/fg/stream/cancel",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.cancel_fg_video_stream", ""),
        },
        "media.pause_fg_video_stream": {
            "service_name": "/media/video/fg/stream/pause",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.pause_fg_video_stream", ""),
        },
        "media.resume_fg_video_stream": {
            "service_name": "/media/video/fg/stream/resume",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.resume_fg_video_stream", ""),
        },
        "media.set_fg_video_alpha": {
            "service_name": "/media/video/fg/set_alpha",
            "cancel_service_name": None,
            "params": [
                ("value", float),               # alpha transparency [0.0, 1.0]
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.set_fg_video_alpha", ""),
        },

        # -------------------------------------------------------
        # MEDIA  ->  Video Background
        # -------------------------------------------------------
        "media.play_bg_video_file": {
            "service_name": "/media/video/bg/file/play",
            "cancel_service_name": "/media/video/bg/file/cancel",
            "params": [
                ("uri", str),
                ("speed", float, 1.0),          # optional; playback speed multiplier
                ("with_audio", bool, False),     # optional; play embedded audio track
            ],
            "response_type": bool,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.play_bg_video_file", ""),
        },
        "media.pause_bg_video_file": {
            "service_name": "/media/video/bg/file/pause",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.pause_bg_video_file", ""),
        },
        "media.resume_bg_video_file": {
            "service_name": "/media/video/bg/file/resume",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.resume_bg_video_file", ""),
        },
        "media.cancel_bg_video_stream": {
            "service_name": "/media/video/bg/stream/cancel",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.cancel_bg_video_stream", ""),
        },
        "media.pause_bg_video_stream": {
            "service_name": "/media/video/bg/stream/pause",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.pause_bg_video_stream", ""),
        },
        "media.resume_bg_video_stream": {
            "service_name": "/media/video/bg/stream/resume",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.resume_bg_video_stream", ""),
        },

        # -------------------------------------------------------
        # SPEAKER
        # -------------------------------------------------------
        "speaker.set_volume": {
            "service_name": "/speaker/volume/set",
            "cancel_service_name": None,
            "params": [
                ("value", float),               # master speaker volume [0.0, 1.0]
            ],
            "response_type": bool,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("speaker.set_volume", ""),
        },
        "speaker.get_volume": {
            "service_name": "/speaker/volume/get",
            "cancel_service_name": None,
            "params": [],
            "response_type": float,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("speaker.get_volume", ""),
        },
        "speaker.mute": {
            "service_name": "/speaker/volume/mute",
            "cancel_service_name": None,
            "params": [],
            "response_type": bool,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("speaker.mute", ""),
        },
        "speaker.unmute": {
            "service_name": "/speaker/volume/unmute",
            "cancel_service_name": None,
            "params": [],
            "response_type": bool,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("speaker.unmute", ""),
        },

        # -------------------------------------------------------
        # FACE
        # -------------------------------------------------------
        "face.look": {
            "service_name": "/face/look",
            "cancel_service_name": None,
            "params": [
                ("l_eye", list),                # [dx, dy] pixel offset from center for left eye
                ("r_eye", list),                # [dx, dy] pixel offset from center for right eye
                ("duration", float, 0.0),       # optional; if >0 resets eyes to center after N seconds
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("face.look", ""),
        },
        "face.show_emotion": {
            "service_name": "/face/emotion/show",
            "cancel_service_name": "/face/emotion/stop",
            "params": [
                ("emotion", str),               # emotion name or relative path (with/without .avi)
                ("speed", float, None),         # optional; playback speed factor (default from config)
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("face.show_emotion", ""),
        },
        "face.list_emotions": {
            "service_name": "/face/emotion/list",
            "cancel_service_name": None,
            "params": [],
            "response_type": list,              # list of relative .avi paths (recursive scan)
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("face.list_emotions", ""),
        },

        # -------------------------------------------------------
        # MOTOR
        # -------------------------------------------------------
        "motor.list": {
            "service_name": "/motor/list",
            "cancel_service_name": None,
            "params": [],
            "response_type": dict,              # {name: {part, position_min, position_max,
                                                #   position_home, velocity_max,
                                                #   calibration_offset, overload_threshold}}
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.list", ""),
        },
        "motor.set_calib": {
            "service_name": "/motor/calib/set",
            "cancel_service_name": None,
            "params": [
                ("motor", str),                      # motor name
                ("offset", float, None),             # optional; calibration offset value (degrees)
                ("overload_threshold", int, None), # optional; calibration overload_threshold value (degrees)
                ("velocity_max", int, None),       # optional; calibration velocity_max value (degrees)
                ("store", bool, False),              # optional; persist offset to config file
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.set_calib", ""),
        },
        "motor.calib_all": {
            "service_name": "/motor/calib/all",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.calib_all", ""),
        },
        "motor.set_velocity": {
            "service_name": "/motor/velocity/set",
            "cancel_service_name": None,
            "params": [
                ("motor", str),                 # motor name
                ("velocity", int),              # velocity value (0 .. velocity_max)
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.set_velocity", ""),
        },
        "motor.on": {
            "service_name": "/motor/on",
            "cancel_service_name": None,
            "params": [
                ("motor", str),                 # motor name to enable torque
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.on", ""),
        },
        "motor.off": {
            "service_name": "/motor/off",
            "cancel_service_name": None,
            "params": [
                ("motor", str),                 # motor name to disable torque
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.off", ""),
        },
        "motor.on_all": {
            "service_name": "/motor/on/all",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.on_all", ""),
        },
        "motor.off_all": {
            "service_name": "/motor/off/all",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.off_all", ""),
        },
        "motor.home": {
            "service_name": "/motor/move/home",
            "cancel_service_name": None,
            "params": [
                ("motor", str),                 # motor name to move to home position
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.home", ""),
        },
        "motor.home_all": {
            "service_name": "/motor/move/home/all",
            "cancel_service_name": None,
            "params": [],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.home_all", ""),
        },

        # -------------------------------------------------------
        # GESTURE
        # -------------------------------------------------------
        "gesture.record": {
            "service_name": "/gesture/record/start",
            "cancel_service_name": "/gesture/record/stop",
            "params": [
                ("motors", list),                       # list[str] of motor names to record
                ("release_motors", bool, False),         # optional; disable torque during recording
                ("delay_start_ms", int, 0),              # optional; delay before recording starts (ms)
                ("timeout_ms", int, 60000),               # optional; max recording duration (ms)
                ("refine_keyframe", bool, True),         # optional; remove redundant keyframes
                ("keyframe_pos_eps", float, 0.75),       # optional; position epsilon for refinement (deg)
                ("keyframe_max_gap_us", int, 100000),    # optional; max gap between keyframes (μs)
            ],
            "response_type": dict,                      # returns recorded trajectory keyframes dict
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("gesture.record", ""),
        },
        "gesture.stop_record": {
            "service_name": "/gesture/record/stop",            
            "params": [],
            "response_type": bool,                      # stops recording if in progress, returns True if recording was stopped, False if no recording in progress
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("gesture.stop_record", ""),
        },
        "gesture.store_record": {
            "service_name": "/gesture/record/store",
            "cancel_service_name": None,
            "params": [
                ("gesture", str),                       # name/relative path to save as XML
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("gesture.store_record", ""),
        },
        "gesture.play": {
            "service_name": "/gesture/play",
            "cancel_service_name": "/gesture/cancel",
            "params": [
                ("keyframes", dict),                    # keyframes trajectory dict
                ("resample", bool, True),               # optional; resample to uniform rate_hz
                ("rate_hz", float, 100.0),              # optional; resample rate in Hz
                ("speed_factor", float, 1.0),           # optional; playback speed multiplier
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("gesture.play", ""),
        },
        "gesture.play_file": {
            "service_name": "/gesture/file/play",
            "cancel_service_name": "/gesture/cancel",
            "params": [
                ("gesture", str),                       # gesture name or path (with/without .xml)
                ("speed_factor", float, 1.0),           # optional; playback speed multiplier
            ],
            "response_type": bool,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("gesture.play_file", ""),
        },
        "gesture.list_files": {
            "service_name": "/gesture/file/list",
            "cancel_service_name": None,
            "params": [],
            "response_type": list,                      # list of available gesture file paths
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("gesture.list_files", ""),
        },

        # -------------------------------------------------------
        # TTS
        # -------------------------------------------------------
        "tts.set_default_engine": {
            "service_name": "/tts/default_engine/set",
            "cancel_service_name": None,
            "params": [
                ("engine", str),                # engine id (e.g. "acapela", "azure", or custom)
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("tts.set_default_engine", ""),
        },
        "tts.get_default_engine": {
            "service_name": "/tts/default_engine/get",
            "cancel_service_name": None,
            "params": [],
            "response_type": str,               # current default engine id
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("tts.get_default_engine", ""),
        },
        "tts.list_engines": {
            "service_name": "/tts/engines/list",
            "cancel_service_name": None,
            "params": [],
            "response_type": list,              # list of available engine id strings
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("tts.list_engines", ""),
        },
        "tts.say_text": {
            "service_name": "/tts/engine/say/text",
            "cancel_service_name": "/tts/engine/cancel",
            "params": [                
                ("text", str),                  # plain text to synthesize
                ("engine", str, None),          # optional; engine id to use 
                ("lang", str, None),            # optional; language code (e.g. "en-US")
                ("voice", str, None),           # optional; voice id or name
                ("rate", float, None),          # optional; speech rate multiplier
                ("pitch", float, None),         # optional; pitch adjustment
                ("volume", float, None),        # optional; volume level
                ("style", str, None),           # optional; speaking style (engine-dependent)
            ],
            "response_type": type(None),        # blocks until audio playback completes
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("tts.say_text", ""),
        },
        "tts.say_ssml": {
            "service_name": "/tts/engine/say/ssml",
            "cancel_service_name": "/tts/engine/cancel",
            "params": [                
                ("ssml", str),                  # SSML markup string
                ("engine", str, None),          # optional; engine id to use 
            ],
            "response_type": type(None),        # blocks until audio playback completes
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("tts.say_ssml", ""),
        },
        "tts.set_config": {
            "service_name": "/tts/engine/configure/set",
            "cancel_service_name": None,
            "params": [
                ("config", dict),               # engine-specific config key/value pairs
                ("engine", str, None),          # optional; engine id (uses default if omitted)
            ],
            "response_type": type(None),
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("tts.set_config", ""),
        },
        "tts.get_config": {
            "service_name": "/tts/engine/configure/get",
            "cancel_service_name": None,
            "params": [
                ("engine", str, None),          # optional; engine id (uses default if omitted)
            ],
            "response_type": dict,              # current engine configuration dict
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("tts.get_config", ""),
        },
        "tts.get_languages": {
            "service_name": "/tts/engine/languages/get",
            "cancel_service_name": None,
            "params": [
                ("engine", str, None),          # optional; engine id (uses default if omitted)
            ],
            "response_type": list,              # list of supported language code strings
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("tts.get_languages", ""),
        },
        "tts.get_voices": {
            "service_name": "/tts/engine/voices/get",
            "cancel_service_name": None,
            "params": [
                ("engine", str, None),          # optional; engine id (uses default if omitted)
            ],
            "response_type": list,              # list of {id, lang, lang_name, gender,
                                                #   is_child, is_multilingual, display_name}
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("tts.get_voices", ""),
        },
        "tts.supports_ssml": {
            "service_name": "/tts/engine/supports/ssml",
            "cancel_service_name": None,
            "params": [
                ("engine", str, None),          # optional; engine id (uses default if omitted)
            ],
            "response_type": bool,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("tts.supports_ssml", ""),
        },
        # -------------------------------------------------------
        # Microphone
        # -------------------------------------------------------
        "microphone.get_int_tuning": {
            "service_name": "/microphone/int/tunning/get",
            "cancel_service_name": None,
            "params": [],
            "response_type": dict,   # { "AECNORM": 1.0, "VOICEACTIVITY": 0, ... } (all readable params)
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("microphone.get_int_tuning", ""),
        },
        "microphone.set_int_tuning": {
            "service_name": "/microphone/int/tunning/set",
            "cancel_service_name": None,
            "params": [
                ("name", str),           # respeaker param name (e.g. "AECNORM")
                ("value", float),        # numeric value
            ],
            "response_type": bool,  # True if set() succeeded
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("microphone.set_int_tuning", ""),
        },
    },

    # ===========================================================
    # STREAM APIs
    # ===========================================================
    "stream": {

        # -------------------------------------------------------
        # MEDIA NODE  (all inbound — consumers push frames in)
        # -------------------------------------------------------
        "media.fg_audio_stream": {
            "direction": "in",
            "topic": "/media/audio/fg/stream:i",
            "frame_type": "AudioFrameRaw",
            "delivery": "reliable",
            "queue_size": 10,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.fg_audio_stream", ""),
        },
        "media.bg_audio_stream": {
            "direction": "in",
            "topic": "/media/audio/bg/stream:i",
            "frame_type": "AudioFrameRaw",
            "delivery": "reliable",
            "queue_size": 10,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.bg_audio_stream", ""),
        },
        "media.fg_video_stream": {
            "direction": "in",
            "topic": "/media/video/fg/stream:i",
            "frame_type": "ImageFrameRaw",
            "delivery": "latest",
            "queue_size": 0,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.fg_video_stream", ""),
        },
        "media.bg_video_stream": {
            "direction": "in",
            "topic": "/media/video/bg/stream:i",
            "frame_type": "ImageFrameRaw",
            "delivery": "latest",
            "queue_size": 0,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("media.bg_video_stream", ""),
        },

        # -------------------------------------------------------
        # MOTOR NODE  (outbound state/error/progress; inbound commands)
        # -------------------------------------------------------
        "motor.joints_state": {
            "direction": "out",
            "topic": "/motor/joints/state/stream:o",
            "frame_type": "JointStateFrame",      # {name: {position, velocity, effort, voltage, temprature}}
            "delivery": "latest",
            "queue_size": 2,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.joints_state", ""),
        },
        "motor.joints_error": {
            "direction": "out",
            "topic": "/motor/joints/error/stream:o",
            "frame_type": "DictFrame",      # {name: {overload_limit?, voltage_limit?,
                                            #   temperature_limit?, sensor_failure?}}
            "delivery": "latest",
            "queue_size": 2,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.joints_error", ""),
        },
        "gesture.progress": {
            "direction": "out",
            "topic": "/gesture/progress/stream:o",
            "frame_type": "DictFrame",      # gesture playback progress info
            "delivery": "latest",
            "queue_size": 2,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("gesture.progress", ""),
        },
        "motor.joints_command": {
            "direction": "in",
            "topic": "/motor/joints/command/stream:i",
            "frame_type": "JointCommandFrame",      # {name: {position, velocity?}} command dict
            "delivery": "reliable",
            "queue_size": 10,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("motor.joints_command", ""),
        },
        # ----------------------------------------------------------------
        # Microphone (outpund audio streams and microphone events streams)
        # ----------------------------------------------------------------        
        "microphone.int_audio_ch0": {
            "direction": "out",
            "topic": "/mic/int/audio/ch0/stream:o",
            "frame_type": "AudioFrameRaw",
            "delivery": "reliable",
            "queue_size": 10,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("microphone.int_audio_ch0", ""),
        },
        "microphone.int_audio_ch1": {
            "direction": "out",
            "topic": "/mic/int/audio/ch1/stream:o",
            "frame_type": "AudioFrameRaw",
            "delivery": "reliable",
            "queue_size": 10,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("microphone.int_audio_ch1", ""),
        },
        "microphone.int_audio_ch2": {
            "direction": "out",
            "topic": "/mic/int/audio/ch2/stream:o",
            "frame_type": "AudioFrameRaw",
            "delivery": "reliable",
            "queue_size": 10,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("microphone.int_audio_ch2", ""),
        },
        "microphone.int_audio_ch3": {
            "direction": "out",
            "topic": "/mic/int/audio/ch3/stream:o",
            "frame_type": "AudioFrameRaw",
            "delivery": "reliable",
            "queue_size": 10,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("microphone.int_audio_ch3", ""),
        },
        "microphone.int_audio_ch4": {
            "direction": "out",
            "topic": "/mic/int/audio/ch4/stream:o",
            "frame_type": "AudioFrameRaw",
            "delivery": "reliable",
            "queue_size": 10,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("microphone.int_audio_ch4", ""),
        },
        "microphone.int_event": {
            "direction": "out",
            "topic": "/mic/int/event/stream:o",
            "frame_type": "DictFrame",   # {"activity": bool, "direction": int}
            "delivery": "latest",
            "queue_size": 2,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("microphone.int_event", ""),
        },
        "microphone.ext_audio_ch0": {
            "direction": "out",
            "topic": "/mic/ext/audio/ch0/stream:o",
            "frame_type": "AudioFrameRaw",
            "delivery": "reliable",
            "queue_size": 10,
            "robots": ["qtrobot-v3"],
            "doc": QTROBOT_CORE_API_DOCS.get("microphone.ext_audio_ch0", ""),
        },        
    },
}
