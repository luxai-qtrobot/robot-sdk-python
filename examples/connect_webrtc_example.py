"""
connect_webrtc_example.py

Shows the different ways to create a Robot client over WebRTC transport.

WebRTC provides a direct P2P connection between the operator and the robot.
Signaling (handshake) is exchanged through either an MQTT broker or a
broker-less ZMQ PAIR socket — after that, all traffic flows directly over
the WebRTC data channel (for RPC and generic streams) or native media tracks
(for video/audio streams).

Requirements:
    pip install luxai-robot[webrtc]
    pip install luxai-robot[webrtc,mqtt]   # for MQTT-signaled variants
"""
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot
from luxai.robot.core.transport import WebRTCTransport
from luxai.robot import (
    MqttOptions,
    MqttTlsOptions,
    MqttAuthOptions,
    WebRTCOptions,
    WebRTCTurnServer
)

BROKER_LOCAL  = "mqtt://10.231.0.2:1883"     # MQTT broker used for signaling
BROKER_PUBLIC = "mqtt://broker.hivemq.com:1883"
ROBOT_ID      = "QTRD000320"                  # change to your robot serial

BROKER = BROKER_LOCAL   # switch to BROKER_PUBLIC to signal over the internet


# ── Option 1 ──────────────────────────────────────────────────────────────────
# Basic WebRTC connection using MQTT signaling — no TLS, no authentication.
# The broker is only used for the handshake; all data flows P2P afterwards.
def connect_webrtc_mqtt_basic():
    Logger.set_level("DEBUG")
    
    robot = Robot.connect_webrtc_mqtt(BROKER, ROBOT_ID, webrtc_options=WebRTCOptions(stun_servers=[]))
    Logger.info(f"[webrtc/mqtt basic] connected to {robot.robot_id} ({robot.robot_type})")    
    robot.close()


# ── Option 2 ──────────────────────────────────────────────────────────────────
# MQTT signaling over TLS with server certificate verification.
def connect_webrtc_mqtt_tls():
    robot = Robot.connect_webrtc_mqtt(
        "mqtts://10.231.0.2:8883",
        ROBOT_ID,
        mqtt_options=MqttOptions(
            tls=MqttTlsOptions(ca_file="/path/to/ca.crt"),
        ),
    )
    Logger.info(f"[webrtc/mqtt tls] connected to {robot.robot_id} ({robot.robot_type})")
    robot.close()


# ── Option 3 ──────────────────────────────────────────────────────────────────
# MQTT signaling with mTLS + custom WebRTC STUN/TURN servers.
# Use TURN servers when both peers are behind symmetric NATs.
def connect_webrtc_mqtt_mtls_with_turn():
    robot = Robot.connect_webrtc_mqtt(
        "mqtts://10.231.0.2:8883",
        ROBOT_ID,
        mqtt_options=MqttOptions(
            tls=MqttTlsOptions(
                ca_file="/path/to/ca.crt",
                cert_file="/path/to/client.crt",
                key_file="/path/to/client.key",
            ),
            auth=MqttAuthOptions(mode="mtls"),
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
    Logger.info(f"[webrtc/mqtt mtls+turn] connected to {robot.robot_id} ({robot.robot_type})")
    robot.close()


# ── Option 4 ──────────────────────────────────────────────────────────────────
# WebRTC with automatic reconnect — the P2P connection re-establishes itself
# if it drops, without restarting the signaling process.
def connect_webrtc_mqtt_reconnect():
    robot = Robot.connect_webrtc_mqtt(
        BROKER,
        ROBOT_ID,
        reconnect=True,
        connect_timeout=20.0,
    )
    Logger.info(f"[webrtc/mqtt reconnect] connected to {robot.robot_id} ({robot.robot_type})")
    robot.close()


# ── Option 5 ──────────────────────────────────────────────────────────────────
# Broker-less WebRTC using ZMQ PAIR signaling (LAN only, no MQTT needed).
# The robot side must bind (bind=True); the operator side connects (bind=False).
#
# Robot side:
#   Robot.connect_webrtc_zmq("tcp://*:5555", ROBOT_ID, bind=True)
#
# Operator side (this script):
def connect_webrtc_zmq():
    robot = Robot.connect_webrtc_zmq(
        "tcp://192.168.3.152:5555",
        ROBOT_ID,
    )
    Logger.info(f"[webrtc/zmq] connected to {robot.robot_id} ({robot.robot_type})")
    robot.tts.say_text("Hello over broker-less WebRTC!")
    robot.close()


# ── Option 6 ──────────────────────────────────────────────────────────────────
# Power-user style: construct WebRTCConnection and WebRTCTransport manually,
# then pass the transport directly to Robot().
# Useful when you need direct control over the connection lifecycle.
def connect_manual_transport():
    from luxai.magpie.transport.webrtc import WebRTCConnection

    conn = WebRTCConnection.with_mqtt(
        BROKER_LOCAL,
        session_id=ROBOT_ID,
        reconnect=False,
        options=WebRTCOptions(stun_servers=["stun:stun.l.google.com:19302"]),
    )
    if not conn.connect(timeout=15.0):
        raise RuntimeError("WebRTC handshake timed out")

    transport = WebRTCTransport(conn)
    robot = Robot(transport=transport)
    Logger.info(f"[manual] connected to {robot.robot_id} ({robot.robot_type})")
    robot.close()


# ── Option 7 ──────────────────────────────────────────────────────────────────
# Use Robot as a context manager for automatic cleanup.
def connect_context_manager():
    with Robot.connect_webrtc_mqtt(BROKER, ROBOT_ID) as robot:
        Logger.info(f"[context] connected to {robot.robot_id} ({robot.robot_type})")
        robot.tts.say_text("Hello over WebRTC!")
    # robot.close() is called automatically on exit


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    try:
        connect_webrtc_mqtt_basic()
        # connect_webrtc_mqtt_tls()
        # connect_webrtc_mqtt_mtls_with_turn()
        # connect_webrtc_mqtt_reconnect()
        # connect_webrtc_zmq()
        # connect_manual_transport()
        # connect_context_manager()
    except ImportError as e:
        Logger.error(f"Missing dependency: {e}")
        Logger.error("Install WebRTC support with: pip install luxai-robot[webrtc]")
    except RuntimeError as e:
        Logger.error(f"Failed to connect: {e}")
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
