import importlib
import json
import os

_TOOLS_DIR = os.path.dirname(__file__)

def _load_manifests():
    decls = []
    modules = {}
    for entry in os.listdir(_TOOLS_DIR):
        mdir = os.path.join(_TOOLS_DIR, entry)
        if not os.path.isdir(mdir):
            continue
        mf = os.path.join(mdir, "manifest.json")
        tool_py = os.path.join(mdir, "tool.py")
        if not (os.path.exists(mf) and os.path.exists(tool_py)):
            continue
        with open(mf, encoding="utf-8") as f:
            manifest = json.load(f)
        decls.append({
            "name": manifest["name"],
            "description": manifest["description"],
            "parameters": manifest["parameters"]
        })
        mod = importlib.import_module(f"app.agent.tools.{entry}.tool")
        modules[manifest["name"]] = mod
    return decls, modules

TOOL_DECLARATIONS, _MODULES = _load_manifests()

def execute_tool(name: str, args: dict, kb, client, inherited_scope=None):
    mod = _MODULES.get(name)
    if not mod:
        return f"أداة غير معروفة: {name}"
    return mod.execute(args, kb, client, inherited_scope)

# Re-export shared helpers for backward compat
try:
    from app.agent.tools.readFile.tool import _resolve_safe_path, _smart_read, ALLOWED_ROOTS
except Exception:
    ALLOWED_ROOTS = []
