# test_say.py
import time
from luxai.magpie.utils import Logger
from luxai.magpie.frames import StringFrame, DictFrame

from luxai.robot.core import Robot
from luxai.robot.core import Robot, wait_all_actions, wait_any_action

def asr_event_callback(event: StringFrame):
    Logger.info(f"event: {event.value}")

def asr_speech_callback(speech: DictFrame):
    Logger.info(f"speech: {speech.value}")


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by node_id (serial number), e.g. "QTRD000310" or by endpoint (IP:port)
    # robot = Robot.connect_zmq(node_id="QTRD000310")
    robot = Robot.connect_zmq(endpoint="tcp://192.168.3.215:50500")
    Logger.info(f"Connected to {robot._robot_serial} ({robot._robot_type}), SDK version: {robot._sdk_version}")
    
    robot.enable_plugin_local("asr-azure")
    ret = robot.asr.configure_azure(
        region="",              # add you azure speech region e.g. westeurope
        subscription="",        # add you azure speech subscription
        continuous_mode=True,
        use_vad=True
    )
    Logger.info(f"configure_azure return {ret}")

    # use callback     
    robot.asr.stream.on_azure_event(asr_event_callback)
    robot.asr.stream.on_azure_speech(asr_speech_callback)

    # use single call (non-blocking)
    # h = robot.asr.recognize_azure_async()
    # Logger.info("waiting for recognize_azure...")
    # Logger.info(h.result())

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()

