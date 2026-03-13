import time
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot


def list_engines(robot: Robot):
    # List all loaded/available TTS engine ids
    engines = robot.tts.list_engines()
    Logger.info(f"Available TTS engines: {engines}")    

def get_set_default_engine(robot: Robot):
    # Get the current default engine
    engine = robot.tts.get_default_engine()
    Logger.info(f"Current default TTS engine: {engine}")

    # Switch the default engine to 'acapela'
    Logger.info("Setting default TTS engine to 'acapela'...")
    robot.tts.set_default_engine("acapela")


def say_text(robot: Robot):
    # Say a simple phrase using the acapela engine
    Logger.info("Saying text with acapela engine...")
    ret = robot.tts.say_text("acapela", "Hello, This is spoken with the default settings.")
    Logger.info(f"Return {ret}")

    # Say text with rate and pitch adjustments
    Logger.info("Saying text with rate and pitch adjustments...")
    robot.tts.say_text("acapela", "This is spoken slower at a higher pitch.", rate=0.85, pitch=1.2)

    # Say text with explicit language and voice parameters
    Logger.info("Saying text with voice override...")
    robot.tts.say_text("acapela", "This is spoken with the Rosie voice.", voice="Rosie")

    # Say text with inline SSML tags to adjust speed mid-utterance
    robot.tts.say_text("acapela", "I will speak with different speed.  \\rspd=130\\ for example now I'm speaking faster. \\rspd=70\\ And now I'm speaking slower.")


def say_text_cancel(robot: Robot):
    # Start a long utterance in non-blocking mode and cancel it after 2 seconds
    Logger.info("Starting speech (will cancel after 2 seconds)...")
    h = robot.tts.say_text_async("acapela", "This is a very long sentence. That will be interrupted before it finishes after one second.")
    time.sleep(2)
    h.cancel()
    Logger.info("Speech cancelled.")


def say_ssml_azure(robot: Robot):
    # Say SSML markup using the azure engine
    ssml = (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">'
        '    <voice name="en-US-MultiTalker-Ava-Andrew:DragonHDLatestNeural">'
        '        <mstts:dialog>'
        '            <mstts:turn speaker="ava">Hello, Andrew! How is s your day going?</mstts:turn>'
        '            <mstts:turn speaker="andrew">Hey Ava! It is been great, just exploring some new features in QTrobort.</mstts:turn>'
        '            <mstts:turn speaker="ava">That sounds interesting! I believe we are re both working on exciting projects.</mstts:turn>'
        '        </mstts:dialog>'
        '    </voice>'
        '</speak>'
    )
    Logger.info("Saying SSML with azure engine...")
    ret = robot.tts.say_ssml("azure", ssml)
    Logger.info(f"Return {ret}")


def check_ssml_support(robot: Robot):
    # Check whether each engine supports SSML
    engines = robot.tts.list_engines()
    for engine in engines:
        supported = robot.tts.supports_ssml(engine)
        Logger.info(f"  {engine}: SSML supported = {supported}")


def get_languages_and_voices(robot: Robot):
    # List supported languages for the acapela engine
    langs = robot.tts.get_languages("acapela")
    Logger.info(f"acapela languages: {langs}")

    # List available voices for the acapela engine
    voices = robot.tts.get_voices("acapela")
    Logger.info(f"acapela voices ({len(voices)}):")
    for v in voices:
        Logger.info(f"  {v}")


def engine_config(robot: Robot):
    # Read the current config for the acapela engine
    cfg = robot.tts.get_config("acapela")
    Logger.info(f"acapela config: {cfg}")

    # Update the acapela engine with a subscription key and region
    Logger.info("Configuring acapela engine with pitch and rate adjustments...")
    robot.tts.set_config("acapela", {"pitch": 1.0, "rate": 0.8})
    Logger.info("Config updated.")


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    # connect robot by node_id (serial number), e.g. "QTRD000123" or by endpoint (IP:port)
    # robot = Robot.connect_zmq(node_id="QTRD000123")
    robot = Robot.connect_zmq(endpoint="tcp://192.168.3.215:50500")
    Logger.info(f"Connected to {robot._robot_serial} ({robot._robot_type}), SDK version: {robot._sdk_version}")

    list_engines(robot)
    get_languages_and_voices(robot)
    # engine_config(robot)
    # get_set_default_engine(robot)
    # say_text(robot)
    # say_text_cancel(robot)
    # check_ssml_support(robot)
    # say_ssml_azure(robot)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
    finally:
        robot.close()
