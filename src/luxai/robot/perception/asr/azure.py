
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
    def __init__(self, robot: "Robot", use_vad : bool = False):        
        super().__init__()
        # start microphone stream
        self.microphone_stream = MicrophoneStream(
            robot=robot,
            use_vad=use_vad, 
            silence_timeout=None)
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
        self.is_configured = False
        self.audio_input_stream = None
        self.is_canceled = False

    # from BaseNode
    def interrupt(self):
        # Logger.info("ASRAzureNode interrupt()...")
        if self.audio_input_stream is not None:
            self.audio_input_stream.close()
            self.audio_input_stream = None
        self.is_configured = False
    
    # --------------------------------------------------
    # ASRBaseNode: Configure ASR engine 
    # --------------------------------------------------
    def configure(self, args: dict) -> bool:
        # Logger.info("ASRAzureNode configure()...")
        self.subscription = args.get("subscription")
        self.region = args.get("region")
        self.speech_recognition_languages = args.get("languages", ["en-US"])
        self.silence_timeout = args.get("silence_timeout", 0.2)
        self.use_vad = args.get("use_vad", False)

        if not self.subscription or not self.region: 
            Logger.error(f"{self.name} both 'subscription' and 'region' params are needed!")
            return False

        # setup the Azure ASR engine        
        if len(self.speech_recognition_languages) > 1:
            self.auto_detect_language = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=self.speech_recognition_languages)            
        else: 
            self.auto_detect_language = None        
        
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription, 
            region=self.region,
            speech_recognition_language=None if self.auto_detect_language else self.speech_recognition_languages[0])

        self.speech_config.set_property(speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, str(self.silence_timeout*1000))  # set this to higher value for more pause in the speech
        self.speech_config.set_property(speechsdk.PropertyId.Conversation_Initial_Silence_Timeout, "5000")
        self.speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "5000")
        self.audio_input_stream = AudioInputStreamCallback(robot=self._robot, use_vad=self.use_vad)
        self.audio_config = speechsdk.audio.AudioConfig(stream=speechsdk.audio.PullAudioInputStream(self.audio_input_stream))  
        
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, 
                                                            audio_config=self.audio_config,
                                                            auto_detect_source_language_config=self.auto_detect_language)

        # Connect callbacks to the events fired by the speech recognizer            
        self.speech_recognizer.recognizing.connect(lambda evt: self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.RECOGNIZING))))
        self.speech_recognizer.recognized.connect(lambda evt: self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.RECOGNIZED))))
        self.speech_recognizer.session_started.connect(lambda evt: self.on_asr_event(StringFrame(str(value=ASRRecogntionEvent.STARTED))))
        self.speech_recognizer.session_stopped.connect(lambda evt: self.on_asr_event(StringFrame(str(value=ASRRecogntionEvent.STOPPED))))
        self.speech_recognizer.canceled.connect(lambda evt: self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.CANCELED))))
        self.is_configured = True 
        return True

    # --------------------------------------------------
    # ASRBaseNode: One-shot recognition
    # --------------------------------------------------
    def recognize_once(self, args: dict | None = None) -> Optional[Tuple[str, str]]:
        """
        Return recognition result as (language, text) tuple.
        """
        timeout = args.get("timeout", 10.0) if args is not None else 10.0
        if not self.is_configured: 
            Logger.error(f"{self.name} is not configured. have you forget to call the .configure() first?")
            return None, None

        self.is_canceled = False
        self.audio_input_stream.reset()
        start = time.time()
        is_voice = False
        while not is_voice and not self.is_canceled:
            is_voice = self.audio_input_stream.wait_for_voice(timeout=0.5)
            if time.time() - start > timeout:
                break

        if self.is_canceled:
            self.on_asr_event(StringFrame(value=str(ASRRecogntionEvent.CANCELED)))
            return None, None
            
        if not is_voice:
            return None, None
        
        result = self.speech_recognizer.recognize_once_async().get()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:            
            if self.auto_detect_language:
                auto_detect_source_language_result = speechsdk.AutoDetectSourceLanguageResult(result)
                detected_language = auto_detect_source_language_result.language            
            return result.text, detected_language if self.auto_detect_language else self.speech_recognition_languages[0]
                
        if result.reason == speechsdk.ResultReason.NoMatch:            
            return None, None

        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            Logger.warning(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                Logger.error(f"{self.name}: {cancellation_details.error_details}")                

        return None, None

    # --------------------------------------------------
    # ASRBaseNode: Cancel recognition
    # --------------------------------------------------
    def cancel(self, args: dict | None = None) -> dict:
        # Logger.debug("ASRAzureNode cancel()...")
        self.is_canceled = True


