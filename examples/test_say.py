# test_say.py
import time
import inspect

from luxai.magpie.utils import Logger
from luxai.magpie.frames import Frame, AudioFrameFlac
from luxai.robot.core import Robot, wait_all_actions, wait_any_action



def main():

    robot = Robot.connect_zmq(endpoint="tcp://192.168.3.152:50557")    
    # robot = Robot.connect_zmq(node_id="QTPC")
    print("Connected to robot.")

    joint_reader = robot.motors.stream.open_joints_state_reader()
    data, _ = joint_reader.read()
    Logger.info(data)
    

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
    Logger.set_level("INFO")
    main()

