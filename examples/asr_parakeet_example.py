import time
from luxai.magpie.utils import Logger
from luxai.magpie.frames import StringFrame, DictFrame

from luxai.robot.core import Robot


def asr_event_callback(event: StringFrame):
    Logger.info(f"event: {event.value}")    


def asr_speech_callback(speech: DictFrame):
    Logger.debug(f"speech: {speech.value}")


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by robot_id (serial number) or by endpoint (IP:port)
    # robot = Robot.connect_zmq(robot_id="QTRD000123")
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")
    Logger.info(f"Connected to {robot.robot_id} ({robot.robot_type}), SDK version: {robot.sdk_version}")

    robot.enable_plugin_local("asr-parakeet")

    ret = robot.asr.configure_parakeet(
        endpoint="tcp://10.231.0.2:50860",  # qtrobot-parakeet-asr-server on Jetson Orin
        language="en",                      # ISO-639-1 language code (model auto-detects)
        use_vad=True,
        silence_timeout=0.3,            # silence duration (s) — used by client VAD and server RMS detection
        max_buffer_seconds=20.0,        # max utterance duration before forced finalization
        continuous_mode=True,
    )
    Logger.info(f"configure_parakeet returned {ret}")

    # Subscribe to event and speech streams
    # speech stream carries both interim (is_final=False) and final (is_final=True) results
    robot.asr.stream.on_parakeet_event(asr_event_callback)
    robot.asr.stream.on_parakeet_speech(asr_speech_callback)

    # Or perform a single recognition (non-blocking)
    # h = robot.asr.recognize_parakeet_async()
    # Logger.info("waiting for recognize_parakeet...")
    # Logger.info(h.result())

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
