# test_say.py
import time
import inspect
import random
from luxai.magpie.utils import Logger
from luxai.magpie.transport import ZMQRpcResponder, ZMQPublisher
from luxai.magpie.frames import Frame, AudioFrameFlac

from luxai.robot.core import Robot, wait_all_actions, wait_any_action

from luxai.robot.perception.asr.base import ASRBaseNode

import time
from luxai.magpie.frames import StringFrame, DictFrame


if __name__ == "__main__":
    Logger.set_level("DEBUG")

    robot = Robot.connect_zmq(endpoint="tcp://192.168.3.152:50557")    
    # robot = Robot.connect_zmq(node_id="QTPC")
    print("Connected to robot.")

    robot.enable_plugin("asr-azure")

    # robot.microphone.stream.open_external1_reader()
    ret = robot.asr.configure_azure(
        subscription="123",
        region="987"
    ).result()
    print(ret)

    try:        
        time.sleep(60)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        robot.close()
