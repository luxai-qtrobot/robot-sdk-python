"""
tests/test_kinematics_solvers.py

Verifies that the pure-math HeadSolver and ArmsSolver produce results
numerically identical to the original numpy-based implementations.

numpy is used here only as a reference oracle — it is NOT a runtime
dependency of the SDK.
"""
from __future__ import annotations

import math
import unittest

import numpy as np

from luxai.robot.kinematics.head_solver import HeadSolver
from luxai.robot.kinematics.arms_solver import ArmsSolver


# ---------------------------------------------------------------------------
# numpy reference implementations (verbatim from the original qt_kinematics)
# ---------------------------------------------------------------------------

class _NpHeadSolver:
    fx, fy        = 419.76220703125, 419.3450927734375
    ppx, ppy      = 421.1879577636719, 247.27752685546875
    cam_offset_z  = 0.09
    camera_height = 0.6
    img_cx, img_cy = 424, 240

    def calculate_head_angles(self, xyz):
        x, y, z = xyz
        yaw   = np.arctan2(y, x)
        d_xy  = np.sqrt(x**2 + y**2)
        pitch = np.arctan2(self.camera_height - z, d_xy)
        yaw   = np.clip(yaw,   np.radians(-60), np.radians(60))
        pitch = np.clip(pitch, np.radians(-25), np.radians(25))
        return [float(np.degrees(yaw)), float(np.degrees(pitch))]

    def calculate_xyz(self, yaw_deg, pitch_deg, depth):
        t1 = np.radians(yaw_deg);  t2 = np.radians(pitch_deg)
        return [float(depth * np.cos(t1)), float(depth * np.sin(t1)),
                float(self.camera_height - depth * np.sin(t2))]

    def pixel_to_camera(self, u, v, depth):
        u = u + (self.ppx - self.img_cx)
        v = v + (self.ppy - self.img_cy)
        return [float((u - self.ppx) * depth / self.fx),
                float((v - self.ppy) * depth / self.fy),
                float(depth + self.cam_offset_z)]

    def pixel_to_base(self, uv, depth, yaw_deg, pitch_deg):
        xyz_cam = self.pixel_to_camera(uv[0], uv[1], depth)
        t1 = np.radians(yaw_deg);  t2 = np.radians(pitch_deg)
        T01 = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0.34],[0,0,0,1]])
        c1,s1 = np.cos(t1), np.sin(t1)
        T12 = np.array([[c1,0,-s1,0],[s1,0,c1,0],[0,-1,0,0.1],[0,0,0,1]])
        c2,s2 = np.cos(t2), np.sin(t2)
        T23 = np.array([[0,-s2,c2,0.16*s2],[0,c2,s2,-0.16*c2],[-1,0,0,0],[0,0,0,1]])
        T = np.dot(np.dot(T01, T12), T23)
        p = np.dot(T, np.append(xyz_cam, 1))
        return [depth, float(p[1]), float(p[2])]


class _NpArmsSolver:
    D1, D2 = 0.4, 0.12
    _PITCH_LIM = (-140.0, 140.0)
    _ROLL_LIM  = (-75.0,   -5.0)
    _ELBOW     = -7.0

    def _solve(self, xyz, side):
        x, y, z = xyz
        z -= self.D1;  y -= self.D2
        d_xz = np.hypot(x, z)
        t1 = (-np.arctan2(z, x)   if side == "left" else  np.arctan2(z, x))
        t2 = (-np.arctan2(d_xz, y) if side == "left" else -np.arctan2(d_xz, -y))
        t3 = np.radians(self._ELBOW)
        t1 = np.clip(t1, np.radians(self._PITCH_LIM[0]), np.radians(self._PITCH_LIM[1]))
        t2 = np.clip(t2, np.radians(self._ROLL_LIM[0]),  np.radians(self._ROLL_LIM[1]))
        return [float(np.degrees(t1)), float(np.degrees(t2)), float(np.degrees(t3))]

    def calculate_right_arm_angles(self, xyz): return self._solve(xyz, "right")
    def calculate_left_arm_angles(self,  xyz): return self._solve(xyz, "left")


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

_HEAD_POINTS = [
    (1.0,  0.0,  0.6),
    (1.0,  0.5,  0.6),
    (1.0, -0.5,  0.6),
    (1.0,  0.0,  1.2),
    (1.0,  0.0,  0.0),
    (0.3,  0.3,  0.3),
    (5.0,  2.0,  0.6),   # yaw clamped
    (1.0,  0.0, -0.5),   # pitch clamped
]

_FK_CASES = [
    (0.0,   0.0,  1.0),
    (15.0, -5.0,  1.5),
    (-30.0, 10.0, 0.8),
    (60.0,  25.0, 2.0),
]

_PIXEL_CASES = [
    (320, 240, 1.0),
    (0,   0,   0.5),
    (848, 480, 2.0),
    (424, 240, 1.5),
]

_PIXEL_BASE_CASES = [
    (320, 240, 1.0,   0.0,  0.0),
    (200, 150, 1.5,  10.0, -5.0),
    (600, 300, 0.8, -20.0,  8.0),
    (424, 240, 2.0,  30.0, 15.0),
]

_ARM_POINTS = [
    (1.0, -0.2, 0.6),
    (1.0,  0.2, 0.6),
    (0.5, -0.5, 0.4),
    (0.5,  0.5, 0.4),
    (0.3, -0.1, 0.5),
    (0.3,  0.1, 0.5),
    (2.0, -1.0, 0.6),   # out of reach — clamped
    (2.0,  1.0, 0.6),   # out of reach — clamped
]

_TOL = 1e-9


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHeadSolver(unittest.TestCase):

    def setUp(self):
        self.head    = HeadSolver()
        self.np_head = _NpHeadSolver()

    def test_calculate_head_angles(self):
        for xyz in _HEAD_POINTS:
            with self.subTest(xyz=xyz):
                got = self.head.calculate_head_angles(xyz)
                ref = self.np_head.calculate_head_angles(xyz)
                self.assertAlmostEqual(got[0], ref[0], delta=_TOL)
                self.assertAlmostEqual(got[1], ref[1], delta=_TOL)

    def test_calculate_xyz(self):
        for yaw, pitch, depth in _FK_CASES:
            with self.subTest(yaw=yaw, pitch=pitch, depth=depth):
                got = self.head.calculate_xyz(yaw, pitch, depth)
                ref = self.np_head.calculate_xyz(yaw, pitch, depth)
                for g, r in zip(got, ref):
                    self.assertAlmostEqual(g, r, delta=_TOL)

    def test_pixel_to_camera(self):
        for u, v, depth in _PIXEL_CASES:
            with self.subTest(u=u, v=v, depth=depth):
                got = self.head.pixel_to_camera(u, v, depth)
                ref = self.np_head.pixel_to_camera(u, v, depth)
                for g, r in zip(got, ref):
                    self.assertAlmostEqual(g, r, delta=_TOL)

    def test_pixel_to_base(self):
        for u, v, depth, yaw, pitch in _PIXEL_BASE_CASES:
            with self.subTest(u=u, v=v, depth=depth, yaw=yaw, pitch=pitch):
                got = self.head.pixel_to_base([u, v], depth, yaw, pitch)
                ref = self.np_head.pixel_to_base([u, v], depth, yaw, pitch)
                for g, r in zip(got, ref):
                    self.assertAlmostEqual(g, r, delta=_TOL)


class TestArmsSolver(unittest.TestCase):

    def setUp(self):
        self.arms    = ArmsSolver()
        self.np_arms = _NpArmsSolver()

    def test_right_arm(self):
        for xyz in _ARM_POINTS:
            with self.subTest(xyz=xyz):
                got = self.arms.calculate_right_arm_angles(xyz)
                ref = self.np_arms.calculate_right_arm_angles(xyz)
                for g, r in zip(got, ref):
                    self.assertAlmostEqual(g, r, delta=_TOL)

    def test_left_arm(self):
        for xyz in _ARM_POINTS:
            with self.subTest(xyz=xyz):
                got = self.arms.calculate_left_arm_angles(xyz)
                ref = self.np_arms.calculate_left_arm_angles(xyz)
                for g, r in zip(got, ref):
                    self.assertAlmostEqual(g, r, delta=_TOL)


if __name__ == "__main__":
    unittest.main()
