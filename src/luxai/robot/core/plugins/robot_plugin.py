# src/luxai/robot/core/plugins.py
from __future__ import annotations

from abc import ABC, abstractmethod

class RobotPlugin(ABC):
    """
    Base class for all Robot SDK local plugins (ASR, vision modules, etc.).

    A plugin:
        - is instantiated and owned by a Robot instance
        - may start local background nodes (e.g., ASRNode using inproc://)
        - may register RPC/stream endpoints by launching local magpie nodes
        - must clean up all resources in stop()

    Subclasses MUST implement:
        - start(robot)
        - stop()
    """

    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name        

    # ---------------------------------------------------------
    @abstractmethod
    def start(self, robot: "Robot") -> None:
        """
        Called when plugin is enabled.
        Plugin should:
            - Start magpie nodes
            - Register local inproc endpoints
            - Allocate any required resources
        """
        pass

    # ---------------------------------------------------------
    @abstractmethod
    def stop(self) -> None:
        """
        Called when plugin is disabled OR when Robot.close() is called.
        Must stop threads, magpie nodes, and release resources.
        """
        pass
