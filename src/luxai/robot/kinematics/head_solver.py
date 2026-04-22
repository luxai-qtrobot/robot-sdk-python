import math


class HeadSolver:
    # Calibrated defaults for the QTrobot RealSense camera (848x480)
    _FX_DEFAULT      = 419.76220703125
    _FY_DEFAULT      = 419.3450927734375
    _PPX_DEFAULT     = 421.1879577636719
    _PPY_DEFAULT     = 247.27752685546875
    _CAM_OFFSET_Z    = 0.09   # camera 9 cm ahead of HeadPitch joint centre
    _CAMERA_HEIGHT   = 0.6    # camera height above robot base frame (metres)
    # Image centre for the 848x480 resolution
    _IMG_CX_DEFAULT  = 424
    _IMG_CY_DEFAULT  = 240

    # Head joint limits (degrees)
    _YAW_LIMIT   = (-60.0, 60.0)
    _PITCH_LIMIT = (-25.0, 25.0)

    def __init__(self):
        self.fx             = self._FX_DEFAULT
        self.fy             = self._FY_DEFAULT
        self.ppx            = self._PPX_DEFAULT
        self.ppy            = self._PPY_DEFAULT
        self.img_cx         = self._IMG_CX_DEFAULT
        self.img_cy         = self._IMG_CY_DEFAULT
        self.cam_offset_z   = self._CAM_OFFSET_Z
        self.camera_height  = self._CAMERA_HEIGHT

    def configure(self, fx=None, fy=None, ppx=None, ppy=None,
                  img_cx=None, img_cy=None, camera_height=None):
        if fx             is not None: self.fx            = fx
        if fy             is not None: self.fy            = fy
        if ppx            is not None: self.ppx           = ppx
        if ppy            is not None: self.ppy           = ppy
        if img_cx         is not None: self.img_cx        = img_cx
        if img_cy         is not None: self.img_cy        = img_cy
        if camera_height  is not None: self.camera_height = camera_height

    def calculate_head_angles(self, xyz):
        """IK: 3-D point in robot base frame → [head_yaw_deg, head_pitch_deg]."""
        x, y, z = xyz
        yaw   = math.atan2(y, x)
        d_xy  = math.sqrt(x**2 + y**2)
        pitch = math.atan2(self.camera_height - z, d_xy)
        yaw   = max(math.radians(self._YAW_LIMIT[0]),   min(math.radians(self._YAW_LIMIT[1]),   yaw))
        pitch = max(math.radians(self._PITCH_LIMIT[0]), min(math.radians(self._PITCH_LIMIT[1]), pitch))
        return [math.degrees(yaw), math.degrees(pitch)]

    def calculate_xyz(self, head_yaw_deg, head_pitch_deg, depth):
        """FK: joint angles + depth → 3-D point in robot base frame."""
        t1 = math.radians(head_yaw_deg)
        t2 = math.radians(head_pitch_deg)
        x  = depth * math.cos(t1)
        y  = depth * math.sin(t1)
        z  = self.camera_height - depth * math.sin(t2)
        return [x, y, z]

    def pixel_to_base(self, uv, depth, head_yaw_deg, head_pitch_deg):
        """Camera pixel + depth + current head angles → 3-D point in robot base frame."""
        xyz_cam  = self.pixel_to_camera(uv[0], uv[1], depth)
        xyz_base = self._camera_to_base(xyz_cam, head_yaw_deg, head_pitch_deg)
        # x is approximated by depth (forward distance) for head angle calculation
        return [depth, xyz_base[1], xyz_base[2]]

    def pixel_to_camera(self, u, v, depth):
        """Pixel (u, v) + depth → 3-D point in camera frame."""
        u = u + (self.ppx - self.img_cx)
        v = v + (self.ppy - self.img_cy)
        x_cam = (u - self.ppx) * depth / self.fx
        y_cam = (v - self.ppy) * depth / self.fy
        z_cam = depth + self.cam_offset_z
        return [x_cam, y_cam, z_cam]

    def _camera_to_base(self, xyz_camera, head_yaw_deg, head_pitch_deg):
        t1 = math.radians(head_yaw_deg)
        t2 = math.radians(head_pitch_deg)
        T  = self._transformation_matrix(t1, t2)
        x, y, z = xyz_camera
        # Apply 4x4 homogeneous transform to [x, y, z, 1]
        return [
            T[0][0]*x + T[0][1]*y + T[0][2]*z + T[0][3],
            T[1][0]*x + T[1][1]*y + T[1][2]*z + T[1][3],
            T[2][0]*x + T[2][1]*y + T[2][2]*z + T[2][3],
        ]

    def _transformation_matrix(self, theta1, theta2):
        # T01: translation along z by 0.34
        # T12: yaw rotation + translation along z by 0.1
        # T23: pitch rotation + translation
        # Returns T01 × T12 × T23 as a 4x4 list-of-lists

        c1 = math.cos(theta1); s1 = math.sin(theta1)
        c2 = math.cos(theta2); s2 = math.sin(theta2)

        # T01 × T12 (T01 is pure z-translation by 0.34, so only the last
        # column translation row changes: tz becomes 0.34 + 0.1 = 0.44)
        T02 = [
            [ c1,  0, -s1,    0],
            [ s1,  0,  c1,    0],
            [  0, -1,    0, 0.44],
            [  0,  0,    0,    1],
        ]

        T23 = [
            [ 0, -s2,  c2,  0.16 * s2],
            [ 0,  c2,  s2, -0.16 * c2],
            [-1,    0,   0,          0],
            [ 0,    0,   0,          1],
        ]

        return self._matmul4(T02, T23)

    @staticmethod
    def _matmul4(A, B):
        return [
            [sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)]
            for i in range(4)
        ]
