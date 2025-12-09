# test_say.py
import time
import inspect
import random
from luxai.magpie.utils import Logger
from luxai.magpie.transport import ZMQRpcResponder, ZMQPublisher
from luxai.magpie.frames import Frame, AudioFrameFlac

from luxai.robot.core import Robot, wait_all_actions, wait_any_action

from luxai.robot.perception.asr.base import ASRBaseNode
from luxai.robot.perception.asr.microphone_stream import MicrophoneStream
import time
from luxai.magpie.frames import StringFrame, DictFrame


def asr_event_callback(event: StringFrame):
    Logger.info(f"event: {event.value}")

def asr_speech_callback(speech: DictFrame):
    Logger.info(f"speech: {speech.value}")


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    robot = Robot.connect_zmq(endpoint="tcp://192.168.3.152:50557")    
    # robot = Robot.connect_zmq(node_id="QTPC")
    print("Connected to robot.")

    robot.enable_plugin("asr-azure")


    robot.asr.stream.on_azure_event(asr_event_callback)
    # robot.asr.stream.on_azure_speech(asr_speech_callback)

    ret = robot.asr.configure_azure(
        region="westeurope",
        subscription="ace88fb2108f45b59adc5ae52f07b8ca",
        continuous_mode=False
    ).result()
    
    print(ret)
    

    h = robot.asr.recognize_azure(blocking=False)    
    Logger.info("waitring for recognize_azure.")
    Logger.info(h.result())

    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:        
        robot.close()
