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
    robot = Robot.connect_zmq(endpoint="tcp://tcp://10.231.0.2:50500")
    Logger.info(f"Connected to {robot._robot_serial} ({robot._robot_type}), SDK version: {robot._sdk_version}")

    robot.enable_plugin_local("asr-riva")

    ret = robot.asr.configure_riva(
        server="localhost:50051",   # address of the Nvidia Riva ASR docker server
        language="en-US",
        continuous_mode=True,
        use_vad=True,
    )
    Logger.info(f"configure_riva returned {ret}")

    # Subscribe to event and speech streams
    robot.asr.stream.on_riva_event(asr_event_callback)
    robot.asr.stream.on_riva_speech(asr_speech_callback)

    # Or perform a single recognition (non-blocking)
    # h = robot.asr.recognize_riva_async()
    # Logger.info("waiting for recognize_riva...")
    # Logger.info(h.result())

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
