"""مصنف النية المقيد — الطبقة الثانية في الهجين.

القاعدة: القواعد أولاً للحالات الصريحة، وهذا المصنف فقط عند الغموض.
المخرج مقيد بقائمة INTENTS الـ18 — أي نية خارجها مرفوضة.
"""
import re
import sys

from arabic_text import parse_json_block

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.query_analyzer.analyzer import INTENTS

CLASSIFIER_SYSTEM = """أنت مصنف نية أسئلة مدرس اللغة العربية.
اختر نية واحدة فقط من هذه القائمة المغلقة (لا تخترع غيرها):
chitchat, prepare_lesson, explain, compare, parse, generate_worksheet, generate_exercises, generate_quiz, generate_exam, generate_reading, generate_discussion, generate_visual, generate_revision, correct, review, activity, pedagogical_advice, general_question

تعريفات مختصرة:
- chitchat: تحية/شكر/تعريف بلا طلب تعليمي.
- prepare_lesson: طلب تحضير درس/خطة/سير حصة.
- parse: طلب إعراب جملة محددة.
- explain: شرح قاعدة أو مفهوم.
- compare: الفرق بين مفهومين.
- generate_*: طلب توليد (ورقة عمل/تدريبات/اختبار/امتحان/قراءة/مناقشة/وسيلة بصرية/مراجعة).
- correct/review: تصحيح أو مراجعة نص.
- pedagogical_advice: كيف أشرح/أبسط/أعالج خطأ شائع.
- activity: نشاط صفي تفاعلي.
- general_question: سؤال عام غير مصنف.

أجب JSON فقط: {"intent": "<واحدة من القائمة>", "confidence": 0.0-1.0}"""

_CONFIDENCE_RE = re.compile(r"0?\.\d+|1\.0|1|0")


def _parse_result(raw: str) -> tuple[str | None, float]:
    """يستخرج (نية، ثقة) من نص النموذج — يعيد (None, 0.0) عند الفشل."""
    if not raw:
        return None, 0.0
    data = parse_json_block(raw)
    if not data:
        return None, 0.0
    intent = data.get("intent")
    if intent not in INTENTS:
        return None, 0.0
    try:
        conf = float(data.get("confidence", 0.0))
    except (TypeError, ValueError):
        conf = 0.0
    conf = min(1.0, max(0.0, conf))
    return intent, conf


def classify_intent_llm(client, question: str, context: dict | None = None) -> tuple[str | None, float]:
    """يصنف النية عبر النموذج — مقيد بالـ18. فشله آمن (None, 0.0)."""
    from app.agent.fc_client import call_simple

    ctx = context or {}
    ctx_line = ""
    if ctx.get("topic") or ctx.get("intent"):
        ctx_line = f"\nالسياق السابق: الموضوع={ctx.get('topic') or '-'} | النية السابقة={ctx.get('intent') or '-'}"
    user = f"سؤال المدرس: {question}{ctx_line}\nأجب JSON فقط."
    try:
        raw = call_simple(client, user, CLASSIFIER_SYSTEM)
    except Exception:
        return None, 0.0
    return _parse_result(raw)
