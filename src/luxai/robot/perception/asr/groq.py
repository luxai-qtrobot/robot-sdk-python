import io
import time
import wave
from typing import Optional, Tuple

from luxai.magpie.utils import Logger
from luxai.magpie.frames import StringFrame, DictFrame

from .base import ASRBaseNode, ASRRecogntionEvent
from .microphone_stream import MicrophoneStream

try:
    from groq import Groq
except ImportError:
    raise ImportError(
        "groq package is not installed. "
        "Please install it using `pip install groq`."
    )


class ASRGroqNode(ASRBaseNode):

    def __init__(self, robot, responder, stream_writer, name="asr-groq"):
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
        api_key = args.get("api_key")
        if not api_key:
            Logger.error(f"{self.name}: 'api_key' is required!")
            return False

        self.language_code = args.get("language", "en")
        self.context_prompt = args.get("context_prompt", None)
        self.silence_timeout = args.get("silence_timeout", 0.5)
        self.use_vad = args.get("use_vad", True)

        if self.context_prompt and len(self.context_prompt) > 224:
            Logger.error(f"{self.name}: 'context_prompt' must be 224 characters or fewer.")
            return False

        try:
            self.client = Groq(api_key=api_key)
        except Exception as e:
            Logger.error(f"{self.name}: failed to initialize Groq client: {e}")
            return False

        # (re-)create microphone stream
        if self.microphone_stream is not None:
            self.microphone_stream.close()
        self.microphone_stream = MicrophoneStream(
            robot=self._robot,
            use_vad=self.use_vad,
            silence_timeout=self.silence_timeout if self.use_vad else None,
        )
        self.microphone_stream.__enter__()

        self.is_configured = True
        return True

    # --------------------------------------------------
    # ASRBaseNode: One-shot recognition
    # --------------------------------------------------
    def recognize_once(self, args: dict | None = None) -> Optional[Tuple[str, str]]:
        """
        Collect one utterance (VAD-gated) and transcribe it via Groq Whisper.
        Returns (text, language) or (None, None).
        """
        timeout = args.get("timeout", 10.0) if args is not None else 10.0
        if not self.is_configured:
            Logger.error(f"{self.name} is not configured. Have you forgotten to call configure() first?")
            return None, None

        self.is_canceled = False

        # Re-open stream if it was closed by a previous cancel or recognition
        if self.microphone_stream._closed:
            self.microphone_stream.__enter__()
        self.microphone_stream.reset(seconds_to_keep=0)

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

        # Collect audio chunks until the stream ends (silence_timeout reached)
        buffered_chunks = []
        for chunk in self.microphone_stream:
            if self.is_canceled:
                break
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.RECOGNIZING)))
            buffered_chunks.append(chunk)

        if self.is_canceled:
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.CANCELED)))
            return None, None

        if not buffered_chunks:
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.STOPPED)))
            return None, None

        # Pack collected chunks into an in-memory WAV file
        audio_bytes = io.BytesIO()
        with wave.open(audio_bytes, 'wb') as wf:
            wf.setnchannels(self.microphone_stream.get_channels())
            wf.setsampwidth(self.microphone_stream.get_sample_width())
            wf.setframerate(self.microphone_stream.get_rate())
            wf.writeframes(b''.join(buffered_chunks))
        audio_bytes.seek(0)

        # Send to Groq Whisper API
        try:
            transcription = self.client.audio.transcriptions.create(
                file=("audio.wav", audio_bytes.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                language=self.language_code,
                temperature=0.0,
                prompt=self.context_prompt,
            )
            if transcription.text and transcription.text.strip():
                self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.RECOGNIZED)))
                self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.STOPPED)))
                return transcription.text.strip(), self.language_code
        except Exception as e:
            Logger.error(f"{self.name}: Groq API error: {e}")

        self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.STOPPED)))
        return None, None

    # --------------------------------------------------
    # ASRBaseNode: Cancel recognition
    # --------------------------------------------------
    def cancel(self, args: dict | None = None) -> None:
        self.is_canceled = True
        # Close the microphone stream to unblock the audio collection loop
        if self.microphone_stream is not None:
            self.microphone_stream.close()
