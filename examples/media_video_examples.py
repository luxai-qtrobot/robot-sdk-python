import time
import numpy as np
from luxai.magpie.utils import Logger
from luxai.magpie.utils.common import get_uinque_id
from luxai.magpie.frames import ImageFrameRaw
from luxai.robot.core import Robot, wait_all_actions


def fg_video_alpha(robot: Robot):
    # Set FG video alpha to fully opaque and confirm
    Logger.info("Setting FG video alpha to 1.0 (fully opaque)...")
    robot.media.set_fg_video_alpha(1.0)

    # Reduce to half-transparent
    Logger.info("Setting FG video alpha to 0.5 (half transparent)...")
    robot.media.set_fg_video_alpha(0.5)
    time.sleep(2)

    # Restore to fully opaque
    Logger.info("Restoring FG video alpha to 1.0...")
    robot.media.set_fg_video_alpha(1.0)


def play_bg_video_file(robot: Robot):
    # This file should exist on the robot for the example to work
    video_file_on_robot = "/home/qtrobot/robot/data/emotions/QT/kiss.avi"

    # Play a video file on the BG lane and wait for it to finish
    Logger.info("Playing BG video file (blocking)...")
    ret = robot.media.play_bg_video_file(video_file_on_robot)
    Logger.info(f"Done. Result: {ret}")

    # Play a file non-blocking, then cancel it after 5 seconds
    Logger.info("Playing BG video file (non-blocking, will cancel after 2 seconds)...")
    h = robot.media.play_bg_video_file_async(video_file_on_robot)
    time.sleep(2)
    h.cancel()
    Logger.info("BG video file playback cancelled.")


def pause_resume_bg_video_file(robot: Robot):
    video_file_on_robot = "/home/qtrobot/robot/data/emotions/QT/kiss.avi"
    # Play a file, pause it, wait, then resume
    Logger.info("Playing BG video file...")
    play_handler = robot.media.play_bg_video_file_async(video_file_on_robot)
    time.sleep(2)

    Logger.info("Pausing BG video...")
    robot.media.pause_bg_video_file()
    Logger.info("Paused. Waiting 3 seconds...")
    time.sleep(3)

    Logger.info("Resuming BG video...")
    robot.media.resume_bg_video_file()
    Logger.info("Resumed.")
    play_handler.wait()  # Wait for playback to finish
    Logger.info("BG video file playback finished.")



def _make_heart_frame(width: int, height: int, scale = 1.5) -> ImageFrameRaw:
    import numpy as np

    # Create transparent RGBA image
    image = np.zeros((height, width, 4), dtype=np.uint8)

    # Coordinate grid normalized to [-1.5, 1.5]
    y, x = np.ogrid[:height, :width]
    x = (x - width / 2) / (width / 2)
    y = -((y - height / 2) / (height / 2))  # <-- flip vertically
    
    x *= scale
    y *= scale

    # Heart equation mask
    heart_mask = (x**2 + y**2 - 1)**3 - x**2 * y**3 <= 0

    # Fill heart (Red, full alpha)
    image[heart_mask] = (255, 0, 0, 255)  # RGBA

    # Convert to raw bytes
    return ImageFrameRaw(
        data=image.tobytes(),
        format="raw",
        width=width,
        height=height,
        channels=4,
        pixel_format="RGBA",
    )

def fg_video_stream(robot: Robot):
    import time, math

    stream_id = get_uinque_id()
    Logger.info(f"Starting FG video stream with ID: {stream_id}")

    fps = 30
    duration_s = 5.0
    total_frames = int(fps * duration_s)
    frame_interval = 1.0 / fps

    # Pre-build once
    heart_frame = _make_heart_frame(width=400, height=280, scale=5.0)
    heart_frame.gid = stream_id

    # Heartbeat speed
    bpm = 72.0
    freq = bpm / 60.0  # beats per second

    robot.media.set_fg_video_alpha(0.0)
    writer = robot.media.stream.open_fg_video_stream_writer()

    t0 = time.perf_counter()
    for frame_id in range(1, total_frames + 1):
        heart_frame.id = frame_id
        writer.write(heart_frame)

        t = time.perf_counter() - t0

        # Smooth heartbeat pulse (0 → 1 → 0)
        alpha = 0.5 * (1 + math.sin(2 * math.pi * freq * t))
        alpha = alpha ** 2  # makes it feel more like a "beat"
        robot.media.set_fg_video_alpha(alpha)
        time.sleep(frame_interval)

    robot.media.set_fg_video_alpha(1.0)
    robot.media.cancel_fg_video_stream()
    Logger.info("FG video stream cancelled.")


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by node_id (serial number), e.g. "QTRD000123" or by endpoint (IP:port)
    # robot = Robot.connect_zmq(node_id="QTRD000123")
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")
    Logger.info(f"Connected to {robot._robot_serial} ({robot._robot_type}), SDK version: {robot._sdk_version}")

    fg_video_stream(robot)
    # fg_video_alpha(robot)
    # play_bg_video_file(robot)
    # pause_resume_bg_video_file(robot)        

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
