"""
connect_zmq_example.py

Shows the different ways to create a Robot client over ZMQ transport.

Requirements:
    pip install luxai-robot
"""
from luxai.magpie.utils import Logger
from luxai.robot.core import Robot
from luxai.robot.core.transport import ZmqTransport


# ── Option 1 ──────────────────────────────────────────────────────────────────
# Connect by explicit endpoint (fastest — no discovery).
# Use this when you know the robot's IP address.
def connect_by_endpoint():
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500")
    Logger.info(f"[endpoint] connected to {robot._robot_serial} ({robot._robot_type})")
    robot.close()


# ── Option 2 ──────────────────────────────────────────────────────────────────
# Connect by robot_id (robot serial number).
# The SDK resolves the robot's IP automatically via Zeroconf/mDNS discovery.
# The robot must be reachable on the local network.
def connect_by_robot_id():
    robot = Robot.connect_zmq(robot_id="QTRD000320")
    Logger.info(f"[robot_id] connected to {robot._robot_serial} ({robot._robot_type})")
    robot.close()


# ── Option 3 ──────────────────────────────────────────────────────────────────
# Connect by robot_id with a custom discovery timeout.
def connect_by_robot_id_with_timeout():
    robot = Robot.connect_zmq(robot_id="QTRD000320", connect_timeout=10.0)
    Logger.info(f"[robot_id+timeout] connected to {robot._robot_serial} ({robot._robot_type})")
    robot.close()


# ── Option 4 ──────────────────────────────────────────────────────────────────
# Connect with a custom default RPC timeout.
# All RPC calls (robot.tts.say_text(), etc.) will use this timeout unless
# a per-call timeout is specified explicitly.
def connect_with_rpc_timeout():
    robot = Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500", default_rpc_timeout=10.0)
    Logger.info(f"[rpc_timeout] connected to {robot._robot_serial} ({robot._robot_type})")
    robot.close()


# ── Option 5 ──────────────────────────────────────────────────────────────────
# Power-user style: construct ZmqTransport manually and pass it to Robot().
# Useful when you need direct control over the transport lifecycle or want to
# share a transport across multiple objects.
def connect_manual_transport():
    transport = ZmqTransport(endpoint="tcp://10.231.0.2:50500")
    robot = Robot(transport=transport)
    Logger.info(f"[manual] connected to {robot._robot_serial} ({robot._robot_type})")
    robot.close()


# ── Option 6 ──────────────────────────────────────────────────────────────────
# Use Robot as a context manager for automatic cleanup.
def connect_context_manager():
    with Robot.connect_zmq(endpoint="tcp://10.231.0.2:50500") as robot:
        Logger.info(f"[context] connected to {robot._robot_serial} ({robot._robot_type})")
        robot.tts.say_text("Hello from ZMQ!")
    # robot.close() is called automatically on exit


if __name__ == "__main__":
    # Logger.set_level("DEBUG")

    try:
        connect_by_endpoint()
        # connect_by_robot_id()
        # connect_by_robot_id_with_timeout()
        # connect_with_rpc_timeout()
        # connect_manual_transport()
        # connect_context_manager()
    except RuntimeError as e:
        Logger.error(f"Failed to connect: {e}")
    except KeyboardInterrupt:
        Logger.info("Interrupted by user.")
