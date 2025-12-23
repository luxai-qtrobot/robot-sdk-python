
from luxai.magpie.transport import ZMQRpcResponder, ZMQPublisher
from luxai.magpie.utils import Logger
from luxai.robot.core.transport import Transport
from luxai.robot.perception.asr import ASRAzureNode

from .robot_plugin import RobotPlugin


class ASRAzurePlugin(RobotPlugin):

    def __init__(self):
        super().__init__(plugin_name="asr-azure")
        self.azure_node : ASRAzureNode = None
        self._transport: Transport = None
        

    # --------------------------------------------------
    # RobotPlugin: start plugin
    # --------------------------------------------------
    def start(self, robot: "Robot", transport: Transport) -> None:
        try:
            self.stop()
        except Exception as e:
            pass 
        
        self._transport  = transport

        self.azure_node = ASRAzureNode(
            robot=robot,
            responder=ZMQRpcResponder(f"inproc://{self.plugin_name}-rpc", bind=True),
            stream_writer=ZMQPublisher(f"inproc://{self.plugin_name}-stream", bind=True, queue_size=10),
            name=self.plugin_name,                      
        )

        rpc = {
            '/asr-azure/configure': {'transports': {'zmq': {"endpoint": "inproc://asr-azure-rpc"}}},
            '/asr-azure/recognize': {'transports': {'zmq': {"endpoint": "inproc://asr-azure-rpc"}}},
            '/asr-azure/recognize/cancel': {'transports': {'zmq': {"endpoint": "inproc://asr-azure-rpc"}}}
            }
        
        stream = {
            '/asr-azure/speech' : {'transports': {'zmq': {"endpoint": "inproc://asr-azure-stream", "queue_size": 10}}},
            '/asr-azure/event'  : {'transports': {'zmq': {"endpoint": "inproc://asr-azure-stream", "queue_size": 10}}}
        }

        # --- add plugin rpc routes ---
        robot._setup_rpc_routes(transport, rpc)
        # --- add plugin stream routes ---
        robot._setup_stream_routes(transport, stream)

        Logger.debug(f"{self.plugin_name} plugin started.")

    # --------------------------------------------------
    # RobotPlugin: stop plugin
    # --------------------------------------------------
    def stop(self) -> None:
        if self._transport is not None:
            self._transport.close()
            self._transport = None
            Logger.debug(f"{self.plugin_name} plugin stopped.")

        if self.azure_node is not None:
            self.azure_node.terminate()
            self.azure_node = None
        
