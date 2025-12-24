from __future__ import annotations

from typing import Any, Dict, List, Type

from .api_core import QTROBOT_CORE_APIS
from .api_plugins import QTROBOT_PLUGINS_APIS

QTROBOT_APIS: Dict[str, Dict[str, Any]] = {
    # all rpc APIs from core and plugins
    "rpc": {**QTROBOT_CORE_APIS["rpc"], **QTROBOT_PLUGINS_APIS["rpc"]},

    # all stream APIs from core and plugins
    "stream": {**QTROBOT_CORE_APIS["stream"], **QTROBOT_PLUGINS_APIS["stream"]}
}
