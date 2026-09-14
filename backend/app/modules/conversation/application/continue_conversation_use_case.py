"""محادثة حرة بسياق الجلسة — تجميع (ملخص + حديث + نبرة) ثم استدعاء توليد واحد.

قراءة فقط على teacher_memory (لا كتابة من هنا).
"""

from app.modules.lesson_knowledge.application.agent.fc_client import call_simple
from src.storage.chat_store import MAX_CONTEXT_MESSAGES

from app.modules.conversation.application.conversation_prompts import (
    CONVERSATION_SYSTEM,
    SUMMARY_SYSTEM,
)


def build_conversation_context(summary: str, history: list, memory_block: str) -> str:
    """يركّب سياقاً نصياً واحداً من المكونات الثلاثة — بلا أي استدعاء."""
    parts = []
    if memory_block:
        parts.append(memory_block)
    if summary:
        parts.append("[ملخص ما سبق من المحادثة]\n" + summary)
    if history:
        turns = "\n".join(
            f"{'المدرس' if role == 'user' else 'المساعد'}: {text}"
            for role, text in history
        )
        parts.append("[آخر الرسائل]\n" + turns)
    return "\n\n".join(parts)


def continue_conversation(
    client, question: str, history: list, summary: str = "", memory_block: str = ""
) -> str:
    """يولّد رد المحادثة عبر استدعاء واحد — بلا RAG."""
    context = build_conversation_context(summary, history, memory_block)
    user = f"{context}\n\n[رسالة المدرس الجديدة]\n{question}" if context else question
    return call_simple(client, user, CONVERSATION_SYSTEM)


def maybe_update_summary(client, summary_repo, store, thread_id: int) -> None:
    """يحدّث الملخص التراكمي فقط لما تجاوز نافذة السياق المباشر.

    العتبة هي MAX_CONTEXT_MESSAGES نفسها (مصدر حقيقة واحد مع recent_history) —
    لا رقم ثانٍ. المحادثات القصيرة: صفر تكلفة إضافية.
    """
    messages = store.get_messages(thread_id)
    if len(messages) <= MAX_CONTEXT_MESSAGES:
        return
    state = summary_repo.get(thread_id)
    overflow = [
        m
        for m in messages[: len(messages) - MAX_CONTEXT_MESSAGES]
        if m["id"] > state["summarized_upto_msg_id"]
    ]
    if not overflow:
        return
    turns = "\n".join(
        f"{'المدرس' if m['role'] == 'user' else 'المساعد'}: {m['content']}"
        for m in overflow
    )
    previous = f"الملخص السابق:\n{state['summary']}\n\n" if state["summary"] else ""
    new_summary = call_simple(
        client, f"{previous}رسائل جديدة للتلخيص:\n{turns}", SUMMARY_SYSTEM
    )
    summary_repo.save(thread_id, new_summary, overflow[-1]["id"])


def build_conversation_result(answer: str, thread_id) -> dict:
    """عقد استجابة مطابق لعقد الدروس حرفياً — بلا مصادر (hits فارغة)."""
    return {
        "answer": answer,
        "hits": [],
        "trace": [{"tool": "conversation"}],
        "thread_id": thread_id,
    }
