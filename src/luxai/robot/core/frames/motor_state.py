from dataclasses import dataclass, field
from typing import Dict, Any, Iterable, Mapping, List, Optional

from luxai.magpie.frames import DictFrame


# ---------------------------------------------------------------------------
# MotorStateFrame
# ---------------------------------------------------------------------------

@dataclass
class MotorStateFrame(DictFrame):
    """
    High-level helper for motor state messages.

    Underlying wire format (DictFrame.value):

        {
            "HeadYaw": {
                "temperature": 0.0,
                "voltage":     0.0,
                # optional extra fields (current, error, etc.)
            },
            ...
        }
    """

    value: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # --- internal helpers -------------------------------------------------

    def _require_motor(self, motor: str) -> Dict[str, float]:
        try:
            return self.value[motor]
        except KeyError as exc:
            available = ", ".join(sorted(self.value.keys())) or "<none>"
            raise KeyError(
                f"Motor '{motor}' not found in MotorStateFrame. "
                f"Available motors: {available}"
            ) from exc

    def _get_field(self, motor: str, field_name: str) -> Optional[float]:
        data = self._require_motor(motor)
        val = data.get(field_name)
        return float(val) if val is not None else None

    # --- public API -------------------------------------------------------

    def motors(self) -> Iterable[str]:
        """Return an iterable of all motor names present in this frame."""
        return self.value.keys()

    def temperature(self, motor: str) -> Optional[float]:
        """
        Return temperature of a motor, or None if the field is missing.

        Raises KeyError if the motor name does not exist.
        """
        return self._get_field(motor, "temperature")

    def voltage(self, motor: str) -> Optional[float]:
        """
        Return voltage of a motor, or None if the field is missing.

        Raises KeyError if the motor name does not exist.
        """
        return self._get_field(motor, "voltage")

    def motor_dict(self, motor: str) -> Dict[str, float]:
        """Return the full dict for a motor, or raise KeyError if unknown."""
        return dict(self._require_motor(motor))

    def __str__(self) -> str:
        names = list(self.value.keys())
        preview = ", ".join(names[:5])
        if len(names) > 5:
            preview += ", ..."
        return (
            f"{self.name}#{self.gid}:{self.id}"
            f"(motors={len(names)}: [{preview}])"
        )

