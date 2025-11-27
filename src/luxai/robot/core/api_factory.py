# src/luxai/robot/core/api_factory.py
from __future__ import annotations

import inspect
from typing import Any, Dict

from luxai.magpie.utils.logger import Logger
from .actions import ActionHandle, ActionError


def create_api_method(api_name: str, method_name: str, spec: Dict[str, Any]):
    """
    Create a Robot instance method from an IDL spec.

    api_name:
        Full API name from IDL, e.g. "speech.say".
        This is what we use for compatibility checks (supported_apis, deprecated_apis).

    method_name:
        The concrete Python method name attached to Robot, e.g. "say".

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

    # Build signature: (self, <params...>, *, blocking=True)
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

    # Blocking by default; user can override with blocking=False
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
        #    We use api_name here (e.g. "speech.say"), not method_name.
        if supported_apis is not None and api_name not in supported_apis:
            raise ActionError(
                f"API '{api_name}' is not supported by this robot "
                f"(type={robot_type!r})."
            )

        # 2) If IDL says this API is limited to certain robot types → enforce
        if api_robots and robot_type and robot_type not in api_robots:
            raise ActionError(
                f"API '{api_name}' is not supported for robot type {robot_type!r}."
            )

        # 3) Deprecation warnings (static + robot-reported)
        is_deprecated = deprecated_flag or (
            deprecated_apis is not None and api_name in deprecated_apis
        )
        if is_deprecated:
            msg = (
                deprecated_message
                or f"API '{api_name}' is deprecated and may be removed in future versions."
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


def attach_core_apis(Robot_cls, api_specs: Dict[str, Dict[str, Any]]) -> None:
    """
    Attach methods to Robot_cls from the given specs.

    IDL keys are expected to be "namespace.method", e.g. "speech.say".
    We:
      - create a property 'speech' on the class that simply returns self
      - create a method 'say' on the class

    So users can call both:
      robot.say(...)
      robot.speech.say(...)
    """

    created_namespaces: set[str] = set()

    for api_name, spec in api_specs.items():
        # Parse "speech.say" → ns_name = "speech", method_name = "say"
        try:
            ns_name, method_name = api_name.split(".", 1)
        except ValueError:
            raise ValueError(
                f"Invalid API name '{api_name}': expected 'namespace.method' format"
            )

        # Create namespace property only once per namespace name
        if ns_name not in created_namespaces:
            if not hasattr(Robot_cls, ns_name):
                # Simple property that just returns self.
                # This keeps the object flat but gives a nicer dot-namespace:
                #   robot.speech.say(...)
                def _ns(self, _ns_name=ns_name):
                    return self

                setattr(Robot_cls, ns_name, property(_ns))
            created_namespaces.add(ns_name)

        # Create and attach the actual bound method (e.g. Robot.say)
        func = create_api_method(api_name, method_name, spec)
        setattr(Robot_cls, method_name, func)
