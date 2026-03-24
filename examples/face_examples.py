import time
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot


def list_emotions(robot: Robot):
    # List all available emotion files on the robot    
    emotions = robot.face.list_emotions()
    Logger.info(f"Available emotions ({len(emotions)}):")
    for e in emotions:
        Logger.info(f"  {e}")


def show_emotion(robot: Robot):
    # Play an emotion and let it finish naturally
    Logger.info("Showing 'QT/kiss' emotion...")
    robot.face.show_emotion("QT/kiss")    
    Logger.info("Done.")

    # Play an emotion at a different speed
    Logger.info("Showing 'QT/surprise' emotion at 2x speed...")
    ret = robot.face.show_emotion("QT/surprise", speed=2.0)
    Logger.info(f"Done. Return value: {ret}")


def show_emotion_cancel(robot: Robot):
    # Play a long emotion and cancel it after 2 seconds
    Logger.info("Showing 'QT/breathing_exercise' emotion, will cancel after 2 seconds...")
    h = robot.face.show_emotion_async("QT/breathing_exercise")
    time.sleep(3)
    h.cancel()
    Logger.info("Emotion cancelled.")


def look_eyes(robot: Robot):
    # Move both eyes to the right
    Logger.info("Looking right...")
    robot.face.look(l_eye=[30, 0], r_eye=[30, 0])
    time.sleep(1)

    # Move eyes up-left
    Logger.info("Looking up-left...")
    robot.face.look(l_eye=[-20, -20], r_eye=[-20, -20])
    time.sleep(1)

    # Move eyes and auto-reset to center after 3 seconds
    Logger.info("Looking down, auto-reset in 3s...")
    robot.face.look(l_eye=[0, 20], r_eye=[0, 20], duration=3.0)    
    Logger.info("Eyes back to center.")


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by robot_id (serial number), e.g. "QTRD000123" or by endpoint (IP:port)
    # robot = Robot.connect_zmq(robot_id="QTRD000123")    
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")   
    Logger.info(f"Connected to {robot.robot_id} ({robot.robot_type}), SDK version: {robot.sdk_version}")

    list_emotions(robot)
    # show_emotion(robot)
    # show_emotion_cancel(robot)
    # look_eyes(robot)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
