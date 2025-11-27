# test_say.py

from luxai.magpie.utils import Logger
from luxai2.robot.core import Robot

def main():
    # Replace with your robot’s IP
    ROBOT_IP = "192.168.3.173"

    # 1) Connect to robot via ZMQ
    robot = Robot.connect_zmq(host=ROBOT_IP, default_timeout=10.0)

    print("Connected to robot.")

    try:
        res = robot.say_text("Hello this is blocking.").result(timeout=0.2)
        print("Speech action result:", res)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print("Error:", e)
    finally:
        robot.close()
        print("Closed transport.")

    # # 2) Send speech request
    # print("Sending say_text 1 request...")
    # handle = robot.say_text("Hello this is blocking.", blocking=True)
    # print("Sending say_text 2 request...")
    # handle = robot.say_text("Hello! This is not blocking.", blocking=False)

    # # 3) Example: wait for result
    # try:
    #     result = handle.result(timeout=60.0)
    #     print("Speech finished! Response:", result)

    # except Exception as e:
    #     print("Speech action error:", e)

    # # 4) Cleanup
    # robot.close()
    # print("Transport closed.")

if __name__ == "__main__":
    Logger.set_level("DEBUG")
    main()

