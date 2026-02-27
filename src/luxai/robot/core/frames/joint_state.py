from dataclasses import dataclass, field
from typing import Dict, Any, Iterable, Mapping, List, Optional

from luxai.magpie.frames import DictFrame


# ---------------------------------------------------------------------------
# JointStateFrame
# ---------------------------------------------------------------------------

@dataclass
class JointStateFrame(DictFrame):
    """
    High-level helper for joint state messages.

    Underlying wire format (DictFrame.value):

        {
            "HeadYaw": {
                "position": 0.0,
                "velocity": 0.0,
                "effort":   0.0,
                "temperature": 0.0,
                "voltage":     0.0,
            },
            "HeadPitch": {
                "position": 0.0,
                "velocity": 0.0,
                "effort":   0.0,
                "temperature": 0.0,
                "voltage":     0.0,
            },
            ...
        }
    """

    value: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # --- internal helpers -------------------------------------------------

    def _require_joint(self, joint: str) -> Dict[str, float]:
        try:
            return self.value[joint]
        except KeyError as exc:
            available = ", ".join(sorted(self.value.keys())) or "<none>"
            raise KeyError(
                f"Joint '{joint}' not found in JointStateFrame. "
                f"Available joints: {available}"
            ) from exc

    def _require_field(self, joint: str, field_name: str) -> float:
        data = self._require_joint(joint)
        try:
            return float(data[field_name])
        except KeyError as exc:
            raise KeyError(
                f"Field '{field_name}' missing for joint '{joint}' "
                f"in JointStateFrame."
            ) from exc

    # --- public API -------------------------------------------------------

    def joints(self) -> Iterable[str]:
        """Return an iterable of all joint names present in this frame."""
        return self.value.keys()

    def position(self, joint: str) -> float:
        """Return position of the given joint, or raise KeyError if unknown."""
        return self._require_field(joint, "position")

    def velocity(self, joint: str) -> float:
        """Return velocity of the given joint, or raise KeyError if unknown."""
        return self._require_field(joint, "velocity")

    def effort(self, joint: str) -> float:
        """Return effort of the given joint, or raise KeyError if unknown."""
        return self._require_field(joint, "effort")

    def temperature(self, joint: str) -> float:
        """Return temperature of the given joint, or raise KeyError if unknown."""
        return self._require_field(joint, "temperature")

    def voltage(self, joint: str) -> float:
        """Return voltage of the given joint, or raise KeyError if unknown."""
        return self._require_field(joint, "voltage")

    def joint_dict(self, joint: str) -> Dict[str, float]:
        """
        Return the full dict for a joint (position/velocity/effort/extra fields)
        or raise KeyError if the joint does not exist.
        """
        return dict(self._require_joint(joint))

    def __str__(self) -> str:
        names = list(self.value.keys())
        preview = ", ".join(names[:5])
        if len(names) > 5:
            preview += ", ..."
        return (
            f"{self.name}#{self.gid}:{self.id}"
            f"(joints={len(names)}: [{preview}])"
        )

