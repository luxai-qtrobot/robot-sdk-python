# src/luxai/robot/core/transport/webrtc_transport.py
from __future__ import annotations

import threading
from typing import Dict, Optional

from luxai.magpie.utils import Logger
from luxai.magpie.transport import RpcRequester
from luxai.magpie.transport import StreamReader
from luxai.magpie.transport import StreamWriter

from .transport import Transport, TransportsMeta, UnsupportedAPIError


class WebRTCTransport(Transport):
    """
    WebRTC-based Transport implementation using the Magpie WebRTC library.

    Connects to a QTrobot directly via a P2P WebRTC peer connection.  Signaling
    (SDP offer/answer + ICE candidates) is exchanged through a pluggable
    WebRtcSignaler — use MQTT signaling for internet connectivity or ZMQ
    signaling for broker-less LAN use.

    All RPC calls and stream data travel over a single ``"magpie"`` data channel;
    video and audio streams use dedicated native WebRTC media tracks.

    Requires: pip install luxai-robot[webrtc]
    """

    _DEFAULT_QUEUE_SIZE = 10

    def __init__(self, connection) -> None:
        """
        Args:
            connection: A connected WebRTCConnection instance (from luxai.magpie).
        """
        self._connection = connection
        self._requesters: Dict[str, RpcRequester] = {}
        self._stream_resources: list = []
        self._lock = threading.Lock()
        self._closed = False

        Logger.debug("WebRTCTransport: ready")

    # ------------------------------------------------------------------
    # RPCs
    # ------------------------------------------------------------------

    def _get_or_create_requester(self, service_name: str, ack_timeout: float = 2.0) -> RpcRequester:
        with self._lock:
            requester = self._requesters.get(service_name)
            if requester is not None:
                return requester
            from luxai.magpie.transport.webrtc import WebRTCRpcRequester
            requester = WebRTCRpcRequester(
                self._connection,
                service_name=service_name,
                ack_timeout=ack_timeout,
            )
            self._requesters[service_name] = requester
            Logger.debug(f"WebRTCTransport: created WebRTCRpcRequester for service={service_name!r}")
            return requester

    def get_requester(
        self,
        service_name: str,
        transports: TransportsMeta | None,
    ) -> RpcRequester:
        if self._closed:
            raise RuntimeError("WebRTCTransport is closed")

        if transports is None:
            # Initial descriptor call — route by service name directly on the
            # data channel; the robot-side WebRTC responder handles it.
            return self._get_or_create_requester(service_name)

        webrtc_info = transports.get("webrtc")
        if not webrtc_info:
            raise UnsupportedAPIError(
                f"Service {service_name!r} is not available over WebRTC."
            )

        return self._get_or_create_requester(service_name)

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
            raise RuntimeError("WebRTCTransport is closed")

        webrtc_info = transports.get("webrtc")
        if not webrtc_info:
            raise UnsupportedAPIError(f"Stream {topic!r} is not available over WebRTC.")

        webrtc_topic = webrtc_info.get("topic", topic)
        qsize = int(queue_size) if queue_size is not None else int(
            webrtc_info.get("queue_size", self._DEFAULT_QUEUE_SIZE)
        )

        from luxai.magpie.transport.webrtc import WebRTCSubscriber
        sub = WebRTCSubscriber(connection=self._connection, topic=webrtc_topic, queue_size=qsize)
        Logger.debug(f"WebRTCTransport: created WebRTCSubscriber for topic={webrtc_topic!r}, queue_size={qsize}")
        self._stream_resources.append(sub)
        return sub

    def get_stream_writer(
        self,
        topic: str,
        transports: TransportsMeta,
        queue_size: int | None = None,
    ) -> StreamWriter:
        if self._closed:
            raise RuntimeError("WebRTCTransport is closed")

        webrtc_info = transports.get("webrtc")
        if not webrtc_info:
            raise UnsupportedAPIError(f"Stream {topic!r} is not writable over WebRTC.")

        qsize = int(queue_size) if queue_size is not None else int(
            webrtc_info.get("queue_size", self._DEFAULT_QUEUE_SIZE)
        )

        from luxai.magpie.transport.webrtc import WebRTCPublisher
        pub = WebRTCPublisher(connection=self._connection, queue_size=qsize)
        Logger.debug(f"WebRTCTransport: created WebRTCPublisher for topic={topic!r}, queue_size={qsize}")
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
            for service_name, requester in list(self._requesters.items()):
                try:
                    requester.close()
                    Logger.debug(f"WebRTCTransport: closed requester for {service_name!r}")
                except Exception as e:
                    Logger.warning(
                        f"WebRTCTransport: error closing requester {service_name!r}: {e}"
                    )
            self._requesters.clear()

        try:
            self._connection.disconnect()
        except Exception as e:
            Logger.warning(f"WebRTCTransport: error disconnecting WebRTC: {e}")

        self._closed = True
