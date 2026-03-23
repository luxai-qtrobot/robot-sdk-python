"""
connect_mqtt_example.py

Shows the different ways to create a Robot client over MQTT transport.

The robot must be running qtrobot-service-hub-gateway-mqtt, which bridges
the robot's ZMQ services to an MQTT broker.

Requirements:
    pip install luxai-robot[mqtt]
"""
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot
from luxai.robot.core.transport import MqttTransport
from luxai.robot import (
    MqttOptions,
    MqttTlsOptions,
    MqttAuthOptions,
    MqttSessionOptions,
    MqttReconnectOptions,
)

BROKER_LOCAL  = "mqtt://10.231.0.2:1883"              # robot's onboard/local broker
BROKER_PUBLIC = "mqtt://broker.hivemq.com:1883"      # public HiveMQ broker (no auth)
ROBOT_ID      = "QTRD000320"                         # change to your robot serial

BROKER = BROKER_LOCAL   # switch to BROKER_PUBLIC to test over the internet


# ── Option 1 ──────────────────────────────────────────────────────────────────
# Basic plain-TCP connection — no TLS, no authentication.
def connect_basic():
    robot = Robot.connect_mqtt(BROKER, ROBOT_ID)
    Logger.info(f"[basic] connected to {robot._robot_id} ({robot._robot_type})")
    robot.close()


# ── Option 2 ──────────────────────────────────────────────────────────────────
# Username/password authentication over plain TCP.
def connect_with_username_password():
    options = MqttOptions(
        auth=MqttAuthOptions(
            mode="username_password",
            username="myuser",
            password="mypassword",
        )
    )
    robot = Robot.connect_mqtt(BROKER, ROBOT_ID, options=options)
    Logger.info(f"[user/pass] connected to {robot._robot_id} ({robot._robot_type})")
    robot.close()


# ── Option 3 ──────────────────────────────────────────────────────────────────
# TLS with server certificate verification (one-way TLS).
# Use mqtts:// for TLS over TCP or wss:// for TLS over WebSocket.
def connect_with_tls():
    options = MqttOptions(
        tls=MqttTlsOptions(
            ca_file="/path/to/ca.crt",      # broker's CA certificate
        )
    )
    robot = Robot.connect_mqtt("mqtts://10.231.0.2:8883", ROBOT_ID, options=options)
    Logger.info(f"[tls] connected to {robot._robot_id} ({robot._robot_type})")
    robot.close()


# ── Option 4 ──────────────────────────────────────────────────────────────────
# Mutual TLS (mTLS): client presents its own certificate to the broker.
# Strongest authentication — no username/password needed.
def connect_with_mtls():
    options = MqttOptions(
        tls=MqttTlsOptions(
            ca_file="/path/to/ca.crt",          # broker's CA certificate
            cert_file="/path/to/client.crt",    # client certificate
            key_file="/path/to/client.key",     # client private key
        ),
        auth=MqttAuthOptions(mode="mtls"),
    )
    robot = Robot.connect_mqtt("mqtts://10.231.0.2:8883", ROBOT_ID, options=options)
    Logger.info(f"[mtls] connected to {robot._robot_id} ({robot._robot_type})")
    robot.close()


# ── Option 5 ──────────────────────────────────────────────────────────────────
# TLS over WebSocket — useful when connecting through a web proxy or firewall
# that only allows HTTP/HTTPS traffic.
def connect_websocket_tls():
    options = MqttOptions(
        tls=MqttTlsOptions(ca_file="/path/to/ca.crt"),
        auth=MqttAuthOptions(
            mode="username_password",
            username="myuser",
            password="mypassword",
        ),
    )
    robot = Robot.connect_mqtt("wss://broker.example.com:8884/mqtt", ROBOT_ID, options=options)
    Logger.info(f"[wss] connected to {robot._robot_id} ({robot._robot_type})")
    robot.close()


# ── Option 6 ──────────────────────────────────────────────────────────────────
# Full options: TLS + auth + persistent session + custom reconnect backoff.
def connect_full_options():
    options = MqttOptions(
        tls=MqttTlsOptions(
            ca_file="/path/to/ca.crt",
            cert_file="/path/to/client.crt",
            key_file="/path/to/client.key",
        ),
        auth=MqttAuthOptions(mode="mtls"),
        session=MqttSessionOptions(
            clean_start=False,          # resume persistent session on reconnect
            session_expiry_sec=3600,    # keep session alive for 1 hour
        ),
        reconnect=MqttReconnectOptions(
            enabled=True,
            min_delay_sec=1.0,
            max_delay_sec=60.0,
        ),
    )
    robot = Robot.connect_mqtt(
        "mqtts://10.231.0.2:8883",
        ROBOT_ID,
        options=options,
        connect_timeout=15.0,
        default_rpc_timeout=30.0,
    )
    Logger.info(f"[full] connected to {robot._robot_id} ({robot._robot_type})")
    robot.close()


# ── Option 7 ──────────────────────────────────────────────────────────────────
# Power-user style: construct MqttConnection and MqttTransport manually,
# then pass the transport directly to Robot().
# Useful when you need direct control over the connection lifecycle.
def connect_manual_transport():
    from luxai.magpie.transport.mqtt import MqttConnection

    conn = MqttConnection(
        BROKER_LOCAL,
        options=MqttOptions(
            auth=MqttAuthOptions(mode="username_password",
                                 username="myuser", password="mypassword"),
        ),
    )
    if not conn.connect(timeout=10.0):
        raise RuntimeError(f"Failed to connect to broker at {BROKER}")

    transport = MqttTransport(conn, ROBOT_ID)
    robot = Robot(transport=transport)
    Logger.info(f"[manual] connected to {robot._robot_id} ({robot._robot_type})")
    robot.close()


# ── Option 8 ──────────────────────────────────────────────────────────────────
# Use Robot as a context manager for automatic cleanup.
def connect_context_manager():
    with Robot.connect_mqtt(BROKER, ROBOT_ID) as robot:
        Logger.info(f"[context] connected to {robot._robot_id} ({robot._robot_type})")
        robot.tts.say_text("Hello over MQTT!")
    # robot.close() is called automatically on exit


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    try:
        connect_basic()
        # connect_with_username_password()
        # connect_with_tls()
        # connect_with_mtls()
        # connect_websocket_tls()
        # connect_full_options()
        # connect_manual_transport()
        # connect_context_manager()
    except ImportError as e:
        Logger.error(f"Missing dependency: {e}")
        Logger.error("Install MQTT support with: pip install luxai-robot[mqtt]")
    except RuntimeError as e:
        Logger.error(f"Failed to connect: {e}")
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
