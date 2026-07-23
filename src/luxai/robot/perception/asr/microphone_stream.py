from __future__ import annotations
from typing import TYPE_CHECKING

import queue
import math
from collections import deque
from threading import Event
import numpy as np

from luxai.magpie.utils import Logger
from luxai.magpie.frames import AudioFrameRaw

if TYPE_CHECKING:
    from luxai.robot.core import Robot


class SileroVAD:
    """
    Stateful VAD using Silero's VADIterator for proper streaming detection with
    hysteresis: speech onset is confirmed over multiple frames (avoiding noise
    false-triggers) and offset requires a configurable silence duration.
    """

    def __init__(self, threshold: float = 0.8, rate: int = 16000,
                 min_silence_ms: int = 300, speech_pad_ms: int = 30):
        try:
            import torch
        except ImportError:
            Logger.error("SileroVAD requires torch: pip install torch")
            raise

        self._torch = torch

        if rate not in (16000, 8000):
            raise ValueError("SileroVAD: sample rate must be 16000 or 8000")

        self._rate = rate

        model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            trust_repo=True,
        )
        (_, _, _, VADIterator, _) = utils

        self._iterator = VADIterator(
            model,
            threshold=threshold,
            sampling_rate=rate,
            min_silence_duration_ms=min_silence_ms,
            speech_pad_ms=speech_pad_ms,
        )

    @property
    def triggered(self) -> bool:
        """True when currently inside a confirmed speech segment."""
        return self._iterator.triggered

    def process(self, audio_chunk: bytes) -> bool:
        """
        Feed one audio chunk through the VAD iterator.
        Returns True when a complete speech segment just ended.
        Chunk must be exactly 512 samples @ 16 kHz or 256 samples @ 8 kHz.
        """
        audio_int16 = np.frombuffer(audio_chunk, np.int16)
        if audio_int16.size == 0:
            return False
        audio_float32 = audio_int16.astype('float32') / 32768.0
        tensor = self._torch.from_numpy(audio_float32)
        was_triggered = self._iterator.triggered
        with self._torch.no_grad():
            result = self._iterator(tensor)
        if self._iterator.triggered and not was_triggered:
            Logger.debug("VAD: speech started")
        elif not self._iterator.triggered and was_triggered:
            Logger.debug("VAD: speech ended")
        return result is not None

    def reset(self) -> None:
        """Reset LSTM hidden state and iterator state. Call between recognition sessions."""
        self._iterator.reset_states()
        if hasattr(self._iterator, 'buffer'):
            self._iterator.buffer = []


class MicrophoneStream:
    """
    MicrophoneStream provides an iterator over audio data from a ROS audio topic.
    Supports optional voice activity detection (VAD) using SileroVAD via VADIterator.

    Usage:
        with MicrophoneStream(robot, use_vad=True) as mic:
            for chunk in mic:
                process(chunk)

    Modes:
        - VAD disabled:
            Yields raw audio chunks continuously.

        - VAD enabled, silence_timeout=None  (Azure mode):
            Blocks in __next__() until speech starts, then yields chunks indefinitely.
            The caller (e.g. Azure SDK) is responsible for detecting end-of-speech.

        - VAD enabled, silence_timeout=float  (standalone mode):
            Blocks until speech starts, then yields chunks until the speech segment ends
            (VADIterator detects >= silence_timeout seconds of silence). Raises
            StopIteration at the end of each segment so one utterance is processed per loop.

    Parameters:
        rate: int - sample rate (16000 or 8000)
        num_samples: int - chunk size in samples (512 @ 16 kHz or 256 @ 8 kHz for VAD)
        use_vad: bool
        silence_timeout: None or float
            None  - Azure mode: stream never self-terminates after speech starts
            float - standalone mode: stop when speech ends; value is passed to
                    VADIterator as min_silence_duration_ms so the same parameter
                    controls both the VAD hysteresis and the iteration boundary

    stream_buff only ever holds chunks from a confirmed speech segment (plus a small
    PREROLL_MS pre-roll right before onset) - chunks that arrive while still waiting
    for VAD to trigger are kept in a short rolling _preroll buffer instead, not
    stream_buff, so a recognition session can't accumulate an unbounded backlog of
    silence ahead of the real speech (stream_buff used to be fed unconditionally by
    _callback_audio_stream regardless of VAD state, so __next__()'s consumer would
    end up draining several seconds of pre-speech silence before ever reaching the
    actual utterance).
    """

    # How much audio immediately before confirmed VAD onset to keep and prepend,
    # so the very start of a word isn't clipped by trigger latency.
    PREROLL_MS = 200

    def __init__(self,
                 robot: Robot,
                 rate: int = 16000,
                 num_samples: int = 512,
                 use_vad: bool = False,
                 silence_timeout: float | None = 0.5):

        self._robot = robot
        self._rate = rate
        self._num_samples = num_samples
        self._closed = True
        self._silence_timeout = silence_timeout
        self._streaming_voice = False
        self._speech_ended = False
        self._aborted = False

        vad_silence_ms = int(silence_timeout * 1000) if silence_timeout is not None else 300
        self._vad = SileroVAD(rate=rate, min_silence_ms=vad_silence_ms) if use_vad else None

        # Set when VAD detects speech onset; cleared on reset() or standalone speech-end.
        self._speech_gate = Event()

        max_chunks = math.ceil(60 / (num_samples / rate))
        self.stream_buff = queue.Queue(maxsize=max_chunks)
        self._preroll: deque = deque(maxlen=self._preroll_chunks(num_samples, rate))

        self._robot.microphone.stream.on_int_audio_ch0(self._callback_audio_stream, queue_size=10)

    @classmethod
    def _preroll_chunks(cls, num_samples: int, rate: int) -> int:
        chunk_ms = (num_samples / rate) * 1000
        return max(1, round(cls.PREROLL_MS / chunk_ms))

    def get_channels(self) -> int:
        return 1

    def get_rate(self) -> int:
        return self._rate

    def get_sample_width(self) -> int:
        return 2

    def reset(self, seconds_to_keep: float = 0.5) -> None:
        if seconds_to_keep <= 0:
            self.stream_buff.queue.clear()
        else:
            frames_to_keep = math.ceil(seconds_to_keep / (self._num_samples / self._rate))
            last_items = list(self.stream_buff.queue)[-frames_to_keep:]
            self.stream_buff.queue.clear()
            for item in last_items:
                self.stream_buff.put(item)

        self._preroll.clear()
        self._streaming_voice = False
        self._speech_ended = False
        self._aborted = False
        self._speech_gate.clear()
        if self._vad:
            self._vad.reset()

    def abort_wait(self) -> None:
        """Interrupt the current wait-for-speech without permanently closing the stream."""
        self._aborted = True
        self._speech_gate.set()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._speech_gate.set()  # wake up any blocked __next__()
        try:
            self.stream_buff.queue.clear()
            self.stream_buff.put_nowait(None)
        except queue.Full:
            pass

    def __enter__(self):
        self._speech_gate.clear()
        self._speech_ended = False
        self._streaming_voice = False
        self._aborted = False
        self._closed = False
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __iter__(self):
        return self

    def __get_chunk(self, timeout: float = 1.0) -> bytes:
        try:
            chunk = self.stream_buff.get(timeout=timeout)
            if chunk is None or self._closed:
                raise StopIteration
            return chunk
        except queue.Empty:
            raise StopIteration

    def __next__(self) -> bytes:
        if self._closed:
            raise StopIteration

        if not self._vad:
            return self.__get_chunk(timeout=2)

        # VAD gate: block until speech is confirmed, or we are aborted/closed.
        if not self._streaming_voice:
            while not self._closed and not self._aborted:
                if self._speech_gate.wait(timeout=0.2):
                    if not self._closed and not self._aborted:
                        self._streaming_voice = True
                    break
            if not self._streaming_voice:
                raise StopIteration

        # Standalone mode: stop at the boundary of each speech segment.
        if self._speech_ended and self._silence_timeout is not None:
            self._streaming_voice = False
            self._speech_ended = False
            self._speech_gate.clear()
            raise StopIteration

        return self.__get_chunk(timeout=1)

    def _callback_audio_stream(self, frame: AudioFrameRaw) -> None:
        if self._closed:
            return

        if self._rate != frame.sample_rate:
            self._rate = frame.sample_rate
            self._num_samples = frame.num_frames
            max_chunks = math.ceil(60 / (self._num_samples / self._rate))
            self.stream_buff = queue.Queue(maxsize=max_chunks)
            self._preroll = deque(maxlen=self._preroll_chunks(self._num_samples, self._rate))
            if self._vad and frame.sample_rate not in (8000, 16000):
                self._vad = None
                Logger.error(
                    f"SileroVAD: sample rate must be 16000 or 8000; "
                    f"disabling VAD (current: {frame.sample_rate})"
                )

        chunk = frame.data

        if self._vad is None:
            self._enqueue(chunk)
            return

        try:
            was_triggered = self._vad.triggered
            speech_ended = self._vad.process(chunk)
            now_triggered = self._vad.triggered
        except Exception as e:
            Logger.warning(f"SileroVAD error: {e}")
            return

        if now_triggered and not was_triggered:
            # Speech just confirmed - flush the short pre-roll first so the onset
            # of the word isn't clipped by trigger latency, then this triggering
            # chunk itself.
            for preroll_chunk in self._preroll:
                self._enqueue(preroll_chunk)
            self._preroll.clear()

        if now_triggered or was_triggered:
            # Actively inside (or just finished) a confirmed speech segment.
            self._enqueue(chunk)
            if not now_triggered and speech_ended and self._silence_timeout is not None:
                # Speech segment ended in standalone mode — signal __next__() to stop.
                self._speech_ended = True
        else:
            # Not in a confirmed segment - keep only a short rolling pre-roll
            # instead of buffering unconditionally, or a recognition session
            # would start with however many seconds of silence accumulated
            # while __next__() was still waiting for the gate to open.
            self._preroll.append(chunk)

        if now_triggered:
            self._speech_gate.set()

    def _enqueue(self, chunk: bytes) -> None:
        try:
            self.stream_buff.put_nowait(chunk)
        except queue.Full:
            pass
