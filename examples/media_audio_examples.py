import math
import struct
import time
from luxai.magpie.utils import Logger
from luxai.magpie.utils.common import get_uinque_id
from luxai.magpie.frames import AudioFrameRaw
from luxai.robot.core import Robot
from luxai.robot.core import Robot, wait_all_actions, wait_any_action

def fg_audio_volume(robot: Robot):
    # Set FG volume to 100% and confirm
    Logger.info("Setting FG audio volume to 1.0...")
    robot.media.set_fg_audio_volume(1.0)
    vol = robot.media.get_fg_audio_volume()
    Logger.info(f"FG audio volume after set: {vol:.2f}")


def bg_audio_volume(robot: Robot):
    # Set BG volume to 100% and confirm
    Logger.info("Setting BG audio volume to 1.0...")
    robot.media.set_bg_audio_volume(1.0)
    vol = robot.media.get_bg_audio_volume()
    Logger.info(f"BG audio volume after set: {vol:.2f}")


def play_fg_audio_file(robot: Robot):
    # This file should exist on the robot for the example to work
    audio_file_on_robot = "/home/qtrobot/robot/data/audios/QT/5LittleBunnies.wav"

    # Play an audio file on the FG lane and wait for it to finish
    Logger.info("Playing FG audio file (blocking)...")
    ret = robot.media.play_fg_audio_file(audio_file_on_robot)
    Logger.info(f"Done. Result: {ret}")

    # Play a file non-blocking, then cancel it after 2 seconds
    Logger.info("Playing FG audio file (non-blocking, will cancel after 5 seconds)...")
    h = robot.media.play_fg_audio_file_async(audio_file_on_robot)
    time.sleep(5)
    h.cancel()
    Logger.info("FG audio file playback cancelled.")


def pause_resume_fg_audio_file(robot: Robot):
    audio_file_on_robot = "/home/qtrobot/robot/data/audios/QT/5LittleBunnies.wav"
    # Play a file, pause it, wait, then resume
    Logger.info("Playing FG audio file...")
    play_handler = robot.media.play_fg_audio_file_async(audio_file_on_robot)
    time.sleep(10)

    Logger.info("Pausing FG audio...")
    robot.media.pause_fg_audio_file()
    Logger.info("Paused. Waiting 5 seconds...")
    time.sleep(5)

    Logger.info("Resuming FG audio...")
    robot.media.resume_fg_audio_file()
    Logger.info("Resumed.")
    play_handler.wait()  # Wait for playback to finish
    Logger.info("FG audio file playback finished.")

def play_fg_bg_audio_files(robot: Robot):
    bg_audio_file_on_robot = "/home/qtrobot/robot/data/audios/QT/5LittleBunnies.wav"
    fg_audio_file_on_robot = "/home/qtrobot/robot/data/audios/QT/John_Wesley_Tequila.mp3"

    # Lower BG volume to hear FG clearly
    robot.media.set_bg_audio_volume(0.7)
    robot.media.set_fg_audio_volume(1.0)

    # Play FG and BG files simultaneously, cancel both after 3 seconds
    Logger.info("Playing FG and BG audio files simultaneously...")

    h_bg = robot.media.play_bg_audio_file_async(bg_audio_file_on_robot)

    # start FG audio after a short delay to create overlap
    time.sleep(5)
    h_fg = robot.media.play_fg_audio_file_async(fg_audio_file_on_robot)

    # wiat for both to finishes
    wait_all_actions([h_bg, h_fg])
    Logger.info("Both lanes finished playing.")
    # reset BG volume
    robot.media.set_bg_audio_volume(1.0)


def play_fg_online_audio_file(robot: Robot):
    # Play an online audio file (must be a direct link to an audio file, not a webpage)
    # http://radio3.radio-calico.com:8080/calico
    online_audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    online_audio_stream_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
    Logger.info(f"Playing online audio file for 10 sec from URL: {online_audio_url}...")
    h = robot.media.play_fg_audio_file_async(online_audio_url)
    time.sleep(10)
    h.cancel()
    Logger.info("Online audio file playback cancelled.")


def play_fg_online_radio(robot: Robot):
    # Play an online audio file (must be a direct link to an audio file, not a webpage)
    # http://radio3.radio-calico.com:8080/calico
    online_radio_url = "http://radio3.radio-calico.com:8080/calico"
    Logger.info(f"Playing online radio file from URL: {online_radio_url}...")
    h = robot.media.play_fg_audio_file_async(online_radio_url)
    Logger.info("Press <enter> to stop the radio...")
    input()
    h.cancel()
    Logger.info(f"stopped online radio playback.")


def _make_sine_chunk(freq_hz: float, sample_rate: int, chunk_frames: int, phase: int) -> tuple[bytes, int]:
    amplitude = 32767  # max for signed 16-bit
    samples = [
        int(amplitude * math.sin(2 * math.pi * freq_hz * (phase + i) / sample_rate))
        for i in range(chunk_frames)
    ]
    return struct.pack(f"<{chunk_frames}h", *samples), phase + chunk_frames


def fg_audio_stream(robot: Robot):


    # Generate a unique ID for this stream
    stream_id = get_uinque_id()
    Logger.info(f"Starting FG audio stream with ID: {stream_id}")

    # Stream a 440 Hz sine wave tone to the FG lane for 3 seconds, then cancel
    sample_rate = 16000
    freq_hz = 440.0   # A4
    duration_s = 5.0
    chunk_frames = 1024
    total_frames = int(sample_rate * duration_s)

    Logger.info(f"Streaming {freq_hz} Hz tone to FG lane for {duration_s}s...")
    writer = robot.media.stream.open_fg_audio_stream_writer()

    phase = 0
    frame_id = 1
    while phase < total_frames:
        frames_this_chunk = min(chunk_frames, total_frames - phase)
        raw, phase = _make_sine_chunk(freq_hz, sample_rate, frames_this_chunk, phase)
        frame = AudioFrameRaw(
            channels=1,
            sample_rate=sample_rate,
            bit_depth=16,
            data=raw)
        frame.gid = stream_id  # set the group ID for this stream
        frame.id = frame_id    # set a frame ID (optional, for tracking)
        writer.write(frame)
        frame_id += 1
        time.sleep(frames_this_chunk / sample_rate / 1.5)  # pace the stream in real-time

    Logger.info("All frames sent....")


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by node_id (serial number), e.g. "QTRD000310" or by endpoint (IP:port)
    # robot = Robot.connect_zmq(node_id="QTRD000310")
    robot = Robot.connect_zmq(endpoint="tcp://192.168.3.215:50500")
    Logger.info(f"Connected to {robot._robot_serial} ({robot._robot_type}), SDK version: {robot._sdk_version}")

    fg_audio_volume(robot)
    # bg_audio_volume(robot)
    # play_fg_audio_file(robot)
    # pause_resume_fg_audio_file(robot)
    # play_fg_online_audio_file(robot)
    # play_fg_online_radio(robot)
    # play_fg_bg_audio_files(robot)
    # fg_audio_stream(robot)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
