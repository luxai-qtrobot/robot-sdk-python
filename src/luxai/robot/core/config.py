# src/luxai/robot/core/config.py
from __future__ import annotations

from .. import __version__ as SDK_VERSION

from .idl.api import QTROBOT_APIS

# Service used for system/robot description
SYSTEM_DESCRIBE_SERVICE = "/robot/system/describe"

__all__ = [
    "SDK_VERSION",
    "QTROBOT_APIS",
    "SYSTEM_DESCRIBE_SERVICE",
]
