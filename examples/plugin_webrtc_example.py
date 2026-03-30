"""
plugin_webrtc_example.py

Shows how to enable and use remote plugins over WebRTC transport.

Each plugin gets its own independent WebRTC peer connection — with a dedicated
data channel and its own video/audio media tracks — so plugin streams never
conflict with the robot's streams.

When connected via Robot.connect_webrtc_mqtt() or connect_webrtc_zmq(), all
signaling parameters (broker, options, timeout) are inherited by the plugin
peer automatically. Override any of them to target a different gateway.

Requirements:
    pip install luxai-robot[webrtc]
    pip install luxai-robot[webrtc,mqtt]   # for MQTT-signaled variants
"""
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot
from luxai.robot import MqttOptions, MqttTlsOptions, WebRTCOptions, WebRTCTurnServer

BROKER        = "mqtt://10.231.0.2:1883"        # MQTT broker used for signaling
ROBOT_ID      = "QTRD000320"                    # change to your robot serial
PLUGIN_NODE   = "qtrobot-realsense-driver"      # plugin's ZMQ node_id


# ── Option 1 ──────────────────────────────────────────────────────────────────
# Enable a plugin over WebRTC — inherits the robot's signaling broker and
# options automatically. Each peer is independent: separate data channel,
# separate media tracks.
def plugin_inherit_signaling():
    robot = Robot.connect_webrtc_mqtt(BROKER, ROBOT_ID)
    Logger.info(f"[inherit signaling] connected to {robot.robot_id} ({robot.robot_type})")

    # No broker_url needed — reuses the robot's signaling setup
    robot.enable_plugin_webrtc_mqtt("realsense-driver", node_id=PLUGIN_NODE)

    intrinsics = robot.camera.get_color_intrinsics()
    Logger.info(f"Color intrinsics: {intrinsics}")

    scale = robot.camera.get_depth_scale()
    Logger.info(f"Depth scale: {scale} m/unit")

    robot.close()


# ── Option 2 ──────────────────────────────────────────────────────────────────
# Enable a plugin, use it, then disable it cleanly.
# The robot connection (and its WebRTC peer) stay open.
def plugin_enable_disable():
    robot = Robot.connect_webrtc_mqtt(BROKER, ROBOT_ID)
    Logger.info(f"[enable/disable] connected to {robot.robot_id} ({robot.robot_type})")

    robot.tts.say_text("Enabling camera plugin over WebRTC.")

    robot.enable_plugin_webrtc_mqtt("realsense-driver", node_id=PLUGIN_NODE)

    intrinsics = robot.camera.get_color_intrinsics()
    Logger.info(f"Color intrinsics: {intrinsics}")

    robot.disable_plugin("realsense-driver")
    Logger.info("Plugin peer closed — robot peer still connected.")

    robot.tts.say_text("Camera plugin disabled.")
    robot.close()


# ── Option 3 ──────────────────────────────────────────────────────────────────
# Read a single video frame from the plugin's dedicated WebRTC media track.
def plugin_stream():
    robot = Robot.connect_webrtc_mqtt(BROKER, ROBOT_ID)
    Logger.info(f"[stream] connected to {robot.robot_id} ({robot.robot_type})")

    robot.enable_plugin_webrtc_mqtt("realsense-driver", node_id=PLUGIN_NODE)

    reader = robot.camera.stream.open_color_reader()
    frame = reader.read(timeout=5.0)
    if frame is not None:
        Logger.info(f"Color frame: shape={frame.value.shape}")
    else:
        Logger.warning("No frame received within timeout.")

    robot.close()


# ── Option 4 ──────────────────────────────────────────────────────────────────
# Plugin signaled via a different broker — useful when the plugin is on a
# separate gateway or a different network than the robot.
def plugin_different_broker():
    robot = Robot.connect_webrtc_mqtt(BROKER, ROBOT_ID)
    Logger.info(f"[different broker] connected to {robot.robot_id} ({robot.robot_type})")

    robot.enable_plugin_webrtc_mqtt(
        "realsense-driver",
        node_id=PLUGIN_NODE,
        broker_url="mqtt://192.168.2.100:1883",   # separate gateway/broker
    )

    intrinsics = robot.camera.get_color_intrinsics()
    Logger.info(f"Color intrinsics: {intrinsics}")

    robot.close()


# ── Option 5 ──────────────────────────────────────────────────────────────────
# Full mTLS signaling + STUN/TURN for NAT traversal.
# Both the robot peer and the plugin peer use the same security configuration,
# inherited automatically from the robot connection.
def plugin_mtls_with_turn():
    robot = Robot.connect_webrtc_mqtt(
        "mqtts://10.231.0.2:8883",
        ROBOT_ID,
        mqtt_options=MqttOptions(
            tls=MqttTlsOptions(
                ca_file="/path/to/ca.crt",
                cert_file="/path/to/client.crt",
                key_file="/path/to/client.key",
            ),
        ),
        webrtc_options=WebRTCOptions(
            stun_servers=["stun:stun.l.google.com:19302"],
            turn_servers=[
                WebRTCTurnServer(
                    url="turn:turn.example.com:3478",
                    username="user",
                    credential="pass",
                )
            ],
        ),
    )
    Logger.info(f"[mtls+turn] connected to {robot.robot_id} ({robot.robot_type})")

    # Plugin peer inherits mTLS + STUN/TURN — no extra config needed
    robot.enable_plugin_webrtc_mqtt("realsense-driver", node_id=PLUGIN_NODE)

    intrinsics = robot.camera.get_color_intrinsics()
    Logger.info(f"Color intrinsics: {intrinsics}")

    robot.close()


# ── Option 6 ──────────────────────────────────────────────────────────────────
# Broker-less WebRTC using ZMQ signaling (LAN only, no MQTT needed).
# Plugin peer inherits the ZMQ signaling endpoint automatically.
def plugin_webrtc_zmq():
    robot = Robot.connect_webrtc_zmq("tcp://192.168.3.152:5555", ROBOT_ID)
    Logger.info(f"[zmq signaling] connected to {robot.robot_id} ({robot.robot_type})")

    # Inherits ZMQ endpoint from the robot connection
    robot.enable_plugin_webrtc_zmq("realsense-driver", node_id=PLUGIN_NODE)

    intrinsics = robot.camera.get_color_intrinsics()
    Logger.info(f"Color intrinsics: {intrinsics}")

    robot.close()


# ── Option 7 ──────────────────────────────────────────────────────────────────
# Use Robot as a context manager — all peers (robot + plugins) are closed
# automatically on exit.
def plugin_context_manager():
    with Robot.connect_webrtc_mqtt(BROKER, ROBOT_ID) as robot:
        Logger.info(f"[context] connected to {robot.robot_id} ({robot.robot_type})")        
        robot.enable_plugin_webrtc_mqtt("realsense-driver", node_id=PLUGIN_NODE)
        intrinsics = robot.camera.get_color_intrinsics()
        Logger.info(f"Color intrinsics: {intrinsics}")
    # robot.close() — including all plugin peer teardown — is called automatically


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    try:
        plugin_inherit_signaling()
        # plugin_enable_disable()
        # plugin_stream()
        # plugin_different_broker()
        # plugin_mtls_with_turn()
        # plugin_webrtc_zmq()
        # plugin_context_manager()
    except ImportError as e:
        Logger.error(f"Missing dependency: {e}")
        Logger.error("Install WebRTC support with: pip install luxai-robot[webrtc]")
    except RuntimeError as e:
        Logger.error(f"Connection or plugin error: {e}")
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
