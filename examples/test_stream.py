# test_say.py
import time
import inspect

from luxai.magpie.utils import Logger
from luxai.magpie.frames import Frame, AudioFrameFlac
from luxai.robot.core.frames import JointStateFrame
from luxai.robot.core import Robot, wait_all_actions, wait_any_action


def on_mic_0(data:AudioFrameFlac):
    Logger.info(data)


def main():

    robot = Robot.connect_zmq(endpoint="tcp://192.168.3.152:50557")    
    # robot = Robot.connect_zmq(node_id="QTPC")
    print("Connected to robot.")

    joint_reader = robot.motors.stream.open_joints_reader()
    state = joint_reader.read()
    Logger.info(type(state))
    Logger.info(state.position("HeadYaw"))
    
    mic = robot.microphone.stream.on_channel0(on_mic_0)
 
    should_stop = False
    try:
        while(not should_stop):
            time.sleep(5)
    except KeyboardInterrupt:
        should_stop = True
        print("Interrupted by user.")
    except Exception as e:
        print("Error:", e)
    finally:
        robot.close()
        print("Closed transport.")

    # print("Transport closed.")

if __name__ == "__main__":
    # Logger.set_level("DEBUG")
    main()

