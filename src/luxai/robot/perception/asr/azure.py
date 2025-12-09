
# import queue
# from threading import Thread

import time
from typing import Any, Optional, TYPE_CHECKING, Tuple
from luxai.magpie.utils import Logger
from luxai.magpie.frames import StringFrame, DictFrame

from .base import ASRBaseNode, ASRRecogntionEvent
from .microphone_stream import MicrophoneStream
try:
    import azure.cognitiveservices.speech as speechsdk 
except ImportError:
    raise ImportError("azure.cognitiveservices.speech package is not installed. Please install it using `pip install azure-cognitiveservices-speech`.")



class AudioInputStreamCallback(speechsdk.audio.PullAudioInputStreamCallback):
    def __init__(self):
        super().__init__()
        # start microphone stream
        self.microphone_stream = MicrophoneStream(use_vad=True, silence_timeout=None)
        self.microphone_stream.__enter__()  # manually enter the context
        self._stream_iterator = iter(self.microphone_stream)

    def read(self, buffer: memoryview) -> int:        
        try:
            chunk = next(self._stream_iterator)
            if chunk is None:
                return 0
            buffer[:len(chunk)] = chunk
            return len(chunk)
        except StopIteration:
            return 0  # Stream ended
        except Exception as e:
            Logger.warning(f'AudioInputStreamCallback: {str(e)}')
            return 0

    def close(self):
        # Logger.debug(f'AudioInputStreamCallback is closed.')
        self.microphone_stream.__exit__(None, None, None)  # manually exit the context        

    def reset(self):
        # Logger.debug(f'AudioInputStreamCallback is reset.')
        self.microphone_stream.reset()

    def wait_for_voice(self, timeout=None):
        return self.microphone_stream.wait_for_voice(timeout=timeout)



class ASRAzureNode(ASRBaseNode):

    def __init__(self, robot, responder, stream_writer, name="azure"):
        super().__init__(robot, responder, stream_writer, name=name)        

    # from BaseNode
    def setup(self):
        Logger.info("ASRAzureNode setup()...")
        pass

    # from BaseNode
    def interrupt(self):
        Logger.info("ASRAzureNode interrupt()...")
        pass        
    
    # --------------------------------------------------
    # ASRBaseNode: Configure ASR engine 
    # --------------------------------------------------
    def configure(self, args: dict) -> dict:
        Logger.info("ASRAzureNode configure()...")        
        return True

    # --------------------------------------------------
    # ASRBaseNode: One-shot recognition
    # --------------------------------------------------
    def recognize_once(self, args: dict | None = None) -> Optional[Tuple[str, str]]:
        """
        Return a fake speech recognition result.
        """
        Logger.info("ASRAzureNode recognize_once()...")
        time.sleep(1.0)
        return "en-US", "You said hello, right?"

    # --------------------------------------------------
    # ASRBaseNode: Cancel recognition
    # --------------------------------------------------
    def cancel(self, args: dict | None = None) -> dict:
        Logger.info("ASRAzureNode cancel()...")

