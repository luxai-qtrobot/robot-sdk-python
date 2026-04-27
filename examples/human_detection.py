# test_say.py
import time
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot, wait_all_actions, wait_any_action
from luxai.magpie.frames import StringFrame, DictFrame, ListFrame



if __name__ == "__main__":
    Logger.set_level("DEBUG")

    # connect robot by robot_id (serial number), e.g. "QTRD000123" or by endpoint (IP:port)
    robot = Robot.connect_zmq(robot_id="QTRD000320")
    # robot = Robot.connect_zmq(endpoint="tcp://192.168.3.152:50500")
    Logger.info(f"Connected to {robot.robot_id} ({robot.robot_type}), SDK version: {robot.sdk_version}")

    robot.enable_plugin_zmq("human-detector", node_id="qtrobot-human-detector")
    # robot.enable_plugin_zmq("human-detector", endpoint="tcp://127.0.0.1:5770")
    reader = robot.perception.stream.open_human_presence_reader()
    frame = reader.read()
    Logger.info(f"Read {frame}")


    try:
        time.sleep(30)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    
    robot.close()
