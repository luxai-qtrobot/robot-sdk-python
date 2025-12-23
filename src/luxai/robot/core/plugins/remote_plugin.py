
from typing import Any, Dict
from luxai.magpie.utils import Logger
from .robot_plugin import RobotPlugin
from luxai.robot.core.transport import Transport

class RemotePlugin(RobotPlugin):

    def __init__(self, plugin_name: str):
        self._transport: Transport = None
        super().__init__(plugin_name=plugin_name)
        
        
    # --------------------------------------------------
    # RobotPlugin: start plugin
    # --------------------------------------------------
    def start(self, robot: "Robot", transport: Transport) -> None:        
        try:
            self.stop()
        except Exception as e:
            pass         

        self._transport  = transport
        # get system info 
        try:
            requester = self._transport.get_requester(self.plugin_name, None)
            rpc_req = {"name": "", "args": {}}
            raw = requester.call(rpc_req, timeout=5.0)

        except Exception as e:
            Logger.error(f"{self.plugin_name} system describe RPC failed: {e}")
            raise e

        if not isinstance(raw, dict) or not raw.get("status"):
            Logger.error(f"{self.plugin_name} system describe returned invalid payload or status=False.")
            raise e

        desc: Dict[str, Any] = raw.get("response") or {}

        # --- add plugin rpc routes ---                
        robot._setup_rpc_routes(self._transport, desc.get("rpc", {}))

        # --- add plugin stream routes ---                
        robot._setup_stream_routes(self._transport, desc.get("stream", {}))

        Logger.debug(f"{self.plugin_name} plugin started.")

    # --------------------------------------------------
    # RobotPlugin: stop plugin
    # --------------------------------------------------
    def stop(self) -> None:
        if self._transport is not None:
            self._transport.close()
            self._transport = None
            Logger.debug(f"{self.plugin_name} plugin stopped.")



class RealsenseDriverPlugin(RemotePlugin):

    def __init__(self):        
        super().__init__(plugin_name="realsense-driver")
