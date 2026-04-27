
from __future__ import annotations
from typing import Dict, Type, Optional

# src/luxai/robot/core/__init__.py
from .robot_plugin import RobotPlugin

# define a global plugin registry
PLUGIN_REGISTRY: Dict[str, Optional[Type[RobotPlugin]]] = {}


# Try to import optional plugins and register them.
# Each one is guarded by try/except so missing extras never break the SDK.
try:
    # Azure ASR plugin (optional extra: luxai-robot[asr-azure])
    from .asr_azure_plugin import ASRAzurePlugin
    PLUGIN_REGISTRY["asr-azure"] = ASRAzurePlugin
except ImportError:    
    # Extension not installed -> plugin just won't be available.
    PLUGIN_REGISTRY["asr-azure"] = None    

try:
    # Riva ASR plugin (optional extra: luxai-robot[asr-riva])
    from .asr_riva_plugin import ASRRivaPlugin
    PLUGIN_REGISTRY["asr-riva"] = ASRRivaPlugin
except ImportError:
    PLUGIN_REGISTRY["asr-riva"] = None

try:
    # Groq Whisper ASR plugin (optional extra: luxai-robot[asr-groq])
    from .asr_groq_plugin import ASRGroqPlugin
    PLUGIN_REGISTRY["asr-groq"] = ASRGroqPlugin
except ImportError:
    PLUGIN_REGISTRY["asr-groq"] = None

try:
    from .remote_plugin import RealsenseDriverPlugin, HumanDetectorPlugin
    PLUGIN_REGISTRY["realsense-driver"] = RealsenseDriverPlugin
    PLUGIN_REGISTRY["human-detector"] = HumanDetectorPlugin
except ImportError:
    PLUGIN_REGISTRY["realsense-driver"] = None
    PLUGIN_REGISTRY["human-detector"] = None

try:
    from .kinematics_plugin import KinematicsPlugin
    PLUGIN_REGISTRY["kinematics"] = KinematicsPlugin
except ImportError:
    PLUGIN_REGISTRY["kinematics"] = None



# In the future, you add more here:
# try:
#     from luxai.robot.plugins.asr.google import ASRGooglePlugin
#     PLUGIN_REGISTRY["asr-google"] = ASRGooglePlugin
# except ImportError:
#     PLUGIN_REGISTRY["asr-google"] = None    

__all__ = [
    "PLUGIN_REGISTRY",
    "RobotPlugin",
    "ASRRivaPlugin",
]
