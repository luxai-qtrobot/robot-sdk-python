# test_say.py
import time
import inspect
import random
from luxai.magpie.utils import Logger
from luxai.magpie.frames import Frame, AudioFrameFlac
from luxai.robot.core.frames import JointStateFrame, LedColorFrame, JointCommandFrame
from luxai.robot.core import Robot, wait_all_actions, wait_any_action


def on_mic_0(data:AudioFrameFlac):
    Logger.info(data)


def main():
    Logger.set_level("DEBUG")

    robot = Robot.connect_zmq(endpoint="tcp://192.168.3.152:50557")    
    # robot = Robot.connect_zmq(node_id="QTPC")
    Logger.info("Connected to robot.")

    
    robot.speaker.set_volume(60)

    Logger.info("calling speech.say()...")
    h1 = robot.speech.say("Hello. this is a test of the QT robot SDK for Python.", blocking=False)
    time.sleep(2)
    Logger.info("cancelling speech...")
    h1.cancel()
    Logger.info("speech cancelled.")



    # joint_reader = robot.motors.stream.open_joints_reader()
    # state = joint_reader.read()
    # Logger.info(type(state))
    # Logger.info(state.position("HeadYaw"))
    # mic = robot.microphone.stream.on_channel0(on_mic_0)

    # led = robot.microphone.stream.open_led_writer()    

    # joints = robot.motors.stream.open_joints_writer()
    # cmd = JointCommandFrame()    
    # cmd.set_joint("HeadYaw", position=0)
    # cmd.set_joint("HeadPitch", position=0)
    # cmd.set_joint("RightShoulderPitch", position=-80)
    # cmd.set_joint("LeftShoulderPitch", position=80)
    # Logger.info(cmd)

    # mic_stream = robot.microphone.stream.open_channel0_reader()
    # frame  = mic_stream.read(timeout=None) # return AudioFrameFlac


    should_stop = False
    try:
        while(not should_stop):
            # joints.write(cmd)
            # color = LedColorFrame(
            #     r=random.random(), 
            #     g=random.random(), 
            #     b=random.random()
            #     )
            # led.write(color)
            time.sleep(3)
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

