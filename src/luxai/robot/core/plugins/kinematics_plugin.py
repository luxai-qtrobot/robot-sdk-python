from luxai.magpie.transport import ZMQRpcResponder
from luxai.magpie.utils import Logger
from luxai.robot.core.transport import Transport
from luxai.robot.kinematics import KinematicsNode

from .robot_plugin import RobotPlugin


class KinematicsPlugin(RobotPlugin):

    def __init__(self):
        super().__init__(plugin_name="kinematics")
        self._kinematics_node: KinematicsNode = None
        self._transport: Transport = None

    # ------------------------------------------------------------------
    # RobotPlugin: start
    # ------------------------------------------------------------------
    def start(self, robot: "Robot", transport: Transport) -> None:
        try:
            self.stop()
        except Exception:
            pass

        self._transport = transport

        self._kinematics_node = KinematicsNode(
            robot=robot,
            responder=ZMQRpcResponder(f"inproc://{self.plugin_name}-rpc", bind=True),
            name=self.plugin_name,
        )

        rpc = {
            f"/{self.plugin_name}/configure":          {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/look_at_point":      {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/look_at_point/cancel": {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/look_at_pixel":      {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/look_at_pixel/cancel": {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/reach_right":        {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/reach_right/cancel": {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/reach_left":         {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/reach_left/cancel":  {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/aim_at_point":       {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/aim_at_point/cancel": {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/aim_at_pixel":       {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/aim_at_pixel/cancel": {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
            f"/{self.plugin_name}/pixel_to_point":     {"transports": {"zmq": {"endpoint": f"inproc://{self.plugin_name}-rpc"}}},
        }

        robot._setup_rpc_routes(transport, rpc)

        Logger.debug(f"{self.plugin_name} plugin started.")

    # ------------------------------------------------------------------
    # RobotPlugin: stop
    # ------------------------------------------------------------------
    def stop(self) -> None:
        if self._kinematics_node is not None:
            self._kinematics_node.terminate()
            self._kinematics_node = None

        if self._transport is not None:
            self._transport.close()
            self._transport = None
            Logger.debug(f"{self.plugin_name} plugin stopped.")
