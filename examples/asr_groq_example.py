import time
from luxai.magpie.utils import Logger
from luxai.magpie.frames import StringFrame, DictFrame

from luxai.robot.core import Robot


def asr_event_callback(event: StringFrame):
    Logger.info(f"event: {event.value}")


def asr_speech_callback(speech: DictFrame):
    Logger.info(f"speech: {speech.value}")


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by robot_id (serial number) or by endpoint (IP:port)
    # robot = Robot.connect_zmq(robot_id="QTRD000123")
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")
    Logger.info(f"Connected to {robot._robot_serial} ({robot._robot_type}), SDK version: {robot._sdk_version}")

    robot.enable_plugin_local("asr-groq")

    ret = robot.asr.configure_groq(
        api_key="",             # add your Groq API key (https://console.groq.com)
        language="en",          # ISO-639-1 language code, e.g. 'en', 'fr', 'de'
        silence_timeout=0.5,    # seconds of silence that end an utterance
        continuous_mode=True,
    )
    Logger.info(f"configure_groq returned {ret}")

    # Subscribe to event and speech streams
    robot.asr.stream.on_groq_event(asr_event_callback)
    robot.asr.stream.on_groq_speech(asr_speech_callback)

    # Or perform a single recognition (non-blocking)
    # h = robot.asr.recognize_groq_async()
    # Logger.info("waiting for recognize_groq...")
    # Logger.info(h.result())

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
