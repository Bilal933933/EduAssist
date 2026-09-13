from app.modules.tutor_orchestrator.domain.intent import ModuleIntent

# ربط ثابت: نيات analyzer.py الـ18 → الوحدات الثلاث. بلا LLM وبلا إعادة تصنيف.
INTENT_TO_MODULE = {
    # تصحيح لغوي مباشر (نص يُصحَّح/يُراجَع/يُعرَب — لا يحتاج RAG)
    "correct": ModuleIntent.GRAMMAR_CORRECTION,
    "review": ModuleIntent.GRAMMAR_CORRECTION,
    "parse": ModuleIntent.GRAMMAR_CORRECTION,
    # محادثة خفيفة بلا مصادر
    "chitchat": ModuleIntent.CONVERSATION_PRACTICE,
    # كل ما تبقى يحتاج قاعدة المعرفة (منهج/تربية) — بما فيها الاحتياطي
    "prepare_lesson": ModuleIntent.LESSON_KNOWLEDGE,
    "explain": ModuleIntent.LESSON_KNOWLEDGE,
    "compare": ModuleIntent.LESSON_KNOWLEDGE,
    "generate_worksheet": ModuleIntent.LESSON_KNOWLEDGE,
    "generate_exercises": ModuleIntent.LESSON_KNOWLEDGE,
    "generate_quiz": ModuleIntent.LESSON_KNOWLEDGE,
    "generate_exam": ModuleIntent.LESSON_KNOWLEDGE,
    "generate_reading": ModuleIntent.LESSON_KNOWLEDGE,
    "generate_discussion": ModuleIntent.LESSON_KNOWLEDGE,
    "generate_visual": ModuleIntent.LESSON_KNOWLEDGE,
    "generate_revision": ModuleIntent.LESSON_KNOWLEDGE,
    "activity": ModuleIntent.LESSON_KNOWLEDGE,
    "pedagogical_advice": ModuleIntent.LESSON_KNOWLEDGE,
    "general_question": ModuleIntent.LESSON_KNOWLEDGE,
}

# الاحتياطي الآمن الدائم: أي نية غير معروفة (حالية أو مستقبلية) تذهب لمسار
# المصادر — لأنه الوحيد المحمي من الهلوسة عبر validator.
_SAFE_FALLBACK = ModuleIntent.LESSON_KNOWLEDGE


def map_intent(intent) -> ModuleIntent:
    """نية analyzer (نص) ← وحدة. غير المعروف/الفارغ ← LESSON_KNOWLEDGE دائماً."""
    return INTENT_TO_MODULE.get(intent, _SAFE_FALLBACK)
