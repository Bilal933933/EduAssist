import json
import re

DECOMPOSE_PROMPT = """حلل طلب المدرس وفككه إلى استعلامات بحث فرعية.

طلب المدرس: "{question}"
نية الطلب: {intent}

القواعد:
- إذا طلب "حضر لي درس X" → فكك إلى 4 استعلامات: [تعريف X، علامات/أحكام X، أنواع X، أمثلة وتدريبات X]
- إذا سأل "ما الفرق بين A و B" أو "الفرق بين A والحال" → فكك إلى استعلامين منفصلين: [تعريف A، تعريف B] ولا تبحث عن عبارة "الفرق بين" نفسها
- إذا سأل عن أسلوب شرح → فكك إلى 2 استعلامات: [شرح X، استراتيجيات تدريس X]
- إذا كانت النية ورقة عمل/تدريبات/اختبار/مراجعة/قراءة/مناقشة/وسيلة بصرية حول X → فكك X إلى أركانه: [تعريف X وأركانه، أحكام X وقواعدها، أمثلة X، تدريبات وتطبيقات X] — لا تبحث عن عبارة الطلب نفسها (مثل "ورقة عمل" أو "حزمة مراجعة") بل عن مكونات الموضوع
- إذا سؤال عادي → استعلام واحد كما هو
- أضف الصف إذا ذُكر (مثال: الصف الخامس)

أجب JSON فقط:
{{"queries": ["استعلام1", "استعلام2", ...]}}
مثال: "حضر لي درس الفاعل - الخامس" → {{"queries": ["تعريف الفاعل", "علامات رفع الفاعل", "أنواع الفاعل اسم ظاهر وضمير", "أمثلة وتدريبات الفاعل الصف الخامس"]}}
مثال: "ما الفرق بين التمييز والحال" → {{"queries": ["تعريف التمييز وأحكامه", "تعريف الحال وأنواعه"]}}
مثال: "أنشئ حزمة مراجعة شاملة لوحدة الجملة الفعلية - الصف الخامس" → {{"queries": ["تعريف الجملة الفعلية وأركانها", "الفعل وأنواعه", "الفاعل وأحكامه وعلامات رفعه", "المفعول به وعلامات نصبه", "أمثلة وتدريبات الجملة الفعلية الصف الخامس"]}}
"""

# نوايا التوليد التي تتطلب توسعة الموضوع إلى أركانه
EXPAND_INTENTS = {"generate_worksheet", "generate_exercises", "generate_quiz", "generate_exam", "generate_reading", "generate_discussion", "generate_visual", "generate_revision", "prepare_lesson"}

# محاور ثابتة للمواضيع الشائعة: تعمل بلا LLM وتضمن بحث المكونات دائماً
TOPIC_PILLARS = {
    "الجملة الفعلية": ["الفعل وأنواعه", "الفاعل وأحكامه وعلامات رفعه", "المفعول به وعلامات نصبه"],
    "الجملة الاسمية": ["المبتدأ وأحكامه", "الخبر وأنواعه", "النواسخ"],
    "الفاعل": ["تعريف الفاعل", "أنواع الفاعل", "عامل الفاعل", "علامات رفع الفاعل"],
    "المفعول به": ["تعريف المفعول به", "صور المفعول به", "علامات نصب المفعول به"],
    "المبتدأ": ["تعريف المبتدأ", "الخبر وأنواعه", "النواسخ"],
    "كان وأخواتها": ["تعريف كان وأخواتها", "عمل كان وأخواتها", "أمثلة كان وأخواتها"],
    "إن وأخواتها": ["تعريف إن وأخواتها", "عمل إن وأخواتها", "لا النافية للجنس"],
    "المفعول المطلق": ["تعريف المفعول المطلق", "أنواع المفعول المطلق", "علامات نصبه"],
    "الحال": ["تعريف الحال", "أنواع الحال", "الفرق بين الحال والتمييز"],
    "التمييز": ["تعريف التمييز", "أنواع التمييز", "الفرق بين التمييز والحال"],
    "النعت": ["تعريف النعت", "أنواع النعت", "الفرق بين النعت والحال"],
}


def _topic_pillars(topic: str | None) -> list:
    """يطابق الموضوع مع الخريطة (يقبل النكرة/المعرفة والجزء من الاسم)."""
    if not topic:
        return []
    t = topic.strip()
    for key, pillars in TOPIC_PILLARS.items():
        if key in t or t in key:
            return pillars
    return []

_REQUEST_VERBS = ("أنشئ", "انشئ", "حضر", "حضّر", "أعد", "اعد", "صمم", "ولّد", "ولد", "اكتب")


def _extract_topic_and_grade(question: str) -> tuple[str | None, str]:
    """يستخرج الموضوع (بعد درس/وحدة/حول/لدرس/لوحدة) والصف من نص الطلب."""
    q = question.strip()
    grade = ""
    m = re.search(r"الصف\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس)(?:\s+(الابتدائي|الإعدادي|الثانوي))?", q)
    if m:
        grade = f"الصف {m.group(1)}" + (f" {m.group(2)}" if m.group(2) else "")
    m = re.search(r"(?:درس|وحدة|حول|لدرس|لوحدة)\s+(.+?)(?:\s*[-–،,]\s*|\s+للصف|\s+مع\s+|\?|؟|$)", q)
    if m:
        topic = m.group(1).strip(" ،ـ")
        for v in _REQUEST_VERBS:
            if topic.startswith(v):
                topic = topic[len(v):].strip()
        return (topic or None), grade
    return None, grade


def _fallback_queries(question: str, intent: str | None) -> list:
    """توسعة حتمية بدون LLM: تفكيك الموضوع إلى أركانه حسب النية."""
    topic, grade = _extract_topic_and_grade(question)
    if not topic or intent not in EXPAND_INTENTS:
        return [question]
    g = f" {grade}" if grade else ""
    poss = "ها" if (topic.endswith("ة") or topic.endswith("اء") or "الجملة" in topic) else "ه"
    pillars = _topic_pillars(topic)
    if pillars:
        qs = [f"تعريف {topic} وأركان{poss}{g}"]
        qs.extend(f"{p}{g}" for p in pillars)
        qs.append(f"أمثلة وتدريبات {topic}{g}")
        return qs
    if intent == "generate_reading":
        return [f"نصوص {topic}{g}", f"مفاهيم {topic} الأساسية", f"أمثلة {topic}{g}"]
    if intent == "generate_discussion":
        return [f"شرح {topic}{g}", f"مقارنة {topic} بالمفاهيم المشابهة", f"تطبيقات {topic}{g}"]
    if intent == "generate_visual":
        return [f"تعريف {topic}{g}", f"أنواع {topic}", f"مقارنة {topic}{g}"]
    return [f"تعريف {topic} وأركان{poss}{g}", f"أحكام {topic} وقواعدها", f"أمثلة {topic}{g}", f"تدريبات {topic}{g}"]

def get_pillars(question: str) -> list:
    """محاور الموضوع المطلوبة (للناقد): [] عند غياب خريطة."""
    topic, _ = _extract_topic_and_grade(question or "")
    return _topic_pillars(topic)


def decompose_question(client, question: str, max_queries: int = 5, intent: str | None = None) -> list:
    """يفكك سؤال المدرس إلى استعلامات فرعية عبر Gemini، مع fallback حتمي موجّه بالنية."""
    # الأسئلة المفردة (إعراب/شرح/تحية) لا تحتاج تفكيكاً — استعلام واحد مباشر بلا LLM.
    if intent in ("parse", "explain", "chitchat", "general_question", "correct", "review"):
        return [question]
    # حالة خاصة حتمية: الفرق بين A و B → لا تعتمد على LLM فقط
    if "الفرق بين" in question or "الفرق بين" in question.replace("ـ",""):
        m = re.search(r"الفرق بين\s+(.+?)\s+و\s+(.+?)(?:\?|؟|$)", question)
        if m:
            a = m.group(1).strip(" ،ـ")
            b = m.group(2).strip(" ،ـ؟?")
            # نظف من كلمات زائدة مثل "التمييز والحال"
            return [f"تعريف {a} وأحكامه", f"تعريف {b} وأنواعه"]
    if len(question.strip()) < 10:
        return _fallback_queries(question, intent)

    prompt = DECOMPOSE_PROMPT.format(question=question, intent=intent or "غير محددة")
    try:
        from app.agent.fc_client import call_simple
        raw = call_simple(client, prompt, "أنت محلل أسئلة. أجب JSON فقط.")
        # استخراج JSON
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return _fallback_queries(question, intent)
        data = json.loads(m.group())
        queries = data.get("queries", [question])
        # تنظيف
        queries = [q.strip() for q in queries if q.strip()][:max_queries]
        if not queries:
            return _fallback_queries(question, intent)
        # إذا أعاد LLM استعلاماً واحداً فقط لنية توليد → وسّع حتمياً
        if len(queries) <= 1 and intent in EXPAND_INTENTS:
            fb = _fallback_queries(question, intent)
            if len(fb) > 1:
                print(f"[Decomposer] توسعة حتمية ({intent}): {fb}")
                return fb[:max_queries]
        # إلحاق المحاور الغائبة من نتائج LLM (ضمان التغطية)
        if intent in EXPAND_INTENTS:
            topic, grade = _extract_topic_and_grade(question)
            g = f" {grade}" if grade else ""
            for p in _topic_pillars(topic):
                pq = f"{p}{g}"
                if len(queries) >= max_queries:
                    break
                if not any(p.split()[0] in q for q in queries):
                    queries.append(pq)
        # أضف السؤال الأصلي إذا لم يكن موجوداً كأول عنصر
        if question not in queries and len(queries) < max_queries:
            queries.insert(0, question)
        print(f"[Decomposer] {question[:40]} → {queries}")
        return queries
    except Exception as e:
        print(f"[Decomposer error: {e}] → fallback")
        return _fallback_queries(question, intent)
