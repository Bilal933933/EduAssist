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
    "correct", "review",
}

DEEP_INTENTS = {
    "prepare_lesson", "compare", "pedagogical_advice",
    "generate_worksheet", "generate_exercises", "generate_quiz",
    "generate_exam", "generate_reading", "generate_discussion",
    "generate_visual", "generate_revision", "activity",
}

# طلب شامل (كل/جميع/بالتفصيل) يحتاج تفكيكاً ونقداً — لا يكفيه بحث واحد خفيف.
_COMPREHENSIVE_MARKERS = (
    "كل أحكام", "كل احكام", "بكل", "جميع", "كاملة", "بالتفصيل",
    "أخبرني بكل", "اخبرني بكل", "جميع أحكام", "جميع احكام",
)


def is_comprehensive(question: str = "") -> bool:
    q = question or ""
    return any(m in q for m in _COMPREHENSIVE_MARKERS)

CHITCHAT_REPLIES = {
    "مرحبا": "أهلاً بك يا زميلي الفاضل! أنا مساعدك لتحضير دروس اللغة العربية. اذكر لي الدرس والصف (مثال: حضر لي درس الفاعل)، أو أعطني جملة لأعربها لك.",
    "سلام": "وعليكم السلام ورحمة الله! كيف أخدمك في تحضير دروس العربية اليوم؟",
    "شكرا": "العفو يا زميلي! بالتوفيق في حصتك. هل تحتاج شيئاً آخر؟",
    "من أنت": "أنا مساعد المدرس الذكي للغة العربية: أحضّر الدروس وأعرب الجمل وأبني أوراق العمل من مصادرك المعتمدة.",
}


def route(analysis, question: str = "") -> str:
    """يحدد المسار من نية التحليل. مخرج: direct | light | deep."""
    intent = getattr(analysis, "intent", None) or "general_question"
    if intent in DIRECT_INTENTS:
        return "direct"
    if intent in LIGHT_INTENTS:
        # الطلب الشامل (كل الأحكام) يتجاوز light إلى deep ولو كانت نيته explain.
        if intent in ("explain", "general_question") and is_comprehensive(question):
            return "deep"
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
