from __future__ import annotations

from enum import Enum
import time
from typing import Any, Optional, Tuple
from abc import abstractmethod
import threading

from luxai.magpie.utils import Logger
from luxai.magpie.frames import StringFrame, DictFrame
from luxai.magpie.nodes import ServerNode
from luxai.magpie.transport import RpcResponder, StreamWriter


class ASRRecogntionEvent(Enum):
    STARTED = "STARTED"
    RECOGNIZING = "RECOGNIZING"
    RECOGNIZED = "RECOGNIZED"
    STOPPED = "STOPPED"
    CANCELED = "CANCELED"
    

class ASRBaseNode(ServerNode):
    """
    Base node for ASR backends (Azure, Google, Riva, ...).

    RPCs (per provider, e.g. name="azure"):
        - /{name}/configure  e.g /asr-azure/configure
        - /{name}/recognize
        - /{name}/recognize/cancel

    Streams:
        - /{name}/speech  (continuous / interim results)
        - /{name}/event   (high-level events / final results)
    """

    def __init__(
        self,
        robot: "Robot",
        responder: RpcResponder,
        stream_writer: StreamWriter,
        name: str,
        setup_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        self._robot = robot
        self._stream_writer = stream_writer        

        self._asr_engine_lock = threading.Lock()
        self._stream_writer_lock = threading.Lock()

        self._cont_recog_thread: threading.Thread | None = None
        self._cont_recog_stop_event = threading.Event()

        super().__init__(
            name=name,
            responder=responder,
            handler=self._on_rpc_request,
            setup_kwargs=setup_kwargs or {},
        )

    # ------------------------------------------------------------------
    # RPC dispatcher
    # ------------------------------------------------------------------
    def _on_rpc_request(self, req: object) -> dict[str, Any]:
        if req is None:
            return {"status": False, "response": None}

        if not isinstance(req, dict):
            Logger.warning(f"ASR {self.name}: unexpected request type {type(req)}")
            return {"status": False, "response": None}

        try:
            name = req["name"]
            args = req.get("args") or {}
        except Exception as e:
            Logger.warning(f"ASR {self.name}: malformed request {req} ({e})")
            return {"status": False, "response": None}

        # base = f"/asr/{self.name}"

        try:
            if name == f"/{self.name}/configure":
                # stop any running continuous loop first
                self._enable_continuous_mode(False)

                # let engine configure itself
                with self._asr_engine_lock:
                    response = self.configure(args)

                # optional continuous mode
                if args.get("continuous_mode", False):
                    self._enable_continuous_mode(True)

            elif name == f"/{self.name}/recognize":
                with self._asr_engine_lock:
                    response = self.recognize_once(args)

            elif name == f"/{self.name}/recognize/cancel":
                response = self.cancel(args)

            else:
                Logger.warning(f"{self.name}: received unknown request {name}")
                return {"status": False, "response": None}

            return {"status": bool(response), "response": response}

        except Exception as e:
            Logger.warning(f"{self.name}: error in RPC '{name}': {e}")
            return {"status": False, "response": None}

    # ------------------------------------------------------------------
    # Continuous recognition control
    # ------------------------------------------------------------------
    def _enable_continuous_mode(self, enable: bool) -> None:
        if not enable:
            # stop loop
            self._cont_recog_stop_event.set()

            # best-effort join
            if self._cont_recog_thread and self._cont_recog_thread.is_alive():
                self._cont_recog_thread.join(timeout=2.0)

            self._cont_recog_thread = None

            # give backend a chance to cancel any in-flight recognition
            try:
                self.cancel({})
            except Exception as e:
                Logger.debug(f"ASR {self.name}: cancel() during disable failed: {e}")

            return

        # already running
        if self._cont_recog_thread and self._cont_recog_thread.is_alive():
            return

        self._cont_recog_stop_event.clear()
        self._cont_recog_thread = threading.Thread(
            target=self._continuous_recog_loop,
            name=f"{self.name}-continuous-recog",
            daemon=True,
        )
        self._cont_recog_thread.start()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def terminate(self, timeout: float | None = None) -> None:
        """Stop continuous mode, close streams, then terminate ServerNode."""
        self._enable_continuous_mode(False)

        try:
            self._stream_writer.close()
        except Exception as e:
            Logger.debug(f"ASR {self.name}: error closing stream writer: {e}")

        return super().terminate(timeout)

    # ------------------------------------------------------------------
    # Abstract engine hooks (to be implemented by subclasses)
    # ------------------------------------------------------------------
    @abstractmethod
    def recognize_once(self, args: object | None = None) -> Optional[Tuple[str, str]]:
        """
        Perform a single recognition pass.

        Subclasses must implement this and return a DictFrame (or None).
        """
        pass

    @abstractmethod
    def configure(self, args: object | None = None) -> bool:
        """
        Configure the ASR backend (keys, region, languages, etc.).
        """
        pass

    @abstractmethod
    def cancel(self, args: object | None = None) -> Any:
        """
        Cancel any ongoing recognition.
        """
        pass

    # ------------------------------------------------------------------
    # Helpers for emitting events / speech frames
    # ------------------------------------------------------------------
    def on_asr_event(self, event: StringFrame | None) -> None:
        if event is None:
            return
        with self._stream_writer_lock:                         
            self._stream_writer.write(event.to_dict(), f"/{self.name}/event")

    def on_asr_speech(self, speech: DictFrame | None) -> None:        
        if speech is None:
            return
        with self._stream_writer_lock:
            self._stream_writer.write(speech.to_dict(), f"/{self.name}/speech")

    # ------------------------------------------------------------------
    # Continuous recognition loop
    # ------------------------------------------------------------------
    def _continuous_recog_loop(self) -> None:
        while not self._cont_recog_stop_event.is_set():
            try:
                with self._asr_engine_lock:
                    lang, speech = self.recognize_once({'timeout': 3.0})
                if speech is not None :
                    frame = DictFrame(value={ "language": lang, "text": speech })
                    self.on_asr_speech(frame)
            except Exception as e:
                Logger.warning(f"ASR {self.name}: continuous loop error: {e}")
                # optional: small backoff to avoid tight error loop
                time.sleep(1.0)
