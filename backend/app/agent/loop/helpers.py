import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from app.core.logging import get_logger

logger = get_logger("agent")

LIGHT_SYSTEM = (
    "أنت معلم النحو العربي. أجب بالعربية الفصحى البسيطة بإيجاز ودقة. "
    "استعمل الأدلة المسترجعة أولاً واستشهد بها بصيغة [المصدر] عند الاعتماد عليها. "
    "إن لم تجد الجواب في الأدلة فأجب من معرفتك النحوية الموثوقة مع تنبيه واضح في أول الإجابة: "
    "(تنبيه: هذه الإجابة من معرفتي العامة لعدم ورودها في المصادر المرفقة، وتحتمل الخطأ — راجعها مع كتابك)."
)

PEDAGOGY_LIGHT_SYSTEM = (
    "أنت زميل مهني لمدرس لغة عربية (لا تخاطب طالباً). اشرح كيف يوصل القاعدة "
    "لطلاب صفه بخطوات صفية قصيرة: ابدأ بالجملة محل السؤال نفسها، فرّق بالقاعدة "
    "والعلامة (مرفوع/مجزوم)، ثم مثال مضاد واحد، ثم سؤال سريع يختبر الفهم. "
    "استعمل الأدلة المسترجعة أولاً واستشهد بها بصيغة [المصدر]، وإلا أجب من معرفتك "
    "مع التنبيه الواضح في أول الإجابة: "
    "(تنبيه: هذه الإجابة من معرفتي العامة لعدم ورودها في المصادر المرفقة، وتحتمل الخطأ — راجعها مع كتابك)."
)


def select_light_system(analysis=None, question: str = "") -> str:
    """نبرة المسار الخفيف: تربوية لأسئلة الشرح، نحوية لغيرها."""
    try:
        if getattr(analysis, "intent", None) == "pedagogical_advice":
            return PEDAGOGY_LIGHT_SYSTEM
    except Exception:
        pass
    if any(k in (question or "") for k in ["كيف أشرح", "كيف اشرح", "لهم الاجابة", "لهم الإجابة"]):
        return PEDAGOGY_LIGHT_SYSTEM
    return LIGHT_SYSTEM

QUOTA_FALLBACK = (
    "تعذّر الوصول إلى نموذج الإجابة حالياً بسبب ضغط مؤقت على الحصة المجانية (429). "
    "سؤالك محفوظ — انتظر دقيقة ثم اضغط Retry وسأجيبك فوراً."
)


def _load_memory_block(teacher_id: str = "default", current_grade: str | None = None, current_topic: str | None = None) -> str:
    """يحمّل كتلة ذاكرة المدرس مربوطة بالصف/الموضوع الحالي."""
    try:
        from app.storage.teacher_memory import TeacherMemoryStore
        return TeacherMemoryStore().get_prompt_block(
            teacher_id, current_grade=current_grade, current_topic=current_topic
        )
    except Exception as e:
        print(f"[Memory skip: {e}]")
        return ""


def _ev_tag(h: dict) -> str:
    """ترويسة دليل مشروطة: بلا 'صNone' عند غياب الصفحة."""
    src = h.get("source") or "مصدر"
    page = h.get("page")
    return f"[{src} ص{page}]" if page else f"[{src}]"


def _grade_topic_from_analysis(analysis) -> tuple:
    grade = topic = None
    if analysis is None:
        return grade, topic
    scope = getattr(analysis, "scope", None)
    if scope is not None:
        grade = getattr(getattr(scope, "grade", None), "value", None) or getattr(scope, "grade", None)
        topic = getattr(scope, "topic", None)
    if not topic and getattr(analysis, "topics", None):
        topic = analysis.topics[0] if analysis.topics else None
    if isinstance(grade, str) and grade in ("unknown", "غير محدد", ""):
        grade = None
    return (str(grade) if grade else None), (str(topic) if topic else None)
