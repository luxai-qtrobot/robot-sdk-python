#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from luxai.robot.core.config import QTROBOT_CORE_APIS


# Adjust this to your project layout if needed
ROOT = Path(__file__).resolve().parents[1]  # project root
CLIENT_PYI = ROOT / "src" / "luxai" / "robot" / "core" / "client.pyi"
CLIENT_BASE_PYI = ROOT / "src" / "luxai" / "robot" / "core" / "client_base.pyi"
ROBOT_NS_MARKER = "# --- AUTO-GENERATED ROBOT NAMESPACES ---"


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


def _stream_class_name(ns_name: str) -> str:
    """Stream namespace class name (e.g. 'SpeechStreamAPI')."""
    return f"{ns_name.capitalize()}StreamAPI"


def generate_client_stub() -> str:
    """
    Generate client.pyi by:
      - starting from client_base.pyi (manual Robot core methods)
      - inserting Robot namespace properties at ROBOT_NS_MARKER
      - appending auto-generated *API classes
    """
    base = CLIENT_BASE_PYI.read_text(encoding="utf-8")
    if ROBOT_NS_MARKER not in base:
        raise RuntimeError(f"Marker '{ROBOT_NS_MARKER}' not found in {CLIENT_BASE_PYI}")

    rpc_specs: Dict[str, Dict[str, Any]] = QTROBOT_CORE_APIS.get("rpc", {})
    stream_specs: Dict[str, Dict[str, Any]] = QTROBOT_CORE_APIS.get("stream", {})

    # namespaces[ns_name] = {
    #   "rpc":    List[(method_name, spec, api_id)],
    #   "stream": List[(local_name, spec, api_id)],
    # }
    namespaces: Dict[str, Dict[str, List[Tuple[str, Dict[str, Any], str]]]] = {}

    # Group RPC APIs by namespace
    for api_id, spec in rpc_specs.items():
        try:
            ns_name, method_name = api_id.split(".", 1)
        except ValueError:
            raise ValueError(
                f"Invalid RPC API name '{api_id}': expected 'namespace.method' format"
            )
        ns_entry = namespaces.setdefault(ns_name, {"rpc": [], "stream": []})
        ns_entry["rpc"].append((method_name, spec, api_id))

    # Group stream APIs by namespace
    for api_id, spec in stream_specs.items():
        try:
            ns_name, local_name = api_id.split(".", 1)
        except ValueError:
            raise ValueError(
                f"Invalid stream API name '{api_id}': expected 'namespace.name' format"
            )
        ns_entry = namespaces.setdefault(ns_name, {"rpc": [], "stream": []})
        ns_entry["stream"].append((local_name, spec, api_id))

    # ---------------------------------------------------------------------
    # Build Robot namespace properties
    # ---------------------------------------------------------------------
    robot_ns_lines: List[str] = []
    robot_ns_lines.append(ROBOT_NS_MARKER)
    robot_ns_lines.append("")

    for ns_name in sorted(namespaces.keys()):
        api_class = _namespace_class_name(ns_name)
        robot_ns_lines.append("    @property")
        robot_ns_lines.append(f"    def {ns_name}(self) -> {api_class}:")
        robot_ns_lines.append(f'        """Namespace view for {ns_name} APIs."""')
        robot_ns_lines.append("        ...")
        robot_ns_lines.append("")

    robot_ns_block = "\n".join(robot_ns_lines)

    # Replace marker in base with the expanded block
    content = base.replace(ROBOT_NS_MARKER, robot_ns_block)

    # ---------------------------------------------------------------------
    # Build namespace API classes (AudioAPI, SpeechAPI, ...)
    # ---------------------------------------------------------------------
    api_lines: List[str] = []
    api_lines.append("")
    api_lines.append("")

    for ns_name in sorted(namespaces.keys()):
        ns_entry = namespaces[ns_name]
        rpc_list = ns_entry["rpc"]
        stream_list = ns_entry["stream"]

        api_class = _namespace_class_name(ns_name)
        stream_class = _stream_class_name(ns_name)

        # ----- Stream class first (if any streams) -----
        if stream_list:
            api_lines.append(f"class {stream_class}:")
            api_lines.append(f'    """Stream APIs for {ns_name} namespace."""')
            api_lines.append("")

            for local_name, spec, api_id in stream_list:
                topic = spec.get("topic", "")
                direction = spec.get("direction")
                doc = spec.get("doc") or f"Auto-generated stream API for topic {topic!r}."
                frame_type_name = spec.get("frame_type", "Frame")
                # robot -> SDK: reader + callback
                if direction in ("out", None):
                    api_lines.append(
                        f"    def open_{local_name}_reader("
                        "self, queue_size: int | None = ..."
                        f") -> TypedStreamReader[{frame_type_name}]:"
                    )
                    api_lines.append(
                        f'        """Open a reader for stream topic {topic!r}. (API: {api_id})"""'
                    )
                    api_lines.append("        ...")
                    api_lines.append("")

                    api_lines.append(
                        f"    def on_{local_name}("
                        f"self, callback: Callable[[{frame_type_name}], None], queue_size: int | None = ..."
                        ") -> StreamSubscription:"
                    )
                    api_lines.append(
                        f'        """Attach a callback to stream topic {topic!r}. (API: {api_id})"""'
                    )
                    api_lines.append("        ...")
                    api_lines.append("")

                # SDK -> robot: writer
                if direction in ("in", None):
                    api_lines.append(
                        f"    def open_{local_name}_writer("
                        "self, queue_size: int | None = ..."
                        ") -> StreamWriter:"
                    )
                    api_lines.append(
                        f'        """Open a writer for stream topic {topic!r}. (API: {api_id})"""'
                    )
                    api_lines.append("        ...")
                    api_lines.append("")

            api_lines.append("")

        # ----- RPC + stream-property class -----
        api_lines.append(f"class {api_class}:")
        api_lines.append(f'    """Namespace for {ns_name} RPC/stream APIs."""')
        api_lines.append("")

        for method_name, spec, api_id in rpc_list:
            param_entries = spec.get("params", [])
            rendered_params = [_render_param(e) for e in param_entries]
            rendered_params.append("blocking: bool = True")
            params_str = ", ".join(["self"] + rendered_params)

            doc = spec.get("doc") or f"Auto-generated API for service {spec['service_name']}."
            api_lines.append(f"    def {method_name}({params_str}) -> ActionHandle:")
            api_lines.append(f'        """{doc} (API: {api_id})"""')
            api_lines.append("        ...")
            api_lines.append("")

        if stream_list:
            api_lines.append("    @property")
            api_lines.append(f"    def stream(self) -> {stream_class}:")
            api_lines.append(f'        """Stream namespace for {ns_name} APIs."""')
            api_lines.append("        ...")
            api_lines.append("")

        api_lines.append("")

    content += "\n".join(api_lines)
    return content


def main() -> None:
    CLIENT_PYI.parent.mkdir(parents=True, exist_ok=True)
    content = generate_client_stub()
    CLIENT_PYI.write_text(content, encoding="utf-8")
    print(f"Wrote stub: {CLIENT_PYI}")


if __name__ == "__main__":
    main()
