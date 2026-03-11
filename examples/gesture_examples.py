# test_say.py
import time
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot, wait_all_actions, wait_any_action

def list_gestures(robot: Robot):
    #list available gestures
    gestures = robot.gesture.list_files()
    Logger.info(f"Available gestures: {gestures}")


def play_gesture(robot: Robot):
    # Play/cancel playing a gesture
    Logger.info("Playing gesture 'bye' press <Enter> to cancel...")
    h = robot.gesture.play_file_async("QT/bye")
    input()
    h.cancel()
    Logger.info("gesture canceld. puting robot to rest pose...")
    robot.motor.home_all()

def record_gesture(robot: Robot):
    # record a gesture
    Logger.info("Please move the robot's right arm to record a gesture, recording will start in 2 seconds and last for maximum 20 seconds...")
    h = robot.gesture.record_async(
        motors=["RightShoulderPitch", "RightShoulderRoll", "RightElbowRoll"],
        release_motors = True,
        delay_start_ms = 2000,
        timeout_ms = 20000,
        )
    Logger.info("Recording... (press <Enter> to stop recording)")
    input()
    robot.gesture.stop_record()
    keyframes = h.result()
    Logger.info(f"Recording stopped. {len(keyframes['points'])} keyframes recorded.")

    Logger.info("Playing back the recorded gesture in 2 seconds...")
    time.sleep(2)
    robot.gesture.play(keyframes)
    Logger.info("Playback Done. Do you want to save the recorded gesture? (y/n)")
    if input().lower() == 'y':
        name = input("Enter gesture name: ")
        robot.gesture.store_record(name)
        Logger.info(f"Gesture '{name}' stored.")


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by node_id (serial number), e.g. "QTRD000123" or by endpoint (IP:port)
    # robot = Robot.connect_zmq(node_id="QTRD000123")
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")
    Logger.info(f"Connected to {robot._robot_serial} ({robot._robot_type}), SDK version: {robot._sdk_version}")

    list_gestures(robot)
    # play_gesture(robot)
    # record_gesture(robot)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
