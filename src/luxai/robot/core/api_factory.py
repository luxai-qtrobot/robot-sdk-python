# src/luxai/robot/core/api_factory.py
from __future__ import annotations

import inspect
from typing import Any, Dict

from luxai.magpie.utils.logger import Logger
from .actions import ActionHandle, ActionError


def create_api_method(method_name: str, spec: Dict[str, Any]):
    """
    Create a Robot instance method from an IDL spec.

    Spec keys:
        - service_name: str
        - cancel_service_name: Optional[str]
        - params: List[(name, type) or (name, type, default)]
        - since: Optional[str]
        - deprecated: bool
        - deprecated_message: Optional[str]
        - robots: Optional[List[str]]
        - doc: Optional[str]
    """

    service_name: str = spec["service_name"]
    cancel_service_name: str | None = spec.get("cancel_service_name")
    api_robots = spec.get("robots")  # e.g. ["qtrobot-v1", "qtrobot-sim"]
    deprecated_flag: bool = bool(spec.get("deprecated", False))
    deprecated_message: str | None = spec.get("deprecated_message")

    # Build signature: (self, <params...>, *, blocking=False)
    params = [
        inspect.Parameter(
            "self",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]

    for entry in spec.get("params", []):
        if len(entry) == 2:
            pname, ptype = entry
            default = inspect.Parameter.empty
        else:
            pname, ptype, default = entry
        params.append(
            inspect.Parameter(
                pname,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=ptype,
            )
        )

    params.append(
        inspect.Parameter(
            "blocking",
            inspect.Parameter.KEYWORD_ONLY,
            default=True,
            annotation=bool,
        )
    )

    signature = inspect.Signature(params)

    def api_func(*args, **kwargs) -> ActionHandle:
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        self = bound.arguments["self"]
        blocking: bool = bound.arguments["blocking"]

        # ---- Compatibility check: robot capabilities + IDL robots ----
        robot_type = getattr(self, "_robot_type", None)
        supported_apis = getattr(self, "_supported_apis", None)
        deprecated_apis = getattr(self, "_deprecated_apis", None)

        # 1) If robot reported supported_apis and this API is not in it → unsupported
        if supported_apis is not None and method_name not in supported_apis:
            raise ActionError(
                f"API '{method_name}' is not supported by this robot "
                f"(type={robot_type!r})."
            )

        # 2) If IDL says this API is limited to certain robot types → enforce
        if api_robots and robot_type and robot_type not in api_robots:
            raise ActionError(
                f"API '{method_name}' is not supported for robot type {robot_type!r}."
            )

        # 3) Deprecation warnings (static + robot-reported)
        is_deprecated = deprecated_flag or (
            deprecated_apis is not None and method_name in deprecated_apis
        )
        if is_deprecated:
            msg = (
                deprecated_message
                or f"API '{method_name}' is deprecated and may be removed in future versions."
            )
            Logger.warning(f"Robot: {msg}")

        # Build RPC args: skip self and blocking; skip None values
        rpc_args: Dict[str, Any] = {}
        for name, value in bound.arguments.items():
            if name in ("self", "blocking"):
                continue
            if value is None:
                continue
            rpc_args[name] = value

        # Delegate to Robot._start_action
        return self._start_action(
            service_name=service_name,
            args=rpc_args,
            cancel_service_name=cancel_service_name,
            timeout=None,  # internal default timeout inside Robot
            blocking=blocking,
        )

    api_func.__name__ = method_name
    api_func.__qualname__ = f"Robot.{method_name}"
    api_func.__signature__ = signature

    doc = spec.get("doc") or f"Auto-generated API for service {service_name}."
    api_func.__doc__ = doc

    return api_func


def attach_core_apis(QTrobot_cls, api_specs: Dict[str, Dict[str, Any]]) -> None:
    for method_name, spec in api_specs.items():
        func = create_api_method(method_name, spec)
        setattr(QTrobot_cls, method_name, func)
