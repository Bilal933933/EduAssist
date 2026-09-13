"""تصحيح نحوي/إملائي مباشر عبر LLM — بلا RAG وبلا أدوات."""

from src.agent.fc_client import call_simple

from app.modules.grammar_correction.application.grammar_prompts import (
    GRAMMAR_SYSTEM,
)


def correct_text(client, text: str) -> str:
    """يصحح النص عبر استدعاء توليد واحد. يعيد نصاً منظماً أو إقراراً بعدم وجود أخطاء."""
    return call_simple(client, text, GRAMMAR_SYSTEM)


def build_grammar_result(answer: str, thread_id) -> dict:
    """عقد استجابة مطابق لعقد الدروس حرفياً — بلا مصادر (hits فارغة)."""
    return {
        "answer": answer,
        "hits": [],
        "trace": [{"tool": "grammar_correction"}],
        "thread_id": thread_id,
    }
