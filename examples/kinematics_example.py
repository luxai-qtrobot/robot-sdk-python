import time
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by robot_id (serial number) or by endpoint (IP:port)
    # robot = Robot.connect_zmq(robot_id="QTRD000123")
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")
    Logger.info(f"Connected to {robot.robot_id} ({robot.robot_type}), SDK version: {robot.sdk_version}")

    robot.enable_plugin_local("kinematics")

    # Optional: override camera intrinsics or motor wait timeout.
    # Default values match the QTrobot RealSense hardware — skip this call if unchanged.
    # robot.kinematics.configure(motor_timeout=15.0)

    # ----------------------------------------------------------------
    # Head: look at a 3-D point in the robot base frame
    # (origin at the bottom of the robot, x = forward, y = left, z = up)
    # ----------------------------------------------------------------

    # # Look straight ahead at roughly face height
    Logger.info("Looking forward at (1.0, 0.0, 0.6) ...")
    robot.kinematics.look_at_point(1.0, 0.0, 0.6)

    # # Look slightly to the left
    Logger.info("Looking left at (1.0, 0.5, 0.6) ...")
    robot.kinematics.look_at_point(1.0, -0.5, 1.5)

    # # Move eyes only, without moving the head
    # Logger.info("Eye gaze only to (1.0, -0.2, 0.6) ...")
    # robot.kinematics.look_at_point(1.0, -0.2, 0.6, only_gaze=True)

    # Look at a pixel from the camera image (e.g. a detected face centre)
    # Logger.info("Looking at pixel (100, 240) at depth 1.0 m ...")
    # robot.kinematics.look_at_pixel(100, 240, depth=1.0)

    # Non-blocking variant — start the motion and do other work while waiting
    # Logger.info("Starting non-blocking look_at_point ...")
    # h = robot.kinematics.look_at_point_async(1.0, -1.0, 0.6)
    # Logger.info("Doing other work while head moves ...")
    # h.wait()
    # Logger.info("Head motion finished.")

    # # ----------------------------------------------------------------
    # # Head: utility — convert a pixel to a 3-D point (no motor movement)
    # # ----------------------------------------------------------------
    # pt = robot.kinematics.pixel_to_point(320, 240, depth=1.0)
    # Logger.info(f"Pixel (320, 240) at depth 1.0 m → {pt}")


    # # ----------------------------------------------------------------
    # # Arms: point/aim at a 3-D point (arm auto-selected by y sign)
    # # ----------------------------------------------------------------

    Logger.info("Aiming at (1.0, -0.1, 0.6) — right arm selected ...")
    robot.kinematics.aim_at_point(1.0, -0.5, 1.5)

    # Logger.info("Aiming at pixel (400, 300) at depth 1.0 m ...")
    # robot.kinematics.aim_at_pixel(400, 300, depth=1.0)

    # # Non-blocking arm motion with explicit velocity
    # Logger.info("Starting non-blocking reach_left with velocity=30 ...")
    # h = robot.kinematics.reach_left_async(1.0, 0.2, 0.6, velocity=30)
    # h.wait()
    # Logger.info("Left arm motion finished.")

    # # Cancel an in-flight action
    # Logger.info("Starting reach_right, then cancelling it ...")
    # h = robot.kinematics.reach_right_async(1.0, -0.3, 0.6)
    # time.sleep(0.3)
    # h.cancel()
    # Logger.info("Action cancelled.")
    

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.face.look([0, 0], [0, 0])  # look straight ahead before closing
        robot.motor.home_all()
        time.sleep(1)  # wait for homing to finish before closing connection
        robot.close()
