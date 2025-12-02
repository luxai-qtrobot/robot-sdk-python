# test_say.py
import time
import inspect

from luxai.magpie.utils import Logger
from luxai.magpie.frames import AudioFrameFlac
from luxai.robot.core import Robot, wait_all



def list_methods(obj, prefix=""):
    for name, value in inspect.getmembers(obj):
        if inspect.isroutine(value):
            print(prefix + name + "()")
        elif not name.startswith("__") and not inspect.isbuiltin(value) and not inspect.isclass(value):
            # recurse into subobjects
            list_methods(value, prefix + name + ".")

def audio_frame_callback(data):
    # print(data)
    f = AudioFrameFlac.from_dict(data) 
    print(f"received: {f}")

def joint_state_callback(data):
    # print(data)
    # f = AudioFrameFlac.from_dict(data) 
    print(f"received: {data}")


def main():
    # Replace with your robot’s IP

    # print(list_methods(Robot))
    # 1) Connect to robot via ZMQ
    # robot = Robot.connect_zmq(endpoint="tcp://192.168.3.152:50557")    
    robot = Robot.connect_zmq(node_id="QTPC")
    print("Connected to robot.")

    # mic = robot.microphone.stream.open_channel0_reader()
    # data, _ = mic.read()
    # f = AudioFrameFlac.from_dict(data)    
    # print(f)
    # mic.close()

    # sub = robot.microphone.stream.on_channel0(audio_frame_callback)

    # robot.motors.stream.on_joints_state(joint_state_callback)

    # print("calling speech..")
    # h = robot.speech.say("Hello! this is very long text. i am talking but youcan stop me if you want.", blocking=False)
    # print("waiting it finishes..")
    # time.sleep(3)
    # h.cancel()
    # print("canceled")

    h1 = robot.speech.say("Hello! this is very long text. i am talking but youcan stop me if you want.", blocking=False)
    h2 = robot.emotion.show("QT/happy", blocking=False)
    print("waiting for action...")
    wait_all([h1, h2])
    print("all action done!")
    # try:
    #     print(robot.speech.config(language="en-US", speed=80).result())
    #     robot.speech.say("Hello! this is Cutee robot.")

    #     print(robot.speech.config(language="en-US", speed=110).result())
    #     robot.speech.say("Hello! this is Cutee robot.")

    #     print(robot.speech.config(language="en-US", speed=70).result())
    #     robot.speech.say("Hello! this is Cutee robot.")
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

