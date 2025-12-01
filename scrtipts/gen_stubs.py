#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from luxai.robot.core.config import QTROBOT_CORE_APIS


# Adjust this to your project layout if needed
ROOT = Path(__file__).resolve().parents[1]  # project root
CLIENT_PYI = ROOT / "src" / "luxai" / "robot" / "core" / "client.pyi"


def _render_type(t: Any) -> str:
    """Map Python types used in IDL to string annotations for the stub."""
    if t is str:
        return "str"
    if t is int:
        return "int"
    if t is float:
        return "float"
    if t is bool:
        return "bool"
    if t is type(None):
        return "None"
    # Fallback: use type name
    return getattr(t, "__name__", "Any")


def _render_param(entry: tuple) -> str:
    """
    Render a single parameter from IDL entry:
        ("name", type) or ("name", type, default)
    """
    if len(entry) == 2:
        name, typ = entry
        default_str = ""
    else:
        name, typ, default = entry
        if default is None:
            typ_str = f"{_render_type(typ)} | None"
            return f"{name}: {typ_str} = None"
        else:
            default_str = " = ..."
    typ_str = _render_type(typ)
    return f"{name}: {typ_str}{default_str}"


def _namespace_class_name(ns_name: str) -> str:
    """Convert namespace name (e.g. 'speech') to a stub class name (e.g. 'SpeechAPI')."""
    return f"{ns_name.capitalize()}API"


def generate_client_stub() -> str:
    """
    Generate the full text of client.pyi based on QTROBOT_CORE_APIS.

    We create:
      - One namespace class per group (SpeechAPI, EmotionAPI, ...)
      - Robot class with properties:
            @property
            def speech(self) -> SpeechAPI: ...
    """

    lines: List[str] = []

    # Header imports
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("from typing import Any")
    lines.append("from luxai.robot.core.actions import ActionHandle")
    lines.append("")
    lines.append("")

    # Group APIs by namespace: "speech.say" -> ns='speech', method='say'
    namespaces: Dict[str, List[Tuple[str, Dict[str, Any], str]]] = {}
    for api_name, spec in QTROBOT_CORE_APIS.items():
        try:
            ns_name, method_name = api_name.split(".", 1)
        except ValueError:
            raise ValueError(
                f"Invalid API name '{api_name}': expected 'namespace.method' format"
            )
        namespaces.setdefault(ns_name, []).append((method_name, spec, api_name))

    # ---------------------------------------------------------------------
    # Namespace classes (SpeechAPI, EmotionAPI, GestureAPI, ...)
    # ---------------------------------------------------------------------
    for ns_name in sorted(namespaces.keys()):
        class_name = _namespace_class_name(ns_name)
        lines.append(f"class {class_name}:")
        lines.append(f'    """Namespace for {ns_name} APIs."""')
        lines.append("")

        for method_name, spec, api_name in namespaces[ns_name]:
            # Parameters from IDL
            param_entries = spec.get("params", [])
            rendered_params = [_render_param(e) for e in param_entries]

            # Blocking flag at the end (keyword-only in real code, but fine here)
            rendered_params.append("blocking: bool = True")

            params_str = ", ".join(["self"] + rendered_params)

            doc = spec.get("doc") or f"Auto-generated API for service {spec['service_name']}."
            lines.append(f"    def {method_name}({params_str}) -> ActionHandle:")
            lines.append(f'        """{doc} (API: {api_name})"""')
            lines.append("        ...")
            lines.append("")

        lines.append("")  # blank line after class

    # ---------------------------------------------------------------------
    # Robot class with namespace properties
    # ---------------------------------------------------------------------
    lines.append("class Robot:")
    lines.append('    """Type stub for Robot client (auto-generated from IDL)."""')
    lines.append("")

    # Expose each namespace as a property returning the corresponding class
    for ns_name in sorted(namespaces.keys()):
        class_name = _namespace_class_name(ns_name)
        lines.append("    @property")
        lines.append(f"    def {ns_name}(self) -> {class_name}:")
        lines.append(f'        """Namespace view for {ns_name} APIs."""')
        lines.append("        ...")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    CLIENT_PYI.parent.mkdir(parents=True, exist_ok=True)
    content = generate_client_stub()
    CLIENT_PYI.write_text(content, encoding="utf-8")
    print(f"Wrote stub: {CLIENT_PYI}")


if __name__ == "__main__":
    main()
