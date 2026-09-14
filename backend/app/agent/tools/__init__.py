import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agent.tools.registry import TOOL_DECLARATIONS, execute_tool, ALLOWED_ROOTS

try:
    from app.agent.tools.searchChunks.tool import format_search_observation
except Exception:
    def format_search_observation(hits, max_hits=8, max_chars=600):
        return "لا توجد نتائج بحث."

try:
    from app.agent.tools.readFile.tool import _smart_read, _resolve_safe_path
except Exception:
    def _smart_read(*args, **kwargs):
        return ""
    def _resolve_safe_path(*args, **kwargs):
        raise FileNotFoundError("not found")

__all__ = ["TOOL_DECLARATIONS", "execute_tool", "format_search_observation", "_smart_read", "_resolve_safe_path", "ALLOWED_ROOTS"]
