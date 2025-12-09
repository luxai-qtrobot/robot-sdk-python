
from luxai.magpie.transport import ZMQRpcResponder, ZMQPublisher
from luxai.robot.perception.asr import ASRAzureNode
from .robot_plugin import RobotPlugin


class ASRAzurePlugin(RobotPlugin):

    def __init__(self):
        super().__init__(plugin_name="asr-azure")
        self.azure_node : ASRAzureNode = None
        

    # --------------------------------------------------
    # RobotPlugin: start plugin
    # --------------------------------------------------
    def start(self, robot: "Robot") -> None:
        try:
            self.stop()
        except Exception as e:
            pass 
        self.azure_node = ASRAzureNode(
            robot=robot,
            responder=ZMQRpcResponder(f"inproc://{self.plugin_name}-rpc", bind=True),
            stream_writer=ZMQPublisher(f"inproc://{self.plugin_name}-stream", bind=True, queue_size=10),
            name=self.plugin_name,                      
        )


    # --------------------------------------------------
    # RobotPlugin: stop plugin
    # --------------------------------------------------
    def stop(self) -> None:
        if self.azure_node is not None:
            self.azure_node.terminate()
            self.azure_node = None
        
