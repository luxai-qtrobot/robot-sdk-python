import time
from typing import Any, Optional, Tuple

from luxai.magpie.utils import Logger
from luxai.magpie.frames import StringFrame, DictFrame

from .base import ASRBaseNode, ASRRecogntionEvent
from .microphone_stream import MicrophoneStream

try:
    import riva.client
    import grpc
except ImportError:
    raise ImportError(
        "nvidia-riva-client package is not installed. "
        "Please install it using `pip install nvidia-riva-client`."
    )


class ASRRivaNode(ASRBaseNode):

    def __init__(self, robot, responder, stream_writer, name="asr-riva"):
        super().__init__(robot, responder, stream_writer, name=name)
        self.is_configured = False
        self.microphone_stream: Optional[MicrophoneStream] = None
        self.is_canceled = False

    # from BaseNode
    def interrupt(self):
        if self.microphone_stream is not None:
            self.microphone_stream.close()
            self.microphone_stream = None
        self.is_configured = False

    # --------------------------------------------------
    # ASRBaseNode: Configure ASR engine
    # --------------------------------------------------
    def configure(self, args: dict) -> bool:
        self.server = args.get("server", "localhost:50051")
        self.language_code = args.get("language", "en-US")
        self.use_ssl = args.get("use_ssl", False)
        self.ssl_cert = args.get("ssl_cert", None)
        self.profanity_filter = args.get("profanity_filter", False)
        self.automatic_punctuation = args.get("automatic_punctuation", True)
        self.use_vad = args.get("use_vad", False)

        try:
            self.auth = riva.client.Auth(self.ssl_cert, self.use_ssl, self.server)
            self.asr_service = riva.client.ASRService(self.auth)
            self.riva_config = riva.client.StreamingRecognitionConfig(
                config=riva.client.RecognitionConfig(
                    encoding=riva.client.AudioEncoding.LINEAR_PCM,
                    language_code=self.language_code,
                    max_alternatives=1,
                    profanity_filter=self.profanity_filter,
                    enable_automatic_punctuation=self.automatic_punctuation,
                    verbatim_transcripts=True,
                    enable_word_time_offsets=False,
                    sample_rate_hertz=16000,
                    audio_channel_count=1,
                ),
                interim_results=True,
            )
        except Exception as e:
            Logger.error(f"{self.name}: failed to configure Riva client: {e}")
            return False

        # (re-)create microphone stream
        if self.microphone_stream is not None:
            self.microphone_stream.close()
        self.microphone_stream = MicrophoneStream(
            robot=self._robot,
            use_vad=self.use_vad,
            silence_timeout=None,
        )
        self.microphone_stream.__enter__()

        self.is_configured = True
        return True

    # --------------------------------------------------
    # ASRBaseNode: One-shot recognition
    # --------------------------------------------------
    def recognize_once(self, args: dict | None = None) -> Optional[Tuple[str, str]]:
        """
        Return recognition result as (text, language) tuple or (None, None).
        """
        timeout = args.get("timeout", 10.0) if args is not None else 10.0
        if not self.is_configured:
            Logger.error(f"{self.name} is not configured. Have you forgotten to call configure() first?")
            return None, None

        self.is_canceled = False

        # Re-open stream if it was closed by a previous cancel or recognition
        if self.microphone_stream._closed:
            self.microphone_stream.__enter__()
        self.microphone_stream.reset()

        # Wait for voice activity (with optional timeout)
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

        try:
            responses = self.asr_service.streaming_response_generator(
                audio_chunks=self.microphone_stream,
                streaming_config=self.riva_config,
            )
            for response in responses:
                if self.is_canceled:
                    break
                if not response.results:
                    continue
                for result in response.results:
                    if not result.alternatives:
                        continue
                    self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.RECOGNIZING)))
                    transcript = result.alternatives[0].transcript
                    if result.is_final:
                        self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.RECOGNIZED)))
                        # Close stream to cleanly terminate the gRPC generator
                        self.microphone_stream.close()
                        return transcript.strip(), self.language_code

        except Exception as e:
            if not self.is_canceled:
                code = None
                try:
                    code = e.code()
                except Exception:
                    pass
                if code == grpc.StatusCode.UNAVAILABLE:
                    Logger.error(f"{self.name}: Riva server unavailable at '{self.server}'. Will retry on next call.")
                    try:
                        self.auth = riva.client.Auth(self.ssl_cert, self.use_ssl, self.server)
                        self.asr_service = riva.client.ASRService(self.auth)
                    except Exception:
                        pass
                else:
                    Logger.warning(f"{self.name}: recognition error: {e}")

        if self.is_canceled:
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.CANCELED)))
        else:
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.STOPPED)))

        return None, None

    # --------------------------------------------------
    # ASRBaseNode: Cancel recognition
    # --------------------------------------------------
    def cancel(self, args: dict | None = None) -> None:
        self.is_canceled = True
        # Close the microphone stream to unblock the streaming generator iterator
        if self.microphone_stream is not None:
            self.microphone_stream.close()
