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
from luxai.magpie.frames import StringFrame, DictFrame, ListFrame


def on_acceleration_callback(frame: ListFrame):
    Logger.info(f"Acceleration frame received: {frame.value}")


if __name__ == "__main__":
    Logger.set_level("DEBUG")

    robot = Robot.connect_zmq(endpoint="tcp://192.168.3.152:50557")
    # robot = Robot.connect_zmq(node_id="QTPC")
    Logger.info("Connected to robot.")

    robot.enable_plugin_zmq("realsense-driver", endpoint="tcp://192.168.3.152:50655")

    color_intrinsics = robot.camera.get_color_intrinsics().result()
    Logger.info(f"Color intrinsics: {color_intrinsics}")


    depth_intrinsics = robot.camera.get_depth_intrinsics().result()
    Logger.info(f"Depth intrinsics: {depth_intrinsics}")

    depth_scale = robot.camera.get_depth_scale().result()
    Logger.info(f"Depth scale: {depth_scale}")

    robot.camera.stream.on_acceleration(on_acceleration_callback)
    # camera = robot.camera.stream.open_color_reader()
    # frame = camera.read(timeout=3.0)   
    # Logger.info(frame)    


    try:
        time.sleep(30)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    
    robot.close()
