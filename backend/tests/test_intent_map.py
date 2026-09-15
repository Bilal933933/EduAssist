import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.modules.tutor_orchestrator.application.intent_map import (
    INTENT_TO_MODULE,
    map_intent,
)
from app.modules.tutor_orchestrator.application.route_message_use_case import (
    resolve_module,
)
from app.modules.tutor_orchestrator.domain.intent import ModuleIntent
from app.query_analyzer.analyzer import INTENTS, analyze


def test_all_analyzer_intents_covered():
    """كل نية من الـ18 في analyzer.py لها مدخل صريح — لا نية ضائعة."""
    assert set(INTENT_TO_MODULE.keys()) == set(INTENTS)


def test_grammar_module():
    assert map_intent("correct") == ModuleIntent.GRAMMAR_CORRECTION
    assert map_intent("review") == ModuleIntent.GRAMMAR_CORRECTION
    assert map_intent("parse") == ModuleIntent.GRAMMAR_CORRECTION


def test_conversation_module():
    assert map_intent("chitchat") == ModuleIntent.CONVERSATION_PRACTICE


def test_lesson_module_intents():
    for intent in [
        "prepare_lesson", "explain", "compare", "generate_worksheet",
        "generate_exercises", "generate_quiz", "generate_exam",
        "generate_reading", "generate_discussion", "generate_visual",
        "generate_revision", "activity", "pedagogical_advice",
        "general_question",
    ]:
        assert map_intent(intent) == ModuleIntent.LESSON_KNOWLEDGE


def test_unknown_future_intent_falls_back_to_lesson():
    """نية 19 مستقبلية غير موجودة في القاموس يجب ألا تكسر النظام."""
    assert map_intent("some_future_intent_xyz") == ModuleIntent.LESSON_KNOWLEDGE
    assert map_intent("") == ModuleIntent.LESSON_KNOWLEDGE
    assert map_intent(None) == ModuleIntent.LESSON_KNOWLEDGE


def test_resolve_module_reads_analysis_object():
    analysis = analyze("حضر لي درس الفاعل - الصف الخامس")
    assert resolve_module(analysis) == ModuleIntent.LESSON_KNOWLEDGE


def test_resolve_module_missing_intent_defaults_to_lesson():
    class Empty:
        pass
    assert resolve_module(Empty()) == ModuleIntent.LESSON_KNOWLEDGE
    assert resolve_module(None) == ModuleIntent.LESSON_KNOWLEDGE


def test_review_real_message_goes_to_grammar():
    # قرار موثق: "راجع" في الاستخدام الفعلي تستهدف نصاً يُراجَع لغوياً
    # (تدقيق جملة) لا تحضير درس — لذا تبقى في وحدة التصحيح.
    # إن ظهر استخدام يعني "راجع الدرس" يُعاد النظر هنا لا في القاموس.
    analysis = analyze("راجع هذه الجملة: الطالبُ مجتهدٌ")
    assert analysis.intent == "review"
    assert resolve_module(analysis) == ModuleIntent.GRAMMAR_CORRECTION


def test_parse_real_message_goes_to_grammar():
    analysis = analyze("أعرب الجملة التالية: كتب الطالب الدرس")
    assert analysis.intent == "parse"
    assert resolve_module(analysis) == ModuleIntent.GRAMMAR_CORRECTION


def test_chitchat_real_message_goes_to_conversation():
    analysis = analyze("مرحبا")
    assert analysis.intent == "chitchat"
    assert resolve_module(analysis) == ModuleIntent.CONVERSATION_PRACTICE
