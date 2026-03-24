import time
import wave
from luxai.magpie.utils import Logger
from luxai.magpie.frames import AudioFrameRaw, DictFrame
from luxai.robot.core import Robot


def get_int_tuning(robot: Robot):
    # Read all readable Respeaker (internal mic array) tuning parameters
    params = robot.microphone.get_int_tuning()
    Logger.info("Internal mic tuning parameters:")
    for name, value in params.items():
        Logger.info(f"  {name}: {value}")


def set_int_tuning(robot: Robot):
    # Enable AGC (automatic gain control) on the internal mic array
    Logger.info("Setting AGCONOFF to 1 (AGC enabled)...")
    ok = robot.microphone.set_int_tuning(name="AGCONOFF", value=1.0)
    Logger.info(f"set_int_tuning result: {ok}")

    # Confirm the change was applied
    params = robot.microphone.get_int_tuning()
    Logger.info(f"AGCONOFF after set: {params.get('AGCONOFF')}")


def record_int_audio_ch0_to_wav(robot: Robot, duration_s: float = 5.0, output_path: str = "recording.wav"):
    # Open a reader for internal mic channel 0 (processed/ASR channel)
    Logger.info(f"Recording internal mic ch0 for {duration_s}s -> {output_path}")
    reader = robot.microphone.stream.open_int_audio_ch0_reader(queue_size=10)

    # Read the first frame to learn sample rate and bit depth
    first_frame: AudioFrameRaw = reader.read(timeout=3.0)
    if first_frame is None:
        Logger.error("No audio frame received!")
        return

    sample_rate = first_frame.sample_rate
    bit_depth = first_frame.bit_depth
    channels = first_frame.channels
    Logger.info(f"Audio format: {sample_rate} Hz, {bit_depth}-bit, {channels} channel(s)")

    deadline = time.monotonic() + duration_s
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(bit_depth // 8)
        wf.setframerate(sample_rate)

        # Write the first frame that was already read
        wf.writeframes(first_frame.data)

        while time.monotonic() < deadline:
            frame: AudioFrameRaw = reader.read(timeout=1.0)
            if frame :                
                wf.writeframes(frame.data)

    Logger.info(f"Recording saved to {output_path}")


def int_mic_events_callback(robot: Robot):
    # Subscribe to internal mic VAD + direction-of-arrival events via callback
    def on_event(frame: DictFrame):
        evt = frame.value
        activity = evt.get("activity", False)
        direction = evt.get("direction", 0)
        if activity:
            Logger.info(f"Voice detected — DOA: {direction}°")
        else:
            Logger.info("Silence")

    Logger.info("Subscribing to internal mic events (press Ctrl+C to stop)...")
    sub = robot.microphone.stream.on_int_event(on_event, queue_size=2)
    return sub


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by robot_id (serial number), e.g. "QTRD000123" or by endpoint (IP:port)
    # robot = Robot.connect_zmq(robot_id="QTRD000123")
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")
    Logger.info(f"Connected to {robot.robot_id} ({robot.robot_type}), SDK version: {robot.sdk_version}")

    int_mic_events_callback(robot)
    # get_int_tuning(robot)
    # set_int_tuning(robot)
    # record_int_audio_ch0_to_wav(robot, duration_s=5.0, output_path="recording.wav")
    

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
