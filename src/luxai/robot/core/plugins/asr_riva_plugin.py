from luxai.magpie.transport import ZMQRpcResponder, ZmqStreamWriter
from luxai.magpie.utils import Logger
from luxai.robot.core.transport import Transport
from luxai.robot.perception.asr import ASRRivaNode

from .robot_plugin import RobotPlugin


class ASRRivaPlugin(RobotPlugin):

    def __init__(self):
        super().__init__(plugin_name="asr-riva")
        self.riva_node: ASRRivaNode = None
        self._transport: Transport = None

    # --------------------------------------------------
    # RobotPlugin: start plugin
    # --------------------------------------------------
    def start(self, robot: "Robot", transport: Transport) -> None:
        try:
            self.stop()
        except Exception:
            pass

        self._transport = transport

        self.riva_node = ASRRivaNode(
            robot=robot,
            responder=ZMQRpcResponder(f"inproc://{self.plugin_name}-rpc", bind=True),
            stream_writer=ZmqStreamWriter(f"inproc://{self.plugin_name}-stream", bind=True, queue_size=10),
            name=self.plugin_name,
        )

        rpc = {
            '/asr-riva/configure':        {'transports': {'zmq': {"endpoint": "inproc://asr-riva-rpc"}}},
            '/asr-riva/recognize':        {'transports': {'zmq': {"endpoint": "inproc://asr-riva-rpc"}}},
            '/asr-riva/recognize/cancel': {'transports': {'zmq': {"endpoint": "inproc://asr-riva-rpc"}}},
        }

        stream = {
            '/asr-riva/speech': {'transports': {'zmq': {"endpoint": "inproc://asr-riva-stream", "queue_size": 10}}},
            '/asr-riva/event':  {'transports': {'zmq': {"endpoint": "inproc://asr-riva-stream", "queue_size": 10}}},
        }

        robot._setup_rpc_routes(transport, rpc)
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

        if self.riva_node is not None:
            self.riva_node.terminate()
            self.riva_node = None
