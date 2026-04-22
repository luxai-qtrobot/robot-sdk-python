from __future__ import annotations

import threading
import time
from typing import Any, Dict, List, Optional

from luxai.magpie.nodes import ServerNode
from luxai.magpie.transport import RpcResponder
from luxai.magpie.utils import Logger
from luxai.robot.core.frames import JointStateFrame, JointCommandFrame

from .head_solver import HeadSolver
from .arms_solver import ArmsSolver


class KinematicsNode(ServerNode):

    # Head movement threshold: if error is below this, skip head command (eyes-only)
    _LOOK_THRESHOLD_DEG  = 10.0
    # Eye gaze offset clamp (pixels from centre)
    _GAZE_CLIP_DEG       = 20.0

    # Two-phase motor wait thresholds (deg/s)
    _VEL_START_THRESHOLD = 1.0   # above → motors have started
    _VEL_STOP_THRESHOLD  = 0.5   # below → motors have stopped
    _PHASE1_TIMEOUT      = 1.5   # seconds to wait for motors to start

    # Poll interval for wait loops
    _POLL_INTERVAL = 0.025

    def __init__(
        self,
        robot: Any,
        responder: RpcResponder,
        name: str = "kinematics",
    ) -> None:
        self._robot        = robot
        self._head_solver  = HeadSolver()
        self._arms_solver  = ArmsSolver()
        self._motor_timeout = 20.0

        # Joint state cache — updated by background callback
        self._joint_lock      = threading.Lock()
        self._joint_positions: Dict[str, float] = {}
        self._joint_velocities: Dict[str, float] = {}

        # Serialise actions; cancel_event interrupts the running wait loop
        self._action_lock   = threading.Lock()
        self._cancel_event  = threading.Event()

        # Lazy command writer
        self._cmd_writer      = None
        self._cmd_writer_lock = threading.Lock()

        # Signalled by _on_joint_state on the first frame — used to block
        # until the subscriber is live and the position cache is populated.
        self._joint_state_ready = threading.Event()

        # Subscribe to joint state stream (background callback, always live)
        self._robot.motor.stream.on_joints_state(self._on_joint_state)

        # Wait for the first joint state frame so the position cache is
        # populated before the node accepts any RPC commands.
        if not self._joint_state_ready.wait(timeout=5.0):
            raise RuntimeError(
                f"{name}: timed out waiting for joint state stream. "
                "Check that the robot motor service is running and the connection is healthy."
            )

        super().__init__(
            name=name,
            responder=responder,
            handler=self._on_rpc_request,
        )

    # ------------------------------------------------------------------
    # Joint state callback
    # ------------------------------------------------------------------
    def _on_joint_state(self, frame: JointStateFrame) -> None:
        with self._joint_lock:
            for joint in frame.joints():
                self._joint_positions[joint]  = frame.position(joint)
                self._joint_velocities[joint] = frame.velocity(joint)
        self._joint_state_ready.set()

    def _cached_positions(self, names: List[str]) -> Dict[str, float]:
        with self._joint_lock:
            return {n: self._joint_positions.get(n, 0.0) for n in names}

    def _cached_velocities(self, names: List[str]) -> Dict[str, float]:
        with self._joint_lock:
            return {n: self._joint_velocities.get(n, 0.0) for n in names}

    # ------------------------------------------------------------------
    # Motor command writer (lazy init)
    # ------------------------------------------------------------------
    def _get_writer(self):
        with self._cmd_writer_lock:
            if self._cmd_writer is None:
                self._cmd_writer = self._robot.motor.stream.open_joints_command_writer()
            return self._cmd_writer

    def _send_command(self, joint_angles: Dict[str, float], velocity: float = 0.0) -> None:
        cmd = JointCommandFrame()
        for name, angle in joint_angles.items():
            if velocity > 0.0:
                cmd.set_joint(name, position=float(angle), velocity=float(velocity))
            else:
                cmd.set_joint(name, position=float(angle))
        self._get_writer().write(cmd)

    # ------------------------------------------------------------------
    # Two-phase motor wait
    # ------------------------------------------------------------------
    def _wait_for_joints_done(self, joint_names: List[str]) -> bool:
        """
        Phase 1: wait up to _PHASE1_TIMEOUT for at least one joint to start moving.
        Phase 2: wait up to _motor_timeout for all joints to stop moving.
        Returns False if cancelled, True otherwise.
        """
        deadline       = time.monotonic() + self._motor_timeout
        phase1_deadline = time.monotonic() + self._PHASE1_TIMEOUT

        # Phase 1 — wait for motion to begin
        started = False
        while time.monotonic() < phase1_deadline:
            if self._cancel_event.is_set():
                return False
            vels = self._cached_velocities(joint_names)
            if any(abs(v) > self._VEL_START_THRESHOLD for v in vels.values()):
                started = True
                break
            time.sleep(self._POLL_INTERVAL)

        if not started:
            # Joints were already at (or very near) the commanded position
            return True

        # Phase 2 — wait for motion to stop
        while time.monotonic() < deadline:
            if self._cancel_event.is_set():
                return False
            vels = self._cached_velocities(joint_names)
            if all(abs(v) <= self._VEL_STOP_THRESHOLD for v in vels.values()):
                return True
            time.sleep(self._POLL_INTERVAL)

        return True  # hard-cap reached — return anyway

    # ------------------------------------------------------------------
    # RPC dispatcher
    # ------------------------------------------------------------------
    def _on_rpc_request(self, req: object) -> Dict[str, Any]:
        if req is None or not isinstance(req, dict):
            return {"status": False, "response": None}
        try:
            name = req["name"]
            args = req.get("args") or {}
        except Exception:
            return {"status": False, "response": None}

        try:
            n = self.name   # e.g. "kinematics"
            if   name == f"/{n}/configure":
                response = self._handle_configure(args)
            elif name == f"/{n}/look_at_point":
                response = self._handle_look_at_point(args)
            elif name == f"/{n}/look_at_pixel":
                response = self._handle_look_at_pixel(args)
            elif name == f"/{n}/reach_right":
                response = self._handle_reach_right(args)
            elif name == f"/{n}/reach_left":
                response = self._handle_reach_left(args)
            elif name == f"/{n}/aim_at_point":
                response = self._handle_aim_at_point(args)
            elif name == f"/{n}/aim_at_pixel":
                response = self._handle_aim_at_pixel(args)
            elif name == f"/{n}/pixel_to_point":
                response = self._handle_pixel_to_point(args)
            elif name.endswith("/cancel"):
                response = self._handle_cancel(args)
            else:
                Logger.warning(f"{self.name}: unknown RPC '{name}'")
                return {"status": False, "response": None}

            return {"status": True, "response": response}

        except Exception as e:
            Logger.warning(f"{self.name}: error handling '{name}': {e}")
            return {"status": False, "response": None}

    # ------------------------------------------------------------------
    # configure
    # ------------------------------------------------------------------
    def _handle_configure(self, args: dict) -> bool:
        self._head_solver.configure(
            fx             = args.get("fx"),
            fy             = args.get("fy"),
            ppx            = args.get("ppx"),
            ppy            = args.get("ppy"),
            img_cx         = args.get("img_cx"),
            img_cy         = args.get("img_cy"),
            camera_height  = args.get("camera_height"),
        )
        if "motor_timeout" in args:
            self._motor_timeout = float(args["motor_timeout"])
        return True

    # ------------------------------------------------------------------
    # look_at_point / look_at_pixel
    # ------------------------------------------------------------------
    def _handle_look_at_point(self, args: dict) -> bool:
        with self._action_lock:
            self._cancel_event.clear()
            return self._look_at_xyz(
                [args["x"], args["y"], args["z"]],
                only_gaze = bool(args.get("only_gaze", False)),
                velocity  = float(args.get("velocity", 0.0)),
            )

    def _handle_look_at_pixel(self, args: dict) -> bool:
        with self._action_lock:
            self._cancel_event.clear()
            with self._joint_lock:
                head_yaw   = self._joint_positions.get("HeadYaw",   0.0)
                head_pitch = self._joint_positions.get("HeadPitch",  0.0)
            xyz = self._head_solver.pixel_to_base(
                [args["u"], args["v"]], float(args.get("depth", 1.0)),
                head_yaw, head_pitch,
            )
            return self._look_at_xyz(
                xyz,
                only_gaze = bool(args.get("only_gaze", False)),
                velocity  = float(args.get("velocity", 0.0)),
            )

    def _look_at_xyz(self, xyz: List[float], only_gaze: bool, velocity: float) -> bool:
        """Internal: compute head IK, send gaze + optional head command, wait."""
        head_angles = self._head_solver.calculate_head_angles(xyz)
        
        with self._joint_lock:
            cur_yaw   = self._joint_positions.get("HeadYaw",  0.0)
            cur_pitch = self._joint_positions.get("HeadPitch", 0.0)        
        yaw_diff   = head_angles[0] - cur_yaw
        pitch_diff = head_angles[1] - cur_pitch

        # Eye gaze: clipped angular difference → pixel offset
        xp = int(max(-self._GAZE_CLIP_DEG, min(self._GAZE_CLIP_DEG, yaw_diff)))
        yp = int(max(-self._GAZE_CLIP_DEG, min(self._GAZE_CLIP_DEG, pitch_diff)))
        self._robot.face.look(l_eye=[xp, yp], r_eye=[xp, yp])

        if only_gaze:
            return True

        # Skip head movement if already within threshold
        if (abs(yaw_diff)   < self._LOOK_THRESHOLD_DEG and
                abs(pitch_diff) < self._LOOK_THRESHOLD_DEG):
            return True

        self._send_command({"HeadYaw": head_angles[0], "HeadPitch": head_angles[1]}, velocity)
        self._wait_for_joints_done(["HeadYaw", "HeadPitch"])
        return True

    # ------------------------------------------------------------------
    # reach_right / reach_left
    # ------------------------------------------------------------------
    def _handle_reach_right(self, args: dict) -> bool:
        with self._action_lock:
            self._cancel_event.clear()
            angles = self._arms_solver.calculate_right_arm_angles(
                [args["x"], args["y"], args["z"]]
            )
            joints = {
                "RightShoulderPitch": angles[0],
                "RightShoulderRoll":  angles[1],
                "RightElbowRoll":     angles[2],
            }
            self._send_command(joints, float(args.get("velocity", 0.0)))
            self._wait_for_joints_done(list(joints.keys()))
            return True

    def _handle_reach_left(self, args: dict) -> bool:
        with self._action_lock:
            self._cancel_event.clear()
            angles = self._arms_solver.calculate_left_arm_angles(
                [args["x"], args["y"], args["z"]]
            )
            joints = {
                "LeftShoulderPitch": angles[0],
                "LeftShoulderRoll":  angles[1],
                "LeftElbowRoll":     angles[2],
            }
            self._send_command(joints, float(args.get("velocity", 0.0)))
            self._wait_for_joints_done(list(joints.keys()))
            return True

    # ------------------------------------------------------------------
    # aim_at_point / aim_at_pixel
    # ------------------------------------------------------------------
    def _handle_aim_at_point(self, args: dict) -> bool:
        with self._action_lock:
            self._cancel_event.clear()
            return self._aim_at_xyz(
                [args["x"], args["y"], args["z"]],
                velocity = float(args.get("velocity", 0.0)),
            )

    def _handle_aim_at_pixel(self, args: dict) -> bool:
        with self._action_lock:
            self._cancel_event.clear()
            with self._joint_lock:
                head_yaw   = self._joint_positions.get("HeadYaw",   0.0)
                head_pitch = self._joint_positions.get("HeadPitch",  0.0)
            xyz = self._head_solver.pixel_to_base(
                [args["u"], args["v"]], float(args.get("depth", 1.0)),
                head_yaw, head_pitch,
            )
            return self._aim_at_xyz(xyz, velocity=float(args.get("velocity", 0.0)))

    def _aim_at_xyz(self, xyz: List[float], velocity: float) -> bool:
        """Internal: select arm by y sign, compute IK, send command, wait."""
        if xyz[1] >= 0.0:
            angles = self._arms_solver.calculate_left_arm_angles(xyz)
            joints = {
                "LeftShoulderPitch": angles[0],
                "LeftShoulderRoll":  angles[1],
                "LeftElbowRoll":     angles[2],
            }
        else:
            angles = self._arms_solver.calculate_right_arm_angles(xyz)
            joints = {
                "RightShoulderPitch": angles[0],
                "RightShoulderRoll":  angles[1],
                "RightElbowRoll":     angles[2],
            }
        self._send_command(joints, velocity)
        self._wait_for_joints_done(list(joints.keys()))
        return True

    # ------------------------------------------------------------------
    # pixel_to_point  (utility — no wait, no cancel)
    # ------------------------------------------------------------------
    def _handle_pixel_to_point(self, args: dict) -> Dict[str, float]:
        with self._joint_lock:
            head_yaw   = self._joint_positions.get("HeadYaw",   0.0)
            head_pitch = self._joint_positions.get("HeadPitch",  0.0)
        xyz = self._head_solver.pixel_to_base(
            [args["u"], args["v"]], float(args.get("depth", 1.0)),
            head_yaw, head_pitch,
        )
        return {"x": xyz[0], "y": xyz[1], "z": xyz[2]}

    # ------------------------------------------------------------------
    # cancel
    # ------------------------------------------------------------------
    def _handle_cancel(self, args: dict) -> bool:
        self._cancel_event.set()
        return True

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def terminate(self, timeout: Optional[float] = None) -> None:
        self._cancel_event.set()
        with self._cmd_writer_lock:
            if self._cmd_writer is not None:
                try:
                    self._cmd_writer.close()
                except Exception:
                    pass
                self._cmd_writer = None
        return super().terminate(timeout)
