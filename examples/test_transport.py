import time
from luxai.magpie.utils import Logger
from luxai.robot.core.frames import JointStateFrame, MotorStateFrame, JointTrajectoryFrame

from luxai.robot.core.transport import ZmqTransport

if __name__ == "__main__":
    Logger.set_level("DEBUG")


    steam_in_options =  {
        "zmq": {
            "endpoint": f"tcp://*:50555",
            "delivery": "latest",
            "queue_size": 1,
        },
    }

    steam_out_options =  {
        "zmq": {
            "endpoint": f"tcp://*:50556",
            "delivery": "reliable",
            "queue_size": 10,
        },
    }

    transport = ZmqTransport(endpoint="tcp://192.168.3.152:50557")

    # stream = transport.get_stream_reader("/qt_robot/joints/state", transports=steam_in_options)
    # data, _ = stream.read()        
    # f = JointStateFrame.from_dict(data)    
    # print(f.joints())

    # stream = transport.get_stream_reader("/qt_robot/motors/states", transports=steam_in_options)
    # data, _ = stream.read()
    # f = MotorStateFrame.from_dict(data)    
    # print(f.motors())
    # print(f.temperature("HeadPitch"))

    
    traj_stream = transport.get_stream_writer("/qt_robot/joints/trajectory", transports=steam_out_options)    
    while True: 
        try:
            traj = JointTrajectoryFrame()
            traj.add_point(
                time_from_start=0.0,
                joints={
                    "HeadYaw":   {"position": 20.0},
                    "HeadPitch": {"position": 0.0},
                },
            )
            traj_stream.write(traj.to_dict(), "/qt_robot/joints/trajectory")
            time.sleep(2)
        except KeyboardInterrupt:
            Logger.info('stopping...')               
            break



    transport.close()
 