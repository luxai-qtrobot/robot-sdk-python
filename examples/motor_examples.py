import time
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot
from luxai.robot.core.frames import JointStateFrame, JointCommandFrame


def list_motors(robot: Robot):
    # List all configured motors and their parameters
    motors = robot.motor.list()
    for name, info in motors.items():
        Logger.info(f"  {name}: {info}")


def torque_control(robot: Robot):
    # Disable torque on a single motor, wait, then re-enable it
    Logger.info("Disabling torque on HeadYaw...")
    robot.motor.off("HeadYaw")
    time.sleep(2)
    Logger.info("Re-enabling torque on HeadYaw...")
    robot.motor.on("HeadYaw")    
    # robot.motor.on_all()


def home_motors(robot: Robot):
    # Move a single motor to its home position
    Logger.info("Homing HeadYaw...")
    robot.motor.home("HeadYaw")
    Logger.info("HeadYaw homed.")

    # Move all motors to their home positions
    Logger.info("Homing all motors...")
    robot.motor.home_all()
    Logger.info("All motors homed.")


def set_motor_velocity(robot: Robot):
    # Set default velocity for individual motors
    Logger.info("Setting HeadYaw velocity to 50...")
    robot.motor.set_velocity("HeadYaw", 50)


def joint_state_stream(robot: Robot):
    # Subscribe to joint state and error streams
    def on_joint_state(data: JointStateFrame):
        for joint in data.joints():
            Logger.info(f"[{joint}]pos: {data.position(joint):.2f}, vel: {data.velocity(joint):.1f}, eff: {data.effort(joint):.1f}, temp: {data.temperature(joint):.1f}, volt: {data.voltage(joint):.1f}")
        Logger.info("-"*20)
    def on_joint_error(data):
        Logger.warning(f"Joint error: {data.value}")

    Logger.info("Subscribing to joint state and error streams (press Ctrl+C to stop)...")
    robot.motor.stream.on_joints_state(on_joint_state)
    robot.motor.stream.on_joints_error(on_joint_error)


def joint_command_stream(robot: Robot):
    # Open a writer and send direct joint position/velocity commands
    Logger.info("Sending joint commands...")
    writer = robot.motor.stream.open_joints_command_writer()

    cmd = JointCommandFrame()
    cmd.set_joint("HeadYaw", position=30, velocity=40)
    Logger.info(f"Command: {cmd.value}")
    writer.write(cmd)
    time.sleep(2)

    # Return to home
    cmd2 = JointCommandFrame()
    cmd2.set_joint("HeadYaw", position=0, velocity=20)
    writer.write(cmd2)


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by robot_id (serial number), e.g. "QTRD000123" or by endpoint (IP:port)
    # robot = Robot.connect_zmq(robot_id="QTRD000123")
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")
    Logger.info(f"Connected to {robot.robot_id} ({robot.robot_type}), SDK version: {robot.sdk_version}")

    list_motors(robot)
    # torque_control(robot)
    home_motors(robot)
    # set_motor_velocity(robot)    
    # joint_state_stream(robot)
    # joint_command_stream(robot)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
