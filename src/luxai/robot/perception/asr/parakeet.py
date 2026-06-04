"""
ASRParakeetNode — ASR plugin backed by qtrobot-parakeet-asr-server over Magpie ZMQ.

Flow:
  1. configure(): connect to server via ZMQ, open streams, start always-on text reader thread.
  2. recognize_once():
       - arm final-result event, set current utterance gid
       - iterate MicrophoneStream (blocks until speech, yields chunks, stops on silence)
       - forward AudioFrameRaw chunks to server
       - send empty AudioFrameRaw sentinel when stream ends
       - wait on threading.Event set by always-on thread when is_final frame arrives
       - return (text, language) — base class delivers final via on_asr_speech()
  3. Always-on _text_reader_loop:
       - runs from configure() until interrupt()
       - delivers interim frames immediately via on_asr_speech()
       - on is_final: stores result + sets event (no on_asr_speech — avoids double delivery)
  4. cancel(): close mic stream, set event to unblock recognize_once(), send /asr/cancel RPC.
"""

from __future__ import annotations

import threading
from typing import Optional, Tuple

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

        # Always-on text reader thread
        self._reader_stop = threading.Event()
        self._reader_thread: Optional[threading.Thread] = None

        # Final result signaling for recognize_once()
        self._final_event = threading.Event()
        self._final_result: Tuple[Optional[str], str] = (None, "en")
        self._current_utterance_gid: Optional[str] = None

    # --------------------------------------------------
    # BaseNode lifecycle
    # --------------------------------------------------

    def interrupt(self):
        self.is_canceled = True
        self._final_event.set()     # unblock any waiting recognize_once()
        self._stop_reader_thread()
        if self.microphone_stream is not None:
            self.microphone_stream.close()
            self.microphone_stream = None
        self.is_configured = False

    # --------------------------------------------------
    # ASRBaseNode: Configure
    # --------------------------------------------------

    def configure(self, args: dict) -> bool:
        endpoint = args.get("endpoint", "")
        if not endpoint:
            Logger.error(f"{self.name}: 'endpoint' is required (e.g. 'tcp://10.231.0.3:50860')")
            return False

        self.language_code   = args.get("language", "en")
        self.use_vad         = args.get("use_vad", True)
        self.silence_timeout = args.get("silence_timeout", 0.5)

        # Stop existing reader thread before re-opening streams
        self._stop_reader_thread()

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
            resp     = self._rpc.call({"name": "", "args": {}}, 10.0)
            sys_desc = resp.get("response", {}) if isinstance(resp, dict) else {}
            streams  = sys_desc.get("stream", {})

            host          = _extract_host(endpoint)
            audio_ep      = streams[AUDIO_IN_TOPIC]["transports"]["zmq"]["endpoint"]
            text_ep       = streams[TEXT_OUT_TOPIC]["transports"]["zmq"]["endpoint"]
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

        # Push all server-side config — silence_timeout is shared:
        # client uses it for VAD; server timeout is set slightly higher as fallback
        server_config = {"language": self.language_code,
                         "silence_timeout": self.silence_timeout * 1.2 if self.use_vad else self.silence_timeout}
        for key in ["interim_chunks", "silence_energy_threshold", "max_buffer_seconds"]:
            if key in args:
                server_config[key] = args[key]
        try:
            self._rpc.call({"name": "/asr/configure",
                            "args": {"config": server_config}}, 5.0)
        except Exception as e:
            Logger.warning(f"{self.name}: server configure RPC failed: {e}")

        # (Re-)create microphone stream
        if self.microphone_stream is not None:
            self.microphone_stream.close()
        self.microphone_stream = MicrophoneStream(
            robot=self._robot,
            use_vad=self.use_vad,
            silence_timeout=self.silence_timeout if self.use_vad else None,
        )
        self.microphone_stream.__enter__()

        # Start always-on text reader thread
        self._reader_stop.clear()
        self._reader_thread = threading.Thread(
            target=self._text_reader_loop,
            daemon=True,
            name=f"{self.name}-reader",
        )
        self._reader_thread.start()

        self.is_configured = True
        Logger.info(f"{self.name}: configured — endpoint={endpoint} language={self.language_code}")
        return True

    # --------------------------------------------------
    # Always-on text reader loop
    # --------------------------------------------------

    def _text_reader_loop(self) -> None:
        """
        Runs from configure() until interrupt()/stop_reader_thread().
        - Interim frames (is_final=False): delivered immediately via on_asr_speech().
        - Final frame (is_final=True): stored + signals _final_event so recognize_once()
          can return. NOT delivered here — base class delivers it once via the return value.
        Frames whose gid doesn't match the current utterance are silently dropped.
        """
        while not self._reader_stop.is_set():
            try:
                msg, _topic = self._text_reader.read(timeout=1.0)
            except TimeoutError:
                continue
            except Exception as e:
                Logger.warning(f"{self.name}: text reader error: {e}")
                break

            if msg is None:
                continue

            frame = DictFrame.from_dict(msg) if isinstance(msg, dict) else msg
            if not isinstance(frame, DictFrame):
                continue

            # Drop stale frames from previous utterances
            if frame.gid != self._current_utterance_gid:
                continue

            value    = frame.value if isinstance(frame.value, dict) else {}
            text     = value.get("text", "")
            language = value.get("language", self.language_code)
            is_final = value.get("is_final", False)
            
            if text and not is_final:
                # Interim result — deliver immediately                
                self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.RECOGNIZING)))
                self.on_asr_speech(DictFrame(value={"language": language, "text": text, "is_final": False}))

            if is_final:
                # Final result — signal recognize_once(); base class delivers it
                self._final_result = (text or None, language)
                self._final_event.set()

    def _stop_reader_thread(self) -> None:
        if self._reader_thread is not None and self._reader_thread.is_alive():
            self._reader_stop.set()
            self._reader_thread.join(timeout=2.0)
        self._reader_stop.clear()
        self._reader_thread = None

    # --------------------------------------------------
    # ASRBaseNode: One-shot recognition
    # --------------------------------------------------

    def recognize_once(self, args: dict | None = None) -> Optional[Tuple[str, str]]:
        if not self.is_configured:
            Logger.error(f"{self.name}: not configured. Call configure() first.")
            return None, None, False

        self.is_canceled = False

        if self.microphone_stream._closed:
            self.microphone_stream.__enter__()
        self.microphone_stream.reset(seconds_to_keep=0)  # discard pre-speech buffer to avoid hallucination

        utterance_gid = get_uinque_id()

        # Arm the final event BEFORE sending any audio so no frame is missed
        self._final_result = (None, self.language_code)
        self._current_utterance_gid = utterance_gid
        self._final_event.clear()

        # Forward audio chunks to server
        started_emitted = False
        try:
            for chunk in self.microphone_stream:
                if self.is_canceled:
                    break
                if not started_emitted:
                    self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.STARTED)))
                    started_emitted = True
                audio_frame = AudioFrameRaw(
                    gid=utterance_gid,
                    data=bytes(chunk),
                    sample_rate=self.microphone_stream.get_rate(),
                    channels=self.microphone_stream.get_channels(),
                    bit_depth=16,
                    format="PCM",
                )
                self._audio_writer.write(audio_frame.to_dict(), AUDIO_IN_TOPIC)                
        except Exception as e:
            Logger.warning(f"{self.name}: audio forwarding error: {e}")

        # Send end-of-utterance sentinel to server
        sentinel = AudioFrameRaw(gid=utterance_gid)
        self._audio_writer.write(sentinel.to_dict(), AUDIO_IN_TOPIC)

        # Wait for always-on thread to signal final result (or cancel)
        self._final_event.wait(timeout=10.0)
        self._current_utterance_gid = None

        if self.is_canceled:
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.CANCELED)))
            return None, None, False

        text, language = self._final_result

        if text:
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.RECOGNIZED)))
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.STOPPED)))
            return language, text, True

        self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.STOPPED)))
        return None, None, False

    # --------------------------------------------------
    # ASRBaseNode: Cancel
    # --------------------------------------------------

    def cancel(self, args: dict | None = None) -> None:
        self.is_canceled = True
        self._final_event.set()     # unblock recognize_once() if waiting
        if self.microphone_stream is not None:
            self.microphone_stream.close()
        if self._rpc is not None:
            try:
                self._rpc.call({"name": "/asr/cancel", "args": {}}, 2.0)
            except Exception:
                pass
