import time
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot


def get_volume(robot: Robot):
    # Read the current master volume level
    vol = robot.speaker.get_volume()
    Logger.info(f"Current speaker volume: {vol:.2f}")


def set_volume(robot: Robot):
    # Set the master volume to 80%
    Logger.info("Setting volume to 0.8...")
    robot.speaker.set_volume(0.8)

    vol = robot.speaker.get_volume()
    Logger.info(f"Volume after set: {vol:.2f}")

    # Reduce to 40%
    Logger.info("Setting volume to 0.7...")
    robot.speaker.set_volume(0.7)

    vol = robot.speaker.get_volume()
    Logger.info(f"Volume after set: {vol:.2f}")


def mute_unmute(robot: Robot):
    # Mute the speaker, wait, then unmute
    Logger.info("Muting speaker...")
    robot.speaker.mute()
    Logger.info("Speaker muted. Waiting 2 seconds...")
    time.sleep(2)

    Logger.info("Unmuting speaker...")
    robot.speaker.unmute()
    Logger.info("Speaker unmuted.")


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by node_id (serial number), e.g. "QTRD000310" or by endpoint (IP:port)
    # robot = Robot.connect_zmq(node_id="QTRD000310")
    robot = Robot.connect_zmq(endpoint="tcp://192.168.3.215:50500")
    Logger.info(f"Connected to {robot._robot_serial} ({robot._robot_type}), SDK version: {robot._sdk_version}")

    get_volume(robot)
    # set_volume(robot)
    # mute_unmute(robot)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
