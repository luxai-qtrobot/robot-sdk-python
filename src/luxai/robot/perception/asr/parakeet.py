"""
ASRParakeetNode — ASR plugin backed by qtrobot-parakeet-asr-server over Magpie ZMQ.

Flow:
  1. configure(): connect to server, open audio writer + text reader.
  2. recognize_once():
       - wait for VAD (client-side, via MicrophoneStream)
       - stream AudioFrameRaw chunks to server while voice is active
       - send empty AudioFrameRaw sentinel when voice ends
       - background thread reads DictFrame results and emits interim speech events
       - return final (text, language) when DictFrame{is_final=True} arrives
  3. cancel(): send /asr/cancel RPC, stop audio forwarding.
"""

from __future__ import annotations

import queue
import threading
import time
from typing import Optional, Tuple, TYPE_CHECKING

from luxai.magpie.frames import AudioFrameRaw, DictFrame, StringFrame
from luxai.magpie.transport import ZMQRpcRequester, ZmqStreamReader, ZmqStreamWriter
from luxai.magpie.utils import Logger
from luxai.magpie.utils.common import get_uinque_id

from .base import ASRBaseNode, ASRRecogntionEvent
from .microphone_stream import MicrophoneStream

AUDIO_IN_TOPIC = "/asr/audio"
TEXT_OUT_TOPIC  = "/asr/text"


def _extract_host(endpoint: str) -> str:
    """'tcp://192.168.3.111:50860' → '192.168.3.111'"""
    proto = "://"
    pos = endpoint.find(proto)
    if pos < 0:
        return ""
    host_start = pos + len(proto)
    colon = endpoint.rfind(":")
    if colon <= host_start:
        return ""
    return endpoint[host_start:colon]


def _to_connect_endpoint(bind_ep: str, host: str) -> str:
    """'tcp://*:50861' + '192.168.3.111' → 'tcp://192.168.3.111:50861'"""
    return bind_ep.replace("*", host)


class ASRParakeetNode(ASRBaseNode):

    def __init__(self, robot, responder, stream_writer, name="asr-parakeet"):
        super().__init__(robot, responder, stream_writer, name=name)
        self.is_configured = False
        self.is_canceled = False
        self.microphone_stream: Optional[MicrophoneStream] = None
        self._rpc: Optional[ZMQRpcRequester] = None
        self._audio_writer: Optional[ZmqStreamWriter] = None
        self._text_reader: Optional[ZmqStreamReader] = None
        self.language_code = "en"

    # --------------------------------------------------
    # BaseNode lifecycle
    # --------------------------------------------------

    def interrupt(self):
        self.is_canceled = True
        if self.microphone_stream is not None:
            self.microphone_stream.close()

    # --------------------------------------------------
    # ASRBaseNode: Configure
    # --------------------------------------------------

    def configure(self, args: dict) -> bool:
        endpoint = args.get("endpoint", "")
        if not endpoint:
            Logger.error(f"{self.name}: 'endpoint' is required (e.g. 'tcp://10.231.0.2:50860')")
            return False

        self.language_code   = args.get("language", "en")
        self.use_vad         = args.get("use_vad", True)
        self.silence_timeout = args.get("silence_timeout", 1.0)

        # Connect RPC to server base port
        try:
            if self._rpc is not None:
                self._rpc.close()
            self._rpc = ZMQRpcRequester(endpoint)
        except Exception as e:
            Logger.error(f"{self.name}: failed to connect RPC to {endpoint}: {e}")
            return False

        # Query system descriptor to discover stream ports
        try:
            resp = self._rpc.call({"name": "", "args": {}}, 10.0)
            sys_desc = resp.get("response", {}) if isinstance(resp, dict) else {}
            streams = sys_desc.get("stream", {})

            host = _extract_host(endpoint)
            audio_ep = streams[AUDIO_IN_TOPIC]["transports"]["zmq"]["endpoint"]
            text_ep  = streams[TEXT_OUT_TOPIC]["transports"]["zmq"]["endpoint"]

            audio_connect = _to_connect_endpoint(audio_ep, host)
            text_connect  = _to_connect_endpoint(text_ep, host)
        except Exception as e:
            Logger.error(f"{self.name}: failed to parse system descriptor: {e}")
            return False

        # (Re-)open ZMQ streams
        try:
            if self._audio_writer is not None:
                self._audio_writer.close()
            if self._text_reader is not None:
                self._text_reader.close()
            self._audio_writer = ZmqStreamWriter(audio_connect, queue_size=64,
                                                  bind=False, delivery="reliable")
            self._text_reader  = ZmqStreamReader(text_connect, topic=TEXT_OUT_TOPIC,
                                                  queue_size=8, bind=False, delivery="reliable")
        except Exception as e:
            Logger.error(f"{self.name}: failed to open ZMQ streams: {e}")
            return False

        # Send initial language config to server
        try:
            self._rpc.call({"name": "/asr/configure",
                            "args": {"config": {"language": self.language_code}}}, 5.0)
        except Exception as e:
            Logger.warning(f"{self.name}: configure RPC to server failed: {e}")

        # (Re-)create microphone stream
        if self.microphone_stream is not None:
            self.microphone_stream.close()
        self.microphone_stream = MicrophoneStream(
            robot=self._robot,
            use_vad=self.use_vad,
            silence_timeout=self.silence_timeout,
        )
        self.microphone_stream.__enter__()

        self.is_configured = True
        Logger.info(f"{self.name}: configured — endpoint={endpoint} language={self.language_code}")
        return True

    # --------------------------------------------------
    # ASRBaseNode: One-shot recognition
    # --------------------------------------------------

    def recognize_once(self, args: dict | None = None) -> Optional[Tuple[str, str]]:
        timeout = args.get("timeout", 10.0) if args else 10.0

        if not self.is_configured:
            Logger.error(f"{self.name}: not configured. Call configure() first.")
            return None, None

        self.is_canceled = False

        # Re-open mic stream if previously closed
        if self.microphone_stream._closed:
            self.microphone_stream.__enter__()
        self.microphone_stream.reset(seconds_to_keep=0)

        # Wait for voice activity
        start = time.time()
        is_voice = False
        while not is_voice and not self.is_canceled:
            is_voice = self.microphone_stream.wait_for_voice(timeout=0.5)
            if time.time() - start > timeout:
                break

        if self.is_canceled:
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.CANCELED)))
            return None, None

        if not is_voice:
            return None, None

        self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.STARTED)))

        # Assign a gid for this utterance — server echoes it on all text frames
        utterance_gid = get_uinque_id()

        # Background thread: read text results from server and emit speech events
        result_queue: queue.Queue = queue.Queue()
        text_thread = threading.Thread(
            target=self._read_text_stream,
            args=(result_queue,),
            daemon=True,
            name=f"{self.name}-text-reader",
        )
        text_thread.start()

        # Forward audio chunks to server
        try:
            for chunk in self.microphone_stream:
                if self.is_canceled:
                    break
                audio_frame = AudioFrameRaw(
                    gid=utterance_gid,
                    data=bytes(chunk),
                    sample_rate=self.microphone_stream.get_rate(),
                    channels=self.microphone_stream.get_channels(),
                    bit_depth=16,
                    format="PCM",
                )
                self._audio_writer.write(audio_frame.to_dict(), AUDIO_IN_TOPIC)
                self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.RECOGNIZING)))
        except Exception as e:
            Logger.warning(f"{self.name}: audio forwarding error: {e}")

        # Send end-of-utterance sentinel to server
        sentinel = AudioFrameRaw(gid=utterance_gid)
        self._audio_writer.write(sentinel.to_dict(), AUDIO_IN_TOPIC)

        # Wait for final result from text reader thread
        text_thread.join(timeout=5.0)

        if self.is_canceled:
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.CANCELED)))
            return None, None

        try:
            text, language = result_queue.get_nowait()
        except queue.Empty:
            text, language = None, None

        if text:
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.RECOGNIZED)))
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.STOPPED)))
            return text, language

        self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.STOPPED)))
        return None, None

    # --------------------------------------------------
    # Background text reader
    # --------------------------------------------------

    def _read_text_stream(self, result_queue: queue.Queue) -> None:
        while not self.is_canceled:
            try:
                msg, _topic = self._text_reader.read(timeout=2.0)
            except TimeoutError:
                break
            except Exception as e:
                Logger.warning(f"{self.name}: text stream read error: {e}")
                break

            if msg is None:
                continue

            frame = DictFrame.from_dict(msg) if isinstance(msg, dict) else msg
            if not isinstance(frame, DictFrame):
                continue

            value    = frame.value if isinstance(frame.value, dict) else {}
            text     = value.get("text", "")
            language = value.get("language", self.language_code)
            is_final = value.get("is_final", False)

            if text:
                self.on_asr_speech(DictFrame(value={"language": language, "text": text}))

            if is_final:
                result_queue.put((text or None, language))
                break

    # --------------------------------------------------
    # ASRBaseNode: Cancel
    # --------------------------------------------------

    def cancel(self, args: dict | None = None) -> None:
        self.is_canceled = True
        if self.microphone_stream is not None:
            self.microphone_stream.close()
        if self._rpc is not None:
            try:
                self._rpc.call({"name": "/asr/cancel", "args": {}}, 2.0)
            except Exception:
                pass
