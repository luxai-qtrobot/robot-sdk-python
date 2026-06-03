from luxai.magpie.transport import ZMQRpcResponder, ZmqStreamWriter
from luxai.magpie.utils import Logger
from luxai.robot.core.transport import Transport
from luxai.robot.perception.asr import ASRParakeetNode

from .robot_plugin import RobotPlugin


class ASRParakeetPlugin(RobotPlugin):

    def __init__(self):
        super().__init__(plugin_name="asr-parakeet")
        self.parakeet_node: ASRParakeetNode = None
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

        self.parakeet_node = ASRParakeetNode(
            robot=robot,
            responder=ZMQRpcResponder(f"inproc://{self.plugin_name}-rpc", bind=True),
            stream_writer=ZmqStreamWriter(f"inproc://{self.plugin_name}-stream",
                                          bind=True, queue_size=10),
            name=self.plugin_name,
        )

        rpc = {
            f'/{self.plugin_name}/configure':        {'transports': {'zmq': {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f'/{self.plugin_name}/recognize':        {'transports': {'zmq': {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f'/{self.plugin_name}/recognize/cancel': {'transports': {'zmq': {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
        }

        stream = {
            f'/{self.plugin_name}/speech': {'transports': {'zmq': {"endpoint": f"inproc://{self.plugin_name}-stream", "queue_size": 10}}},
            f'/{self.plugin_name}/event':  {'transports': {'zmq': {"endpoint": f"inproc://{self.plugin_name}-stream", "queue_size": 10}}},
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

        if self.parakeet_node is not None:
            self.parakeet_node.terminate()
            self.parakeet_node = None
