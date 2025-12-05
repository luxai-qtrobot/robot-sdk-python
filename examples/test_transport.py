import time
from luxai.magpie.utils import Logger

from luxai.magpie.frames import *
from luxai.robot.core.frames import *

from luxai.robot.core.transport import ZmqTransport

if __name__ == "__main__":
    Logger.set_level("DEBUG")


    # steam_in_options =  {
    #     "zmq": {
    #         "endpoint": f"tcp://*:50555",
    #         "delivery": "latest",
    #         "queue_size": 1,
    #     },
    # }

    steam_out_options =  {
        "zmq": {
            "endpoint": f"tcp://*:50556",
            "delivery": "reliable",
            "queue_size": 10,
        },
    }

    transport = ZmqTransport(endpoint="tcp://192.168.3.152:50557")

    head = transport.get_stream_writer("/qt_robot/head_position/command", transports=steam_out_options)
    cmd = ListFrame(value=[20, 0])
    
    while True: 
        try:
            head.write(cmd.to_dict(), "/qt_robot/head_position/command")
            time.sleep(2)
        except KeyboardInterrupt:
            Logger.info('stopping...')               
            break



    transport.close()
 