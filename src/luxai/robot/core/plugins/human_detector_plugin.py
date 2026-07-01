from luxai.magpie.transport import ZMQRpcResponder, ZmqStreamWriter
from luxai.magpie.utils import Logger
from luxai.robot.core.transport import Transport
from luxai.robot.perception.vision.human_detector import HumanDetectorNode, PRESENCE_TOPIC

from .robot_plugin import RobotPlugin


class HumanDetectorPlugin(RobotPlugin):

    def __init__(self):
        super().__init__(plugin_name="human-detector")
        self._node: HumanDetectorNode = None
        self._transport: Transport = None

    def start(self, robot: "Robot", transport: Transport) -> None:
        try:
            self.stop()
        except Exception:
            pass

        self._transport = transport
        n = self.plugin_name

        self._node = HumanDetectorNode(
            robot=robot,
            responder=ZMQRpcResponder(f"inproc://{n}-rpc", bind=True),
            stream_writer=ZmqStreamWriter(f"inproc://{n}-stream", bind=True, queue_size=10),
            name=n,
        )

        robot._setup_rpc_routes(transport, {
            f"/{n}/configure": {"transports": {"zmq": {"endpoint": f"inproc://{n}-rpc"}}},
        })
        robot._setup_stream_routes(transport, {
            PRESENCE_TOPIC: {"transports": {"zmq": {"endpoint": f"inproc://{n}-stream", "queue_size": 10}}},
        })

        Logger.debug(f"{n} plugin started.")

    def stop(self) -> None:
        if self._node is not None:
            self._node.terminate()
            self._node = None

        if self._transport is not None:
            self._transport.close()
            self._transport = None
            Logger.debug(f"{self.plugin_name} plugin stopped.")
