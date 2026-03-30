"""
plugin_mqtt_example.py

Shows how to enable and use remote plugins over MQTT transport.

The robot and its plugins must be running qtrobot-service-hub-gateway-mqtt,
which bridges ZMQ services — including plugin services — to an MQTT broker.
Each plugin's node_id becomes its MQTT topic namespace.

When connected via Robot.connect_mqtt(), the broker connection is shared
with plugin transports automatically — no extra configuration needed.

Requirements:
    pip install luxai-robot[mqtt]
"""
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot

BROKER        = "mqtt://10.231.0.2:1883"        # robot's MQTT broker
ROBOT_ID      = "QTRD000320"                    # change to your robot serial
PLUGIN_NODE   = "qtrobot-realsense-driver"      # plugin's ZMQ node_id


# ── Option 1 ──────────────────────────────────────────────────────────────────
# Enable a plugin over MQTT — reuses the robot's existing broker connection.
# This is the simplest and most common case: robot and plugin share the same
# gateway and broker.
def plugin_shared_broker():
    robot = Robot.connect_mqtt(BROKER, ROBOT_ID)
    Logger.info(f"[shared broker] connected to {robot.robot_id} ({robot.robot_type})")

    robot.enable_plugin_mqtt("realsense-driver", node_id=PLUGIN_NODE)

    intrinsics = robot.camera.get_color_intrinsics()
    Logger.info(f"Color intrinsics: {intrinsics}")

    scale = robot.camera.get_depth_scale()
    Logger.info(f"Depth scale: {scale} m/unit")

    robot.close()


# ── Option 2 ──────────────────────────────────────────────────────────────────
# Enable a plugin, use it, then disable it — freeing its resources while the
# main robot connection stays open.
def plugin_enable_disable():
    robot = Robot.connect_mqtt(BROKER, ROBOT_ID)
    Logger.info(f"[enable/disable] connected to {robot.robot_id} ({robot.robot_type})")

    robot.tts.say_text("Enabling camera plugin.")

    robot.enable_plugin_mqtt("realsense-driver", node_id=PLUGIN_NODE)

    intrinsics = robot.camera.get_color_intrinsics()
    Logger.info(f"Color intrinsics: {intrinsics}")

    robot.disable_plugin("realsense-driver")
    Logger.info("Plugin disabled — broker connection still open.")

    robot.tts.say_text("Camera plugin disabled.")
    robot.close()


# ── Option 3 ──────────────────────────────────────────────────────────────────
# Read a single camera frame via MQTT stream.
def plugin_stream():
    robot = Robot.connect_mqtt(BROKER, ROBOT_ID)
    Logger.info(f"[stream] connected to {robot.robot_id} ({robot.robot_type})")

    robot.enable_plugin_mqtt("realsense-driver", node_id=PLUGIN_NODE)

    reader = robot.camera.stream.open_color_reader()
    frame = reader.read(timeout=5.0)
    if frame is not None:
        Logger.info(f"Color frame: shape={frame.value.shape}")
    else:
        Logger.warning("No frame received within timeout.")

    robot.close()


# ── Option 4 ──────────────────────────────────────────────────────────────────
# Plugin on a different broker than the robot — useful when the plugin is
# managed by a separate gateway or a different network segment.
def plugin_different_broker():
    robot = Robot.connect_mqtt(BROKER, ROBOT_ID)
    Logger.info(f"[different broker] connected to {robot.robot_id} ({robot.robot_type})")

    robot.enable_plugin_mqtt(
        "realsense-driver",
        node_id=PLUGIN_NODE,
        broker_url="mqtt://192.168.2.100:1883",   # separate gateway/broker
    )

    intrinsics = robot.camera.get_color_intrinsics()
    Logger.info(f"Color intrinsics: {intrinsics}")

    robot.close()


# ── Option 5 ──────────────────────────────────────────────────────────────────
# Use Robot as a context manager — robot.close() (and plugin cleanup) happen
# automatically on exit.
def plugin_context_manager():
    with Robot.connect_mqtt(BROKER, ROBOT_ID) as robot:
        Logger.info(f"[context] connected to {robot.robot_id} ({robot.robot_type})")

        robot.enable_plugin_mqtt("realsense-driver", node_id=PLUGIN_NODE)
        intrinsics = robot.camera.get_color_intrinsics()
        Logger.info(f"Color intrinsics: {intrinsics}")
    # robot.close() — including all plugin teardown — is called automatically


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    try:
        plugin_shared_broker()
        # plugin_enable_disable()
        # plugin_stream()
        # plugin_different_broker()
        # plugin_context_manager()
    except ImportError as e:
        Logger.error(f"Missing dependency: {e}")
        Logger.error("Install MQTT support with: pip install luxai-robot[mqtt]")
    except RuntimeError as e:
        Logger.error(f"Connection or plugin error: {e}")
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
