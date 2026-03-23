# src/luxai/robot/core/transport/mqtt_options.py
"""
Re-exports of Magpie MQTT option classes for configuring MqttTransport.

Install MQTT support with:
    pip install luxai-robot[mqtt]

Usage:
    from luxai.robot.core.transport import MqttOptions, MqttTlsOptions
    # or from the top-level package:
    from luxai.robot import MqttOptions, MqttTlsOptions

    options = MqttOptions(
        tls=MqttTlsOptions(ca_file="/path/to/ca.crt"),
        auth=MqttAuthOptions(mode="username_password",
                             username="user", password="pass"),
    )
    transport = MqttTransport(conn, "QTRD000320")
    # or via the helper:
    robot = Robot.connect_mqtt("mqtts://broker:8883", "QTRD000320", options=options)
"""
try:
    from luxai.magpie.transport.mqtt import (
        MqttOptions,
        MqttTlsOptions,
        MqttAuthOptions,
        MqttSessionOptions,
        MqttReconnectOptions,
        MqttWillOptions,
        MqttDefaultsOptions,
    )
except ImportError as e:
    raise ImportError(
        "MQTT support requires paho-mqtt. "
        "Install via: pip install luxai-robot[mqtt]"
    ) from e

__all__ = [
    "MqttOptions",
    "MqttTlsOptions",
    "MqttAuthOptions",
    "MqttSessionOptions",
    "MqttReconnectOptions",
    "MqttWillOptions",
    "MqttDefaultsOptions",
]
