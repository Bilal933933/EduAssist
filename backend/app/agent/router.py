"""موجه الأسئلة: يقرأ نية السؤال أولاً ويحدد المسار قبل أي استرجاع.

- direct: تحية/شكر/تعريف — رد فوري بلا بحث في المصادر.
- light: إعراب/شرح/سؤال واحد — بحث واحد خفيف ثم توليد واحد،
  مع إجابة احتياطية من معرفة النموذج عند غياب الأدلة.
- deep: تحضير/توليد/مقارنة — الحلقة الوكيلة الكاملة.
"""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DIRECT_INTENTS = {"chitchat"}

LIGHT_INTENTS = {
    "parse", "explain", "general_question",
    "correct", "review", "pedagogical_advice",
}

DEEP_INTENTS = {
    "prepare_lesson", "compare",
    "generate_worksheet", "generate_exercises", "generate_quiz",
    "generate_exam", "generate_reading", "generate_discussion",
    "generate_visual", "generate_revision", "activity",
}

CHITCHAT_REPLIES = {
    "مرحبا": "أهلاً بك يا زميلي الفاضل! أنا مساعدك لتحضير دروس اللغة العربية. اذكر لي الدرس والصف (مثال: حضر لي درس الفاعل)، أو أعطني جملة لأعربها لك.",
    "سلام": "وعليكم السلام ورحمة الله! كيف أخدمك في تحضير دروس العربية اليوم؟",
    "شكرا": "العفو يا زميلي! بالتوفيق في حصتك. هل تحتاج شيئاً آخر؟",
    "من أنت": "أنا مساعد المدرس الذكي للغة العربية: أحضّر الدروس وأعرب الجمل وأبني أوراق العمل من مصادرك المعتمدة.",
}


def route(analysis) -> str:
    """يحدد المسار من نية التحليل. مخرج: direct | light | deep."""
    intent = getattr(analysis, "intent", None) or "general_question"
    if intent in DIRECT_INTENTS:
        return "direct"
    if intent in LIGHT_INTENTS:
        return "light"
    return "deep"


def get_chitchat_reply(question: str) -> str | None:
    """رد ثابت فوري للتحيات الشائعة، أو None لتركها للنموذج."""
    q = (question or "").strip()
    for key, reply in CHITCHAT_REPLIES.items():
        if key in q:
            return reply
    if len(q) <= 20:
        return "أهلاً بك! كيف أساعدك في دروس اللغة العربية اليوم؟"
    return None
