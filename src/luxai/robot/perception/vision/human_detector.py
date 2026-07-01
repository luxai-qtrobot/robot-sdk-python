"""
HumanDetectorNode — reads /persons from qtrobot-yolo-driver, enriches each
frame with face orientation (yaw/pitch), 3-D position in robot base frame (xyz),
optional voice activity detection, and engagement score, then publishes on
/human/presence.
"""
from __future__ import annotations

import math
import threading
from typing import Optional

from luxai.magpie.frames import DictFrame
from luxai.magpie.nodes import ServerNode
from luxai.magpie.transport import RpcResponder, ZmqStreamReader, ZmqStreamWriter
from luxai.magpie.utils import Logger

from luxai.robot.kinematics.head_solver import HeadSolver

PERSONS_TOPIC  = "/persons"
PRESENCE_TOPIC = "/human/presence"

_CONF_THRESH = 0.3   # minimum keypoint confidence to trust


def _kp(kps: dict, name: str):
    k = kps.get(name)
    return k if (k and k.get("conf", 0.0) > _CONF_THRESH) else None


def _uv(kps: dict, name: str):
    k = _kp(kps, name)
    return k["uv"] if k else None


def _estimate_face_angles(kps: dict):
    """
    Estimate (yaw_deg, pitch_deg) from COCO-17 keypoints.
    Yaw  > 0: face turned to the robot's right.
    Pitch > 0: face tilted upward.
    Returns (None, None) when there are not enough reliable keypoints.

    Coordinate convention:
      COCO 'left_*' = person's anatomical left = camera's RIGHT when the
      person faces the camera.  So left_ear.u > right_ear.u in a frontal view.
    """
    nose  = _uv(kps, "nose")
    l_ear = _uv(kps, "left_ear")
    r_ear = _uv(kps, "right_ear")
    l_sh  = _uv(kps, "left_shoulder")
    r_sh  = _uv(kps, "right_shoulder")

    if nose is None:
        return None, None

    sh_w = abs(l_sh[0] - r_sh[0]) if (l_sh and r_sh) else 0.0

    # Yaw: deviation of nose from the midpoint between the two ears.
    yaw = 0.0
    if l_ear and r_ear:
        ear_mid = (l_ear[0] + r_ear[0]) / 2.0
        ref = sh_w * 0.35 if sh_w > 20 else max(abs(l_ear[0] - r_ear[0]), 5.0)
        yaw = math.degrees(math.atan2(nose[0] - ear_mid, ref))
    elif l_ear and not r_ear:
        yaw = 45.0    # only person's left ear visible → face turned right
    elif r_ear and not l_ear:
        yaw = -45.0   # only person's right ear visible → face turned left

    # Pitch: nose height relative to expected face height above shoulder midpoint.
    pitch = 0.0
    if l_sh and r_sh and sh_w > 20:
        sh_mid_v   = (l_sh[1] + r_sh[1]) / 2.0
        face_h     = sh_mid_v - nose[1]    # +ve: nose is above shoulders
        ref_face_h = sh_w * 0.8
        if face_h > 10:
            pitch = math.degrees(math.atan2(face_h - ref_face_h, ref_face_h)) * 0.5

    return round(yaw, 1), round(pitch, 1)


_DEPTH_KP_PRIORITY = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_hip", "right_hip",
]

_EMA_ALPHA    = 0.3
_MAX_DIST_M   = 4.0
_IMG_WIDTH_PX = 640


def _engagement(kps_out: dict, speaking: bool = False) -> float:
    """
    kps_out: enriched keypoints dict — each entry has {uv, conf, depth, xyz}.

    VAD disabled: 0.60 × facing + 0.40 × proximity
    VAD enabled:  0.50 × facing + 0.30 × proximity + 0.20 × speaking
    """
    def _u(name):
        k = kps_out.get(name)
        return k["uv"] if (k and k.get("conf", 0.0) >= _CONF_THRESH and k.get("uv")) else None

    ns = _u("nose")
    le = _u("left_eye")
    re = _u("right_eye")

    if ns and le and re:
        d_l = math.dist(ns, le)
        d_r = math.dist(ns, re)
        total = d_l + d_r
        asymmetry = abs(d_l - d_r) / total if total >= 1.0 else 1.0
        facing = (1.0 - asymmetry) ** 2
    else:
        facing = 0.0

    proximity = 0.0
    for name in _DEPTH_KP_PRIORITY:
        kp = kps_out.get(name)
        if kp and kp.get("xyz") is not None:
            x, y, z  = kp["xyz"]
            proximity = max(0.0, 1.0 - math.sqrt(x*x + y*y + z*z) / _MAX_DIST_M)
            break
    else:
        if le and re:
            proximity = min(1.0, (math.dist(le, re) / _IMG_WIDTH_PX) / 0.10)

    if speaking is None:
        score = 0.60 * facing + 0.40 * proximity
    else:
        score = 0.50 * facing + 0.30 * proximity + 0.20 * float(speaking)
    return round(min(1.0, max(0.0, score)), 3)


class HumanDetectorNode(ServerNode):
    """
    Local SDK node: subscribes to /persons from qtrobot-yolo-driver, enriches
    each frame, and publishes the result on /human/presence.

    Lifecycle:
      1. enable_plugin_local("human-detector") creates the node and wires inproc
         endpoints.
      2. robot.perception.configure_human_detector(endpoint=...) connects the node
         to the running yolo driver and starts the reader loop.
    """

    def __init__(
        self,
        robot,
        responder: RpcResponder,
        stream_writer: ZmqStreamWriter,
        name: str = "human-detector",
    ) -> None:
        self._robot       = robot
        self._out_writer  = stream_writer
        self._head_solver = HeadSolver()

        # Cached head joint angles (degrees), updated via joint-state stream.
        self._joint_lock     = threading.Lock()
        self._head_yaw_deg   = 0.0
        self._head_pitch_deg = 0.0

        # Runtime configuration (set by /configure RPC).
        self._default_depth = 1.0
        self._use_vad       = False

        # /persons stream reader and background thread.
        self._persons_reader: Optional[ZmqStreamReader] = None
        self._reader_stop   = threading.Event()
        self._reader_thread: Optional[threading.Thread] = None

        # VAD state, written by audio callback and read by the reader loop.
        self._vad          = None
        self._vad_lock     = threading.Lock()
        self._vad_speaking = False

        # Per-track EMA smoothing for engagement score.
        self._ema: dict = {}

        try:
            robot.motor.stream.on_joints_state(self._on_joint_state)
        except Exception as e:
            Logger.warning(
                f"{name}: could not subscribe to joint states ({e}); "
                "xyz will assume head at 0° until motor stream becomes available"
            )

        super().__init__(
            name=name,
            responder=responder,
            handler=self._on_rpc_request,
        )

    # ------------------------------------------------------------------
    # Joint state callback
    # ------------------------------------------------------------------

    def _on_joint_state(self, frame) -> None:
        value   = frame.value if hasattr(frame, "value") else {}
        yaw_d   = value.get("HeadYaw",   {})
        pitch_d = value.get("HeadPitch", {})
        yaw     = yaw_d.get("position")   if isinstance(yaw_d,   dict) else None
        pitch   = pitch_d.get("position") if isinstance(pitch_d, dict) else None
        if yaw is not None and pitch is not None:
            with self._joint_lock:
                self._head_yaw_deg   = float(yaw)
                self._head_pitch_deg = float(pitch)

    # ------------------------------------------------------------------
    # RPC dispatcher
    # ------------------------------------------------------------------

    def _on_rpc_request(self, req: dict) -> dict:
        name = req.get("name", "")
        args = req.get("args", {}) or {}
        n    = self.name

        if name == "":
            return {"status": True, "response": self._sys_descriptor()}
        if name == f"/{n}/configure":
            ok = self._configure(args)
            return {"status": ok, "response": ok}

        return {"status": False, "response": f"unknown RPC: {name!r}"}

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def _configure(self, cfg: dict) -> bool:
        endpoint      = cfg.get("endpoint", "")
        node_id       = cfg.get("node_id", "qtrobot-yolo-driver")
        default_depth = float(cfg.get("default_depth", 1.0))
        use_vad       = bool(cfg.get("use_vad", False))
        vad_threshold = float(cfg.get("vad_threshold", 0.5))

        # Build a temporary ZmqTransport pointing at the yolo driver's RPC endpoint.
        # It handles both endpoint= and node_id= (Zeroconf), and resolves tcp://*:port
        # wildcards to real IPs automatically when creating the stream reader.
        try:
            from luxai.robot.core.transport.zmq_transport import ZmqTransport
            if endpoint:
                transport = ZmqTransport(endpoint=endpoint)
            else:
                transport = ZmqTransport(node_id=node_id)
        except Exception as e:
            Logger.error(f"{self.name}: failed to connect to yolo driver ({e})")
            return False

        # Call the sys descriptor RPC (name="") to discover the /persons stream endpoint.
        try:
            requester = transport.get_requester("qtrobot-yolo-driver", None)
            raw = requester.call({"name": "", "args": {}}, timeout=5.0)
            if not isinstance(raw, dict) or not raw.get("status"):
                raise RuntimeError(f"sys descriptor returned: {raw}")
            desc = raw.get("response") or {}
            persons_stream = desc.get("stream", {}).get(PERSONS_TOPIC, {})
            if not persons_stream:
                raise RuntimeError(f"no {PERSONS_TOPIC!r} stream in sys descriptor")
        except Exception as e:
            Logger.error(f"{self.name}: sys descriptor RPC failed: {e}")
            transport.close()
            return False

        # Resolve the stream endpoint: replace tcp://*:port with the real host.
        try:
            zmq_info   = persons_stream.get("transports", {}).get("zmq", {})
            stream_ep  = zmq_info.get("endpoint", "")
            if not stream_ep:
                raise RuntimeError("no zmq endpoint in /persons stream descriptor")
            if stream_ep.startswith("tcp://*:"):
                # Replace wildcard with the host from the user-provided endpoint.
                base_host  = (endpoint or transport._default_rpc_endpoint).split("://")[1].rsplit(":", 1)[0]
                stream_ep  = stream_ep.replace("tcp://*:", f"tcp://{base_host}:", 1)
        except Exception as e:
            Logger.error(f"{self.name}: failed to resolve /persons stream endpoint: {e}")
            transport.close()
            return False

        transport.close()  # only used for the RPC call; stream reader is self-contained

        self._default_depth = default_depth
        self._stop_reader_thread()
        if self._persons_reader is not None:
            self._persons_reader.close()
            self._persons_reader = None

        try:
            self._persons_reader = ZmqStreamReader(
                stream_ep, topic=PERSONS_TOPIC, queue_size=2, bind=False, delivery="latest"
            )
        except Exception as e:
            Logger.error(f"{self.name}: failed to open /persons stream at {stream_ep}: {e}")
            return False

        self._use_vad = use_vad
        if use_vad:
            self._setup_vad(vad_threshold)

        self._reader_stop.clear()
        self._reader_thread = threading.Thread(
            target=self._reader_loop, daemon=True, name=f"{self.name}-reader"
        )
        self._reader_thread.start()

        Logger.info(
            f"{self.name}: configured — node_id={node_id} endpoint={endpoint} "
            f"default_depth={default_depth} use_vad={use_vad}"
        )
        return True

    # ------------------------------------------------------------------
    # VAD
    # ------------------------------------------------------------------

    def _setup_vad(self, threshold: float) -> None:
        try:
            from luxai.robot.perception.asr.microphone_stream import SileroVAD
            self._vad = SileroVAD(threshold=threshold)
            self._robot.microphone.stream.on_int_audio_ch0(self._vad_audio_cb)
            Logger.info(f"{self.name}: Silero VAD enabled (threshold={threshold})")
        except Exception as e:
            Logger.warning(
                f"{self.name}: VAD not available ({e}); voice.speaking will always be False"
            )
            self._vad = None

    def _vad_audio_cb(self, frame) -> None:
        if self._vad is None:
            return
        try:
            data = frame.data if hasattr(frame, "data") else bytes(frame)
            self._vad.process(data)
            with self._vad_lock:
                self._vad_speaking = self._vad.triggered
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Reader loop
    # ------------------------------------------------------------------

    def _reader_loop(self) -> None:
        while not self._reader_stop.is_set():
            try:
                msg, _topic = self._persons_reader.read(timeout=1.0)
            except TimeoutError:
                continue
            except Exception as e:
                Logger.warning(f"{self.name}: /persons reader error: {e}")
                break

            if msg is None:
                continue

            frame = DictFrame.from_dict(msg) if isinstance(msg, dict) else msg
            if not isinstance(frame, DictFrame):
                continue

            try:
                enriched = self._enrich(frame.value or {})
                self._out_writer.write(DictFrame(value=enriched).to_dict(), PRESENCE_TOPIC)
            except Exception as e:
                Logger.warning(f"{self.name}: enrich error: {e}")

    # ------------------------------------------------------------------
    # Enrichment
    # ------------------------------------------------------------------

    def _enrich(self, raw: dict) -> dict:
        with self._joint_lock:
            head_yaw   = self._head_yaw_deg
            head_pitch = self._head_pitch_deg
        with self._vad_lock:
            speaking = self._vad_speaking

        # First pass: build per-person data without voice scores.
        per_person = {}
        for pid, person in (raw.get("persons") or {}).items():
            kps_raw = person.get("keypoints") or {}

            # Add xyz to every keypoint that has a valid depth reading.
            kps_out = {}
            for kname, kp in kps_raw.items():
                uv    = kp.get("uv")
                conf  = kp.get("conf", 0.0)
                depth = float(kp.get("depth", -1.0))
                xyz   = None
                if uv and len(uv) == 2 and depth > 0.0:
                    try:
                        xyz = [
                            round(v, 3)
                            for v in self._head_solver.pixel_to_base(
                                uv, depth, head_yaw, head_pitch
                            )
                        ]
                    except Exception:
                        pass
                kps_out[kname] = {"uv": uv, "conf": conf, "depth": depth, "xyz": xyz}

            face_yaw, face_pitch = _estimate_face_angles(kps_raw)

            per_person[pid] = {
                "bbox":       person.get("bbox"),
                "confidence": person.get("confidence"),
                "keypoints":  kps_out,
                "face_yaw":   face_yaw,
                "face_pitch": face_pitch,
                "engagement": _engagement(kps_out, speaking=speaking if self._use_vad else None),
            }

        # Second pass: compute per-person voice scores if VAD is enabled.
        voice_scores: dict = {}
        if self._use_vad and per_person:
            if speaking:
                weights = {}
                for pid, pd in per_person.items():
                    yaw     = pd["face_yaw"]
                    frontal = max(0.0, 1.0 - abs(yaw) / 60.0) if yaw is not None else 0.25
                    weights[pid] = pd["engagement"] * frontal
                total = sum(weights.values())
                for pid, w in weights.items():
                    voice_scores[pid] = round(w / total if total > 0 else 1.0 / len(weights), 3)
            else:
                voice_scores = {pid: 0.0 for pid in per_person}

        # Prune EMA state for tracks that disappeared.
        for gone in set(self._ema) - set(per_person):
            del self._ema[gone]

        # Build output entries with EMA-smoothed engagement.
        persons_out = {}
        for pid, pd in per_person.items():
            raw  = pd["engagement"]
            prev = self._ema.get(pid)
            smoothed = raw if prev is None else _EMA_ALPHA * raw + (1.0 - _EMA_ALPHA) * prev
            self._ema[pid] = smoothed

            entry: dict = {
                "bbox":       pd["bbox"],
                "confidence": pd["confidence"],
                "keypoints":  pd["keypoints"],
                "face":       {"yaw": pd["face_yaw"], "pitch": pd["face_pitch"]},
                "engagement": round(smoothed, 3),
            }
            if self._use_vad:
                entry["voice"] = {
                    "speaking": speaking,
                    "score":    voice_scores.get(pid, 0.0),
                }
            persons_out[pid] = entry

        return {"persons": persons_out}

    # ------------------------------------------------------------------
    # System descriptor (used by magpie infrastructure)
    # ------------------------------------------------------------------

    def _sys_descriptor(self) -> dict:
        n = self.name
        return {
            "name": n,
            "rpc": {
                f"/{n}/configure": {
                    "transports": {"zmq": {"endpoint": f"inproc://{n}-rpc"}}
                },
            },
            "stream": {
                PRESENCE_TOPIC: {
                    "transports": {
                        "zmq": {"endpoint": f"inproc://{n}-stream", "queue_size": 10}
                    }
                },
            },
        }

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _stop_reader_thread(self) -> None:
        if self._reader_thread is not None and self._reader_thread.is_alive():
            self._reader_stop.set()
            self._reader_thread.join(timeout=2.0)
        self._reader_stop.clear()
        self._reader_thread = None

    def terminate(self, timeout=None) -> None:
        self._stop_reader_thread()
        if self._persons_reader is not None:
            self._persons_reader.close()
            self._persons_reader = None
        super().terminate(timeout=timeout)
