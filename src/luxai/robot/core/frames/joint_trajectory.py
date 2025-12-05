from dataclasses import dataclass, field
from typing import Dict, Any, Iterable, Mapping, List, Optional

from luxai.magpie.frames import DictFrame


# ---------------------------------------------------------------------------
# JointTrajectoryFrame
# ---------------------------------------------------------------------------

@dataclass
class JointTrajectoryFrame(DictFrame):
    """
    Helper for building joint trajectories to *send* to the robot.

    Underlying wire format (DictFrame.value):

        {
            "points": [
                {
                    "time_from_start": 0.0,   # seconds, relative to start
                    "joints": {
                        "RightShoulderPitch": {
                            "position": -88.6,
                            # "velocity":     0.0,  # optional
                            # "acceleration": 0.0,  # optional
                            # "effort":       0.0,  # optional
                        },
                        "RightElbowRoll": {
                            "position": -31.9,
                        },
                        ...
                    },
                },
                ...
            ]
        }

    Usage example:

        stream = transport.get_stream_writer("/qt_robot/joints/trajectory", transports=opts)
        traj = JointTrajectoryFrame()
        traj.add_point(
            time_from_start=0.0,
            joints={
                "HeadPitch": {"position": 0.1},
                "HeadYaw":   {"position": 0.0},
            },
        )
        stream.write(traj.to_dict())
    """

    value: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        # Ensure "points" list exists
        if "points" not in self.value or not isinstance(self.value["points"], list):
            self.value["points"] = []
        # # JointTrajectoryFrame is meta helper frame and the underlying wire frame must be DictFrame! 
        # self.name = "DictFrame"

    # --- public API -------------------------------------------------------

    def points(self) -> List[Dict[str, Any]]:
        """Return the list of trajectory points (each a dict)."""
        return self.value["points"]

    def add_point(
        self,
        time_from_start: float,
        joints: Mapping[str, Mapping[str, float]],
    ) -> None:
        """
        Add a trajectory point with multiple joints.

        Parameters
        ----------
        time_from_start:
            Time from the start of trajectory (in seconds).
        joints:
            Mapping from joint name to dict of fields, e.g.:

                {
                    "HeadYaw": {
                        "position": -0.5,
                        "velocity": 0.0,      # optional
                        "acceleration": 0.0,  # optional
                        "effort": 0.0,        # optional
                    },
                    ...
                }

            Any extra numeric fields will be passed through.
        """
        # Normalize to plain dict-of-dicts
        norm_joints: Dict[str, Dict[str, float]] = {}
        for name, vals in joints.items():
            norm_joints[name] = dict(vals)

        point = {
            "time_from_start": float(time_from_start),
            "joints": norm_joints,
        }
        self.value["points"].append(point)

    def add_single_joint_point(
        self,
        time_from_start: float,
        joint_name: str,
        position: float,
        velocity: Optional[float] = None,
        acceleration: Optional[float] = None,
        effort: Optional[float] = None,
    ) -> None:
        """
        Convenience helper to add a point with a single joint.

        Example:

            traj.add_single_joint_point(
                time_from_start=0.5,
                joint_name="HeadPitch",
                position=0.3,
                velocity=0.0,
            )
        """
        joint_data: Dict[str, float] = {"position": float(position)}
        if velocity is not None:
            joint_data["velocity"] = float(velocity)
        if acceleration is not None:
            joint_data["acceleration"] = float(acceleration)
        if effort is not None:
            joint_data["effort"] = float(effort)

        self.add_point(
            time_from_start=time_from_start,
            joints={joint_name: joint_data},
        )

    def clear_points(self) -> None:
        """Remove all trajectory points."""
        self.value["points"].clear()

    def __str__(self) -> str:
        n = len(self.value.get("points", []))
        return f"{self.name}#{self.gid}:{self.id}(points={n})"



@dataclass
class JointCommandFrame(DictFrame):
    """
    A single-shot joint command frame (non-trajectory).

    Wire format (DictFrame.value):

        {
            "RightShoulderPitch": {"position": -88.6, "velocity": 0.0, ...},
            "RightElbowRoll":     {"position": -31.9},
            ...
        }
    """

    value: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # ----------------------------------------------------------------------
    # Internal helper to normalize joint fields
    # ----------------------------------------------------------------------
    def _normalize_fields(
        self,
        *,
        position: Optional[float] = None,
        velocity: Optional[float] = None,
        acceleration: Optional[float] = None,
        effort: Optional[float] = None,
        **extra,
    ) -> Dict[str, float]:
        fields: Dict[str, float] = {}

        if position is not None:
            fields["position"] = float(position)
        if velocity is not None:
            fields["velocity"] = float(velocity)
        if acceleration is not None:
            fields["acceleration"] = float(acceleration)
        if effort is not None:
            fields["effort"] = float(effort)

        # Allow custom numeric fields
        for key, val in extra.items():
            if isinstance(val, (float, int)):
                fields[key] = float(val)

        return fields

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------
    def set_joint(self, joint: str, **fields) -> None:
        """
        Create or update joint command.

        Example:
            cmd.set_joint("HeadYaw", position=0.3)
            cmd.set_joint("HeadYaw", velocity=0.0)  # ← updates existing
        """
        normalized = self._normalize_fields(**fields)

        if joint not in self.value:
            # First-time assignment
            self.value[joint] = normalized
        else:
            # Update existing fields
            self.value[joint].update(normalized)

    def joints(self):
        """Return list of all commanded joints."""
        return self.value.keys()

    def joint_dict(self, joint: str) -> Dict[str, float]:
        """Return a copy of joint command dict, or raise KeyError."""
        if joint not in self.value:
            raise KeyError(f"Joint '{joint}' not found.")
        return dict(self.value[joint])

    def clear(self):
        """Remove all joint commands."""
        self.value.clear()

    def __str__(self):
        names = list(self.value.keys())
        preview = ", ".join(names[:5])
        if len(names) > 5:
            preview += ", ..."
        return f"{self.name}#{self.gid}:{self.id}(joints={len(names)}: [{preview}])"
    