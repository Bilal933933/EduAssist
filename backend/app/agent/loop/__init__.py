import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agent.loop.deep import run_agentic_rag
from app.agent.loop.stream import run_agentic_rag_stream

__all__ = ["run_agentic_rag", "run_agentic_rag_stream"]
