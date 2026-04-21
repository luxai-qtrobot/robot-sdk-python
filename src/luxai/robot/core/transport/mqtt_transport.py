# src/luxai/robot/core/transport/mqtt_transport.py
from __future__ import annotations

import threading
from typing import Any, Dict, Optional

from luxai.magpie.utils import Logger
from luxai.magpie.transport import RpcRequester
from luxai.magpie.transport import StreamReader
from luxai.magpie.transport import StreamWriter

from .transport import Transport, TransportsMeta, UnsupportedAPIError


class MqttTransport(Transport):
    """
    MQTT-based Transport implementation using the Magpie MQTT library.

    Connects to a QTrobot via an MQTT broker and the qtrobot-service-hub-gateway-mqtt,
    which bridges the robot's ZMQ RPC and stream APIs to MQTT topics.

    Service discovery is performed by calling the gateway's descriptor service on
    the robot_id topic (e.g. "QTRD000320/rpc/req"), which returns the system
    description with mqtt transport info for every RPC and stream endpoint.

    Requires: pip install luxai-robot[mqtt]
    """

    _DEFAULT_QUEUE_SIZE = 10

    def __init__(
        self,
        connection,
        robot_id: str,
        connect_timeout: float = 5.0,
        owns_connection: bool = True,
    ) -> None:
        """
        Args:
            connection: A connected MqttConnection instance (from luxai.magpie).
            robot_id: Robot or plugin identifier (e.g. ``"QTRD000320"`` or
                      ``"qtrobot-realsense-driver"``). Used as the MQTT namespace
                      for the descriptor call.
            connect_timeout: Used as the ack_timeout for the descriptor RPC requester,
                             so the ACK window scales with the user's patience
                             (important for cloud/high-latency brokers).
            owns_connection: If ``True`` (default), ``close()`` will disconnect the
                             broker connection. Set to ``False`` for plugin transports
                             that share the robot's connection.
        """
        self._connection = connection
        self._robot_id = robot_id
        self._connect_timeout = connect_timeout
        self._owns_connection = owns_connection

        self._requesters: Dict[str, RpcRequester] = {}
        self._stream_resources: list = []
        self._lock = threading.Lock()
        self._closed = False

        Logger.debug(f"MqttTransport: ready, robot_id={robot_id!r}")

    @property
    def connection(self):
        """The underlying MqttConnection, for sharing with plugin transports."""
        return self._connection

    # ------------------------------------------------------------------
    # RPCs
    # ------------------------------------------------------------------

    def _get_or_create_requester(self, topic: str, ack_timeout: float = 2.0) -> RpcRequester:
        with self._lock:
            requester = self._requesters.get(topic)
            if requester is not None:
                return requester
            from luxai.magpie.transport.mqtt import MqttRpcRequester
            requester = MqttRpcRequester(self._connection, service_name=topic, ack_timeout=ack_timeout)
            self._requesters[topic] = requester
            Logger.debug(f"MqttTransport: created MqttRpcRequester for topic={topic!r}, ack_timeout={ack_timeout}s")
            return requester

    def get_requester(
        self,
        service_name: str,
        transports: TransportsMeta | None,
    ) -> RpcRequester:
        if self._closed:
            raise RuntimeError("MqttTransport is closed")

        if transports is None:
            # Initial descriptor call — the gateway exposes the system descriptor
            # at the robot_id topic (e.g. "QTRD000320/rpc/req").
            # Use connect_timeout as ack_timeout so cloud/high-latency brokers
            # get a generous window that matches the user's stated patience.
            topic = self._robot_id
            return self._get_or_create_requester(topic, ack_timeout=self._connect_timeout)
        else:
            mqtt_info = transports.get("mqtt")
            if not mqtt_info:
                raise UnsupportedAPIError(
                    f"Service {service_name!r} is not available over MQTT."
                )
            topic = mqtt_info["topic"]

        return self._get_or_create_requester(topic)

    # ------------------------------------------------------------------
    # Streams
    # ------------------------------------------------------------------

    def get_stream_reader(
        self,
        topic: str,
        transports: TransportsMeta,
        queue_size: int | None = None,
    ) -> StreamReader:
        if self._closed:
            raise RuntimeError("MqttTransport is closed")

        mqtt_info = transports.get("mqtt")
        if not mqtt_info:
            raise UnsupportedAPIError(f"Stream {topic!r} is not available over MQTT.")

        mqtt_topic = mqtt_info["topic"]
        qos: Optional[int] = mqtt_info.get("qos")

        if queue_size is not None:
            qsize = int(queue_size)
        else:
            qsize = int(mqtt_info.get("queue_size", self._DEFAULT_QUEUE_SIZE))

        from luxai.magpie.transport.mqtt import MqttStreamReader
        sub = MqttStreamReader(
            connection=self._connection,
            topic=mqtt_topic,
            queue_size=qsize,
            qos=qos,
        )
        Logger.debug(
            f"MqttTransport: created MqttStreamReader for topic={mqtt_topic!r}, "
            f"queue_size={qsize}"
        )
        self._stream_resources.append(sub)
        return sub

    def get_stream_writer(
        self,
        topic: str,
        transports: TransportsMeta,
        queue_size: int | None = None,
    ) -> StreamWriter:
        if self._closed:
            raise RuntimeError("MqttTransport is closed")

        mqtt_info = transports.get("mqtt")
        if not mqtt_info:
            raise UnsupportedAPIError(f"Stream {topic!r} is not writable over MQTT.")

        qos: Optional[int] = mqtt_info.get("qos")

        if queue_size is not None:
            qsize = int(queue_size)
        else:
            qsize = int(mqtt_info.get("queue_size", self._DEFAULT_QUEUE_SIZE))

        from luxai.magpie.transport.mqtt import MqttStreamWriter
        pub = MqttStreamWriter(
            connection=self._connection,
            queue_size=qsize,
            qos=qos,
        )
        Logger.debug(
            f"MqttTransport: created MqttStreamWriter for topic={topic!r}, "
            f"queue_size={qsize}"
        )
        self._stream_resources.append(pub)
        return pub

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        if self._closed:
            return

        for resource in self._stream_resources:
            try:
                resource.close()
            except Exception:
                pass
        self._stream_resources.clear()

        with self._lock:
            for topic, requester in list(self._requesters.items()):
                try:
                    requester.close()
                    Logger.debug(f"MqttTransport: closed requester for {topic!r}")
                except Exception as e:
                    Logger.warning(
                        f"MqttTransport: error closing requester {topic!r}: {e}"
                    )
            self._requesters.clear()

        if self._owns_connection:
            try:
                self._connection.disconnect()
            except Exception as e:
                Logger.warning(f"MqttTransport: error disconnecting MQTT: {e}")

        self._closed = True
