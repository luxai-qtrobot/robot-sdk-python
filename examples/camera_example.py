# test_say.py
import time
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot, wait_all_actions, wait_any_action
from luxai.magpie.frames import StringFrame, DictFrame, ListFrame


def on_acceleration_callback(frame: ListFrame):
    Logger.info(f"Acceleration frame received: {frame.value}")


if __name__ == "__main__":
    Logger.set_level("DEBUG")

    # connect robot by node_id (serial number), e.g. "QTRD000123" or by endpoint (IP:port)
    # robot = Robot.connect_zmq(node_id="QTRD000123")
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")
    Logger.info(f"Connected to {robot._robot_serial} ({robot._robot_type}), SDK version: {robot._sdk_version}")

    # robot.enable_plugin_zmq("realsense-driver", node_id="qtrobot-realsense-driver")
    robot.enable_plugin_zmq("realsense-driver", endpoint="tcp://10.231.0.1:50750")

    color_intrinsics = robot.camera.get_color_intrinsics()
    Logger.info(f"Color intrinsics: {color_intrinsics}")


    depth_intrinsics = robot.camera.get_depth_intrinsics()
    Logger.info(f"Depth intrinsics: {depth_intrinsics}")

    depth_scale = robot.camera.get_depth_scale()
    Logger.info(f"Depth scale: {depth_scale}")

    # robot.camera.stream.on_acceleration(on_acceleration_callback)
    # camera = robot.camera.stream.open_color_reader()
    # frame = camera.read(timeout=3.0)   
    # Logger.info(frame)    


    try:
        time.sleep(30)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    
    robot.close()
