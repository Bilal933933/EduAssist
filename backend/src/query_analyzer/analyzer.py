import re
from dataclasses import dataclass
from src.query_analyzer.scope import Scope, ScopeField

INTENTS = ["chitchat","prepare_lesson","explain","compare","parse","generate_worksheet","generate_exercises","generate_quiz","generate_exam","generate_reading","generate_discussion","generate_visual","generate_revision","correct","review","activity","pedagogical_advice","general_question"]

TOPIC_KEYWORDS = {
    "المفعول المطلق": ("اللغة العربية","نحو"),
    "الفاعل": ("اللغة العربية","نحو"),
    "المبتدأ": ("اللغة العربية","نحو"),
    "كان وأخواتها": ("اللغة العربية","نحو"),
    "إن وأخواتها": ("اللغة العربية","نحو"),
    "التمييز": ("اللغة العربية","نحو"),
    "الحال": ("اللغة العربية","نحو"),
    "النعت": ("اللغة العربية","نحو"),
    "الميزان الصرفي": ("اللغة العربية","صرف"),
    "المجرد والمزيد": ("اللغة العربية","صرف"),
    "التشبيه": ("اللغة العربية","بلاغة"),
    "الاستعارة": ("اللغة العربية","بلاغة"),
    "الهمزة المتوسطة": ("اللغة العربية","إملاء"),
    "التاء المربوطة": ("اللغة العربية","إملاء"),
    "الفهم القرائي": ("اللغة العربية","قراءة"),
    "كتابة موضوع": ("اللغة العربية","تعبير"),
}

@dataclass
class QueryAnalysis:
    intent: str
    scope: Scope
    source_policy: str  # curriculum_first / general_references / mixed / user_material_first
    topics: list[str]
    needs_clarification: bool = False
    clarification_question: str | None = None

CHITCHAT_PATTERNS = [
    "مرحبا", "مرحباً", "اهلا", "أهلا", "أهلاً", "السلام عليكم", "سلام",
    "صباح الخير", "مساء الخير", "هلا", "هاي",
    "شكرا", "شكراً", "جزاك الله", "ممتاز", "احسنت", "أحسنت",
    "من أنت", "من انت", "عرف بنفسك", "كيف حالك", "عامل ايه",
]

PARSE_KEYWORDS = [
    "أعرب", "اعرب", "إعرب", "إعراب", "اعراب",
    "ما إعراب", "ما اعراب", "اعراب الجملة", "إعراب الجملة",
]

def _is_chitchat(q: str) -> bool:
    qs = q.strip()
    if len(qs) <= 30 and any(p in qs for p in CHITCHAT_PATTERNS):
        return True
    return False


def _detect_intent(q: str) -> str:
    ql = q.strip()
    if _is_chitchat(ql):
        return "chitchat"
    if any(k in ql for k in ["حضر لي درس", "حضّر", "خطة درس", "سير حصة", "تحضير"]):
        return "prepare_lesson"
    if "الفرق بين" in ql:
        return "compare"
    if ql.startswith(("أعرب", "اعرب", "إعرب")) or any(k in ql for k in PARSE_KEYWORDS):
        return "parse"
    if "ورقة عمل" in ql:
        return "generate_worksheet"
    if ("سريع" in ql and ("اختبار" in ql or "تقويم" in ql)) or "quiz" in ql.lower():
        return "generate_quiz"
    if "تدريبات" in ql or "تمارين" in ql:
        return "generate_exercises"
    if "امتحان" in ql or "اختبار" in ql:
        return "generate_exam"
    if "مراجعة شاملة" in ql or "حزمة مراجعة" in ql:
        return "generate_revision"
    if "قراءة" in ql or "فهم" in ql:
        return "generate_reading"
    if "مناقشة" in ql or "نقاش" in ql or "تفكير عميق" in ql:
        return "generate_discussion"
    if "وسيلة بصرية" in ql or "خريطة مفاهيم" in ql or "مخطط" in ql or "جدول مقارنة" in ql:
        return "generate_visual"
    if "صحح" in ql:
        return "correct"
    if "راجع" in ql or "مراجعة" in ql:
        return "review"
    if "نشاط" in ql or "تفاعلي" in ql:
        return "activity"
    if "لا يفهم" in ql or "ماذا أفعل" in ql or "كيف أشرح" in ql:
        return "pedagogical_advice"
    if ql.startswith("ما هو") or ql.startswith("ما هي") or "اشرح" in ql:
        return "explain"
    return "general_question"

def _extract_scope(q: str, context: dict | None = None) -> Scope:
    scope = Scope()
    ctx = context or {}
    # استنتاج من السياق السابق
    if ctx.get("grade"):
        scope.grade = ScopeField(value=ctx["grade"], status="inferred")
        scope.stage = ScopeField(value=ctx.get("stage","prep"), status="inferred")
    # معالجة كلمات الصف المفردة (الخامس وحده)
    standalone_grades = {"الأول":"1","الثاني":"2","الثالث":"3","الرابع":"4","الخامس":"5","السادس":"6"}
    q_clean = q.strip()
    if q_clean in standalone_grades:
        num = standalone_grades[q_clean]
        # حدد المرحلة من السياق أو افترض ابتدائي للخامس/السادس
        stage = ctx.get("stage") or ("primary" if q_clean in ["الخامس","السادس"] else "prep")
        # إذا كان السياق prep، احتفظ به
        if ctx.get("stage") == "prep":
            stage = "prep"
        prefix = "primary" if stage=="primary" else "prep"
        scope.grade = ScopeField(value=f"{prefix}_{num}", status="known")
        scope.stage = ScopeField(value=stage, status="known")
        return scope
    # كشف الصف (يتحمل للصف / الصف)
    m = re.search(r"(?:للصف|الصف)\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس).*?(ابتدائي|إعدادي|ثانوي)?", q)
    if m:
        grade_word, stage_word = m.group(1), m.group(2)
        grade_map = {"الأول":"1","الثاني":"2","الثالث":"3","الرابع":"4","الخامس":"5","السادس":"6"}
        num = grade_map.get(grade_word, "")
        if not stage_word:
            # fallback: تحقق من كامل السؤال
            if "إعدادي" in q: stage_word = "إعدادي"
            elif "ابتدائي" in q: stage_word = "ابتدائي"
        stage = "primary" if "ابتدائي" in (stage_word or "") else "prep" if "إعدادي" in (stage_word or "") else "primary"
        if num:
            prefix = "primary" if stage=="primary" else "prep"
            scope.grade = ScopeField(value=f"{prefix}_{num}", status="known")
            scope.stage = ScopeField(value=stage, status="known")
    elif "ابتدائي" in q:
        scope.stage = ScopeField(value="primary", status="inferred")
    elif "إعدادي" in q:
        scope.stage = ScopeField(value="prep", status="inferred")
    # كشف الموضوع والفرع
    for topic, (subj, branch) in TOPIC_KEYWORDS.items():
        if topic in q:
            scope.topic = topic
            scope.subject = ScopeField(value=subj, status="inferred")
            scope.branch = ScopeField(value=branch, status="inferred")
            break
    if not scope.topic:
        m2 = re.search(r"درس\s+([^\s،,]+(?:\s+[^\s،,]+)?)", q)
        if m2:
            scope.topic = m2.group(1).strip(" ،")
    # إذا لم يُذكر صف في prepare_lesson يبقى unknown
    return scope

def _detect_source_policy(q: str, intent: str) -> str:
    if "وفق منهج" in q or "منهج الصف" in q:
        return "curriculum_first"
    if "شرحًا نحويًا متعمقًا" in q or "مرجع" in q:
        return "general_references"
    if intent == "prepare_lesson":
        return "curriculum_first"
    return "mixed"

def analyze(question: str, context: dict | None = None) -> QueryAnalysis:
    q_stripped = question.strip()
    # حالة خاصة: رسالة قصيرة جداً (؟ / الخامس / نعم) → استخدم السياق السابق كاملاً
    if q_stripped in ["؟", "?", "؟؟", "??", "ها", "نعم"] or len(q_stripped) < 4 and context and context.get("topic"):
        # استرجع السياق السابق مع تحديث بسيط
        if context.get("topic") and len(q_stripped) < 8:
            # إذا أرسل "الخامس" وحده، اعتبره تكملة لطلب التحضير السابق
            if q_stripped in ["الخامس", "السادس", "الرابع", "الثالث", "الثاني", "الأول", "الخامس الابتدائي", "الخامس", "السادس"]:
                # حدث الصف فقط
                scope = _extract_scope(q_stripped, context)
                # احتفظ بالموضوع من السياق
                if not scope.topic and context.get("topic"):
                    scope.topic = context["topic"]
                    scope.subject = ScopeField(value=context.get("subject","اللغة العربية"), status="inferred")
                    scope.branch = ScopeField(value=context.get("branch","نحو"), status="inferred")
                intent = context.get("intent", "prepare_lesson")
                source_policy = _detect_source_policy(question, intent)
                topics = [scope.topic] if scope.topic else []
                return QueryAnalysis(intent=intent, scope=scope, source_policy=source_policy, topics=topics, needs_clarification=False, clarification_question=None)
            if q_stripped in ["؟", "?", "؟؟"]:
                # إعادة نفس الطلب السابق
                prev_q = context.get("prev_question", "")
                if prev_q:
                    return analyze(prev_q, context)
    intent = _detect_intent(question)
    scope = _extract_scope(question, context)
    # إذا كان السؤال قصير وبلا موضوع لكن السياق يحمل موضوعاً، استعره
    if not scope.topic and context and context.get("topic") and len(q_stripped) < 15:
        scope.topic = context["topic"]
        if not scope.subject.value and context.get("subject"):
            scope.subject = ScopeField(value=context["subject"], status="inferred")
        if not scope.branch.value and context.get("branch"):
            scope.branch = ScopeField(value=context["branch"], status="inferred")
        if intent == "general_question" and context.get("intent") in ("prepare_lesson", "explain"):
            intent = context["intent"]
    source_policy = _detect_source_policy(question, intent)
    topics = [scope.topic] if scope.topic else []
    if intent == "compare":
        m = re.search(r"الفرق بين\s+(.+?)\s+و\s+(.+?)(?:\?|؟|$)", question)
        if m:
            topics = [m.group(1).strip(), m.group(2).strip()]
    needs, q = scope.needs_clarification(intent)
    return QueryAnalysis(intent=intent, scope=scope, source_policy=source_policy, topics=topics, needs_clarification=needs, clarification_question=q)
