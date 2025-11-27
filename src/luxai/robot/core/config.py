# src/luxai/robot/core/config.py
from __future__ import annotations

from typing import Any, Dict, List, Type

from .. import __version__ as SDK_VERSION

from .api_list import QTROBOT_CORE_APIS

# Service used for system/robot description
SYSTEM_DESCRIBE_SERVICE = "/robot/system/describe"

__all__ = [
    "SDK_VERSION",
    "QTROBOT_CORE_APIS",
    "SYSTEM_DESCRIBE_SERVICE",
]
