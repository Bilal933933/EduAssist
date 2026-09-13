import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')

from unittest.mock import MagicMock, patch

from app.modules.conversation.application import continue_conversation_use_case as uc
from app.modules.conversation.application.conversation_prompts import (
    CONVERSATION_SYSTEM,
)


class FakeStore:
    def __init__(self, messages):
        self._messages = messages

    def get_messages(self, thread_id):
        return self._messages


class FakeSummaryRepo:
    def __init__(self):
        self.state = {"summary": "", "summarized_upto_msg_id": 0}
        self.saves = []

    def get(self, thread_id):
        return dict(self.state)

    def save(self, thread_id, summary, upto_msg_id):
        self.state = {"summary": summary, "summarized_upto_msg_id": upto_msg_id}
        self.saves.append((thread_id, summary, upto_msg_id))


def _msgs(n):
    return [
        {"id": i + 1, "role": "user" if i % 2 == 0 else "assistant", "content": f"ر{i + 1}"}
        for i in range(n)
    ]


def test_context_order_memory_summary_history():
    ctx = uc.build_conversation_context(
        "ملخص", [("user", "مرحبا")], "[ذاكرة]"
    )
    assert ctx.index("[ذاكرة]") < ctx.index("ملخص") < ctx.index("مرحبا")


def test_continue_uses_shared_client_and_prompt():
    with patch.object(uc, "call_simple", return_value="أهلاً") as mocked:
        answer = uc.continue_conversation("cli", "كيف حالك؟", [("user", "مرحبا")], "ملخص", "[ذاكرة]")
        assert answer == "أهلاً"
        user_text, system = mocked.call_args[0][1], mocked.call_args[0][2]
        assert system == CONVERSATION_SYSTEM
        assert "كيف حالك؟" in user_text and "ملخص" in user_text and "مرحبا" in user_text


def test_short_thread_no_summary_cost():
    repo = FakeSummaryRepo()
    with patch.object(uc, "call_simple") as mocked:
        uc.maybe_update_summary("cli", repo, FakeStore(_msgs(8)), thread_id=1)
        mocked.assert_not_called()
    assert repo.saves == []


def test_overflow_summarized_once_then_idempotent():
    repo = FakeSummaryRepo()
    store = FakeStore(_msgs(10))
    with patch.object(uc, "call_simple", return_value="ملخص1") as mocked:
        uc.maybe_update_summary("cli", repo, store, thread_id=1)
        assert mocked.call_count == 1
        assert repo.state == {"summary": "ملخص1", "summarized_upto_msg_id": 2}
        # نفس الحالة مجدداً: لا استدعاء ثانٍ (summarized_upto يمنع التكرار)
        uc.maybe_update_summary("cli", repo, store, thread_id=1)
        assert mocked.call_count == 1


def test_summary_accumulates_previous():
    repo = FakeSummaryRepo()
    repo.state = {"summary": "قديم", "summarized_upto_msg_id": 2}
    store = FakeStore(_msgs(12))
    with patch.object(uc, "call_simple", return_value="جديد") as mocked:
        uc.maybe_update_summary("cli", repo, store, thread_id=1)
        prompt = mocked.call_args[0][1]
        assert "قديم" in prompt  # الملخص السابق داخل مدخلات التلخيص
        assert repo.state["summarized_upto_msg_id"] == 4


class FakeChatStore:
    def __init__(self):
        self.saved = []

    def recent_history(self, thread_id):
        return []

    def add_message(self, thread_id, role, content, sources=None):
        self.saved.append((role, content))


def test_summary_failure_does_not_break_conversation():
    """تدهور رشيق: فشل التلخيص (429 مثلاً) لا يوقف الرد الأساسي."""
    from app.modules.chat import service as svc

    store = FakeChatStore()
    with patch.object(svc, "maybe_update_summary", side_effect=RuntimeError("429")), \
        patch.object(svc, "continue_conversation", return_value="أهلاً بك"), \
        patch.object(svc, "get_summary_repo") as repo_factory, \
        patch("src.storage.teacher_memory.TeacherMemoryStore"):
        repo_factory.return_value.get.return_value = {
            "summary": "", "summarized_upto_msg_id": 0,
        }
        answer, tid = asyncio.run(
            svc.ChatService()._run_conversation("مرحبا", 1, MagicMock(), store)
        )
        assert answer == "أهلاً بك"
        assert tid == 1
        assert ("user", "مرحبا") in store.saved


def test_result_contract_matches_lesson_shape():
    result = uc.build_conversation_result("أهلاً بك", thread_id=5)
    assert result == {
        "answer": "أهلاً بك",
        "hits": [],
        "trace": [{"tool": "conversation"}],
        "thread_id": 5,
    }
