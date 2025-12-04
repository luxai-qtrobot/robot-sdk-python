
from luxai.magpie.utils import Logger
from luxai.magpie.frames import Frame, AudioFrameFlac, BoolFrame, IntFrame, DictFrame

from luxai.robot.core.transport import ZmqTransport

if __name__ == "__main__":
    Logger.set_level("DEBUG")
    transport = ZmqTransport(node_id="QTPC")
    defualt_options =  {
        "zmq": {
            "endpoint": f"tcp://*:50555",
            "delivery": "latest",
            "queue_size": 1,
        },
    }
    stream = transport.get_stream_reader("/qt_robot/joints/state", transports=defualt_options)
    
    transport.close()
 