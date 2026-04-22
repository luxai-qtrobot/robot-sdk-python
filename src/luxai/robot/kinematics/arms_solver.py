from typing import List, Sequence

import numpy as np


class ArmsSolver:
    # Physical offsets (metres)
    _D1 = 0.4   # base frame → shoulder frame along z
    _D2 = 0.12  # shoulder frame → elbow origin along z
    _D3 = 0.26  # elbow → end-effector along x (not used in IK, kept for reference)

    # Joint limits (degrees)
    _SHOULDER_PITCH_LIMIT = (-140.0, 140.0)
    _SHOULDER_ROLL_LIMIT  = ( -75.0,  -5.0)

    # Fixed elbow orientation (degrees)
    _ELBOW_ROLL_DEG = -7.0

    def calculate_right_arm_angles(self, xyz: Sequence[float]) -> List[float]:
        """IK for right arm: target [x,y,z] in base frame → [pitch, roll, elbow] degrees."""
        return self._solve(xyz, side="right")

    def calculate_left_arm_angles(self, xyz: Sequence[float]) -> List[float]:
        """IK for left arm: target [x,y,z] in base frame → [pitch, roll, elbow] degrees."""
        return self._solve(xyz, side="left")

    def _solve(self, xyz: Sequence[float], side: str) -> List[float]:
        x, y, z = xyz
        z    -= self._D1
        y    -= self._D2
        d_xz  = np.hypot(x, z)

        if side == "left":
            t1 = -np.arctan2(z, x)
            t2 = -np.arctan2(d_xz,  y)
        else:
            t1 =  np.arctan2(z, x)
            t2 = -np.arctan2(d_xz, -y)

        t3 = np.radians(self._ELBOW_ROLL_DEG)

        t1 = np.clip(t1, np.radians(self._SHOULDER_PITCH_LIMIT[0]), np.radians(self._SHOULDER_PITCH_LIMIT[1]))
        t2 = np.clip(t2, np.radians(self._SHOULDER_ROLL_LIMIT[0]),  np.radians(self._SHOULDER_ROLL_LIMIT[1]))

        return [float(np.degrees(t1)), float(np.degrees(t2)), float(np.degrees(t3))]
