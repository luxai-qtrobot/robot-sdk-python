from __future__ import annotations
from typing import TYPE_CHECKING

import queue
import math
from threading import Event
import time
import numpy as np

from luxai.magpie.utils import Logger
from luxai.magpie.frames import AudioFrameFlac


if TYPE_CHECKING:
    from luxai.robot.core import Robot

class SileroVAD:
    """
    SileroVAD is a wrapper for the Silero VAD model loaded via torch.hub.
    It supports voice activity detection for 16kHz or 8kHz mono audio streams.

    Methods:
        - is_voice(audio_chunk: bytes) -> bool:
            Returns True if voice is detected in the given audio chunk.
    """    
    def __init__(self, confidence_threshold=0.6, rate=16000):
        import torch
        self._torch = torch
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            trust_repo=True
        )

        if rate not in (16000, 8000):
            raise ValueError("SileroVAD: sample rate must be 16000 or 8000")

        self._rate = rate
        self.confidence_threshold = confidence_threshold
        (self.get_speech_timestamps, self.save_audio,
         self.read_audio, self.VADIterator, self.collect_chunks) = utils

    def is_voice(self, audio_chunk: bytes) -> bool:        
        audio_int16 = np.frombuffer(audio_chunk, np.int16)
        if audio_int16.size == 0:
            return False
        audio_float32 = audio_int16.astype('float32') / 32768.0
        audio_tensor = self._torch.from_numpy(audio_float32)
        confidence = 0
        with self._torch.no_grad():  # Prevents autograd from building a graph and memory leaks
            confidence = self.model(audio_tensor, self._rate).item()
        return confidence > self.confidence_threshold


class MicrophoneStream:
    """
    MicrophoneStream provides an iterator over audio data from a ROS audio topic.
    It supports optional voice activity detection (VAD) using SileroVAD.

    Usage:
        with MicrophoneStream(use_vad=True, silence_timeout=1.0) as mic:
            for audio_chunk in mic:
                process(audio_chunk)

    Modes:
        - VAD disabled (`use_vad=False`):
            Yields raw audio chunks continuously, without any voice filtering.

        - VAD enabled (`use_vad=True`, `silence_timeout=None`):
            Blocks until voice is detected, then yields all chunks continuously.
            The iterator never ends unless the stream is closed or manually interrupted.

        - VAD enabled (`use_vad=True`, `silence_timeout=seconds`):
            Blocks until voice is detected, then yields chunks one by one (including silence).
            Ends the iteration after the specified duration of continuous silence,
            allowing your loop to process one complete voice segment per iteration.
            
    Parameters:
        ros_audio_topic: str - ROS topic name for audio input (default: /qt_respeaker_app/channel0)
        rate: int - Audio sample rate (default: 16000)
        num_samples: int - Audio chunk size in samples
        use_vad: bool - Enable or disable VAD-based streaming
        silence_timeout: float or None - If set, ends a voice segment after this many seconds of silence
    """

    AUDIO_PRE_VOICE_BUFFER_TIME = 0.3 # seconds

    def __init__(self,
                 robot: Robot,
                 rate=16000,
                 num_samples=512,
                 use_vad=True,
                 silence_timeout=1.0):

        self._robot = robot
        self._vad = SileroVAD(rate=rate) if use_vad else None
        self._silence_timeout = silence_timeout
        self._rate = rate
        self._num_samples = num_samples
        self._closed = True
        self._voice_event = Event()  # Event to signal voice detection        
        self._last_voice_time = None
        self._streaming_voice = False

        # Buffer: 60 seconds worth of chunks
        max_chunks = math.ceil(60 / (num_samples / rate))
        self.stream_buff = queue.Queue(maxsize=max_chunks)

        self._robot.microphone.stream.on_channel0(self._callback_audio_stream, queue_size=10)

    def get_channels(self):
        """
        Returns the channel number of the audio stream.
        """
        return 1

    def get_rate(self):       
        """
        Returns the sample rate of the audio stream.
        """
        return self._rate

    def get_sample_width(self):
        """
        Returns the sample width of the audio stream in bytes.
        """
        return 2

    def reset(self, seconds_to_keep=0.5):
        # self.stream_buff.queue.clear()  # Clear the queue
        if seconds_to_keep <= 0:
            self.stream_buff.queue.clear()  # Clear the queue
            self._streaming_voice = False
            self._voice_event.clear()
            return 
        
        frames_to_keep = math.ceil(seconds_to_keep / (self._num_samples/self._rate))        
        # delete all except last frames_to_keep
        last_two_items = list(self.stream_buff.queue)[-1 * frames_to_keep:]  # Get the last item
        self.stream_buff.queue.clear()  # Clear the queue
        for item in last_two_items:
            self.stream_buff.put(item)  # Reinsert the last two items
        self._streaming_voice = False
        self._voice_event.clear()


    def close(self):
        self._closed = True


    def wait_for_voice(self, timeout=None):
        if not self._vad:
            return True
        # This will block until voice_event is set
        if not self._voice_event.wait(timeout=timeout):
            return False
        return not self._closed


    def __enter__(self):   
        self._voice_event.clear()     
        self._closed = False   
        return self

    def __exit__(self, exc_type, exc_value, traceback):        
        self._voice_event.set()
        self._closed = True
        self.stream_buff.put((None, False))
        
    def __iter__(self):
        return self


    def __get_chunk(self, timeout=1):
        try:
            chunk, is_voice = self.stream_buff.get(timeout=timeout)
            if chunk is None or self._closed:
                raise StopIteration
            return chunk, is_voice
        except queue.Empty:
            raise StopIteration


    def __next__(self):        
        if self._closed: # or rospy.is_shutdown():
            raise StopIteration

        if not self._vad:
            chunk, _ = self.__get_chunk(timeout=2)
            return chunk

        # First chunk after silence: wait for voice
        if not self._streaming_voice:
            while not self._closed: #rospy.is_shutdown():
                chunk, is_voice = self.__get_chunk(timeout=1)
                if is_voice:
                    self._last_voice_time = time.time()
                    self._streaming_voice = True
                    return chunk
            raise StopIteration

        # Streaming phase: return chunks until prolonged silence        
        chunk, is_voice = self.__get_chunk(timeout=1)
        if is_voice:
            self._last_voice_time = time.time()
        elif self._silence_timeout is not None and time.time() - self._last_voice_time > self._silence_timeout:
            self._streaming_voice = False
            raise StopIteration

        return chunk
  

    def _callback_audio_stream(self, frame:AudioFrameFlac):
        if not self._closed:
            try:
                # re-iitlaize buffer size if needed 
                if self._rate != frame.sample_rate or self._num_samples != frame.num_frames: 
                    self._rate = frame.sample_rate
                    self._num_samples = frame.num_frames
                    # Buffer: 60 seconds worth of chunks
                    max_chunks = math.ceil(60 / (self._num_samples / self._rate))
                    self.stream_buff = queue.Queue(maxsize=max_chunks)
                    if self._vad and frame.sample_rate not in [8000, 16000]:
                        self._vad = None
                        Logger.error(f"SileroVAD: sample rate must be 16000 or 8000; Disabling VAD! (current sample rate: {frame.sample_rate})")
                
                chunk = frame.to_pcm()
                is_voice = False
                try:
                    is_voice = self._vad.is_voice(chunk) if self._vad else False
                    if is_voice:
                        self._voice_event.set()
                except Exception as e:
                    pass
                self.stream_buff.put_nowait((chunk, is_voice))
            except queue.Full:
                pass  # drop if buffer is full