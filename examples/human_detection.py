"""
Human detection example using the qtrobot-yolo-driver C++ service.

Prerequisites:
  - qtrobot-yolo-driver running and reachable (publishes /persons on port 50771)
  - robot motor service running (for head-angle-aware xyz projection)

The human-detector plugin is local (runs in-process). It connects to the
yolo driver's /persons stream, enriches each frame with face orientation,
3-D position in robot base frame (xyz), and an engagement score, then
republishes on the /human/presence stream.
"""

import time
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot


def on_presence(frame):
    persons = frame.value.get("persons", {})
    if not persons:
        return

    for pid, p in persons.items():
        face  = p.get("face") or {}
        kps   = p.get("keypoints", {})
        voice = p.get("voice")

        nose      = kps.get("nose") or {}
        nose_depth = nose.get("depth", -1.0)
        nose_xyz   = nose.get("xyz")
        Logger.info(
            f"  person {pid}: "
            f"conf={p.get('confidence', 0):.2f}  "
            f"face yaw={face.get('yaw')}° pitch={face.get('pitch')}°  "
            f"nose depth={nose_depth:.2f}m  "
            f"nose xyz={nose_xyz}  "
            f"engagement={p.get('engagement', 0):.2f}"
            + (f"  voice speaking={voice['speaking']} score={voice['score']:.2f}" if voice else "")
        )


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # Connect to the robot by serial number or direct endpoint
    # robot = Robot.connect_zmq(robot_id="QTRD000123")
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.1:50500")
    Logger.info(f"Connected to {robot.robot_id} ({robot.robot_type}), SDK version: {robot.sdk_version}")

    # Enable the human detector plugin (runs locally in this process)
    robot.enable_plugin_local("human-detector")

    # Connect the plugin to the running yolo driver.
    # Pass the yolo driver's RPC endpoint — the stream port is discovered automatically.
    ok = robot.perception.configure_human_detector(
        endpoint="tcp://10.231.0.1:50770",  # yolo driver RPC port 
        default_depth=1.0,   # fallback depth (m) when a keypoint has no valid depth
        use_vad=False,       # set True to add voice.speaking field (requires torch)
    )
    if not ok:
        Logger.error("Failed to configure human detector. Check that qtrobot-yolo-driver is running.")
        robot.close()
        raise SystemExit(1)

    # Subscribe to enriched presence frames
    robot.perception.stream.on_human_presence(on_presence)
    Logger.info("Listening for human presence. Press Ctrl+C to stop.")

    # --- Example: look at the closest person using the kinematics plugin ---
    # robot.enable_plugin_local("kinematics")
    # def on_presence_look(frame):
    #     persons = frame.value.get("persons", {})
    #     if not persons:
    #         return
    #     # Pick person with highest engagement
    #     best = max(persons.values(), key=lambda p: p.get("engagement", 0))
    #     xyz = best.get("xyz")
    #     if xyz:
    #         robot.kinematics.look_at_point(*xyz, only_gaze=False)
    # robot.perception.stream.on_human_presence(on_presence_look)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
