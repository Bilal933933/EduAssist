import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.query_analyzer.analyzer import analyze, is_ambiguous
from app.query_analyzer.llm_classifier import _parse_result
from app.modules.chat.service import _resolve


def test_explicit_stays_rule_based():
    a = analyze("حضر لي درس الفاعل - الصف الخامس")
    assert a.intent == "prepare_lesson"
    assert is_ambiguous(a, "حضر لي درس الفاعل - الصف الخامس") is False


def test_vague_is_ambiguous():
    a = analyze("جهزلي حصة للعيال")
    assert is_ambiguous(a, "جهزلي حصة للعيال") is True


def test_competing_signals_is_ambiguous():
    q = "أعرب الجملة ثم حضر درس الفاعل"
    a = analyze(q)
    assert is_ambiguous(a, q) is True


def test_parse_result_rejects_unknown():
    intent, conf = _parse_result('{"intent": "نية_مخترعة", "confidence": 0.99}')
    assert intent is None


def test_resolve_without_client_preserves_old_behavior():
    analysis, module, mode = _resolve("حضر لي درس الفاعل - الصف الخامس", {})
    assert analysis.intent == "prepare_lesson"
    assert mode == "deep"


def test_resolve_with_failing_llm_falls_back():
    class FailingClient:
        pass
    # مصنف وهمي يفشل — يجب البقاء على القاعدة
    analysis, module, mode = _resolve("جهزلي حصة للعيال", {}, client=FailingClient())
    assert analysis.intent in ("general_question", "chitchat", "prepare_lesson", "explain")
