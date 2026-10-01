"""استدلال نصي نقي لذاكرة المدرس — بلا اعتماد على قاعدة البيانات."""
from __future__ import annotations


def looks_like_lesson_prep(question: str) -> bool:
    q = question or ""
    return any(k in q for k in ["حضر", "تحضير", "خطة درس", "سير حصة", "حضّر", "درس عن"])


def extract_mistake_from_question(question: str) -> str | None:
    q = (question or "").strip()
    triggers = [
        "أخطاء شائعة", "خطأ شائع", "يخطئون", "يخلطون",
        "أخطاء الطلاب", "الخطأ الشائع", "أخطائي الطلاب",
    ]
    if not any(t in q for t in triggers):
        return None
    for t in triggers:
        if t in q:
            tail = q[q.find(t) + len(t) :].strip(" :：-،.")
            if len(tail) > 8:
                return tail[:180]
            return q[:180]
    return None


def infer_preferences(question: str, prefs: dict) -> dict:
    prefs = dict(prefs)
    q = question or ""
    if any(k in q for k in ["مختصر", "باختصار", "سريع"]):
        prefs["detail_level"] = "مختصر"
    elif any(k in q for k in ["مفصل", "عميق", "شامل", "تفصيلي"]):
        prefs["detail_level"] = "مفصل"
    if any(k in q for k in ["من الحياة", "واقعي", "يومي"]):
        prefs["example_style"] = "من_الحياة"
    if any(k in q for k in ["مشوق", "ممتع", "لعبة"]):
        prefs["tone"] = "مشوّق"
    else:
        prefs.setdefault("tone", "احترافي")
    if any(k in q for k in ["خطة", "سير حصة", "تحضير", "حضر"]):
        prefs["prefers_lesson_plans"] = True
    if any(k in q for k in ["تدريب", "تمرين", "أسئلة", "اختبار"]):
        prefs["prefers_exercises"] = True
    return prefs


def loads_list(raw) -> list:
    """تحويل عمود JSON قديم إلى قائمة — يعيد [] عند الفشل."""
    import json

    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []
