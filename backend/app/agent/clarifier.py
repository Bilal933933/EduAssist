"""استخراج نطاق الاستعلام قبل الاسترجاع مع الحفاظ على الاستيضاح القديم."""
import re

from arabic_text import (
    GRADE_NUM_WORDS,
    extract_branch,
    extract_grade_code,
    extract_subject,
    normalize_whitespace,
)

GRADE_PATTERN = re.compile(r"الصف\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر).*?(ابتدائي|إعدادي|اعدادي|ثانوي)")
GRADE_KEYWORDS = [
    "الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر",
    "ابتدائي", "إعدادي", "اعدادي", "ثانوي"
]
GRADE_FOLDER_PATTERN = re.compile(r"(?:grade|primary[_\-]?|row[_\-]?)(\d+)")


def _clean(text: str) -> str:
    return normalize_whitespace(text)


def extract_scope(question: str) -> dict:
    """تركيب صريح من ذرات المكتبة — قاعدة النطاق (الفرع يقتضي العربية) هنا لا في المكتبة."""
    q = _clean(question)
    scope = {}
    grade, stage = extract_grade_code(q)
    if grade:
        scope["grade"] = grade
        scope["stage"] = stage
    subject = extract_subject(q)
    branch = extract_branch(q)
    if branch:
        scope["branch"] = branch
        subject = subject or "اللغة العربية"
    if subject:
        scope["subject"] = subject
    return scope


def _extract_grades_from_hits(hits: list) -> set[str]:
    grades = set()
    for h in hits[:8]:
        src = " ".join(str(h.get(k, "") or "") for k in ("source", "title", "doc_path", "grade"))
        found = GRADE_PATTERN.findall(src)
        for match in found:
            grade_str = " ".join(match) if isinstance(match, tuple) else match
            grades.add(grade_str.strip())
        for kw in GRADE_KEYWORDS:
            if kw in src:
                grades.add(kw)
        for num in GRADE_FOLDER_PATTERN.findall(src):
            if num in GRADE_NUM_WORDS:
                grades.add(f"الصف {GRADE_NUM_WORDS[num]}")
    return grades


def _extract_source_types(hits: list) -> set[str]:
    types = set()
    for h in hits[:8]:
        src = " ".join(str(h.get(k, "") or "") for k in ("source", "doc_path", "doc_type", "source_type")).lower()
        if any(w in src for w in ["textbook", "primary", "المنهج", "الكتاب", "وزارة"]):
            types.add("كتب الوزارة / المنهج")
        elif any(w in src for w in ["references", "general", "مراجع", "كيف تتقن", "الأضواء", "سلاح التلميذ"]):
            types.add("المراجع")
        else:
            types.add("مصادر أخرى")
    return types


def needs_clarification(query: str, hits: list) -> dict | None:
    # إذا حدد الصف في السؤال لا نطلب استيضاحًا.
    if extract_scope(query).get("grade"):
        return None
    if GRADE_PATTERN.search(query) or any(kw in query for kw in GRADE_KEYWORDS):
        return None

    grades = _extract_grades_from_hits(hits)
    if len(grades) > 1:
        clean_options = sorted(grades)[:5]
        return {
            "question": "لم تحدد الصف الدراسي، والنتائج تشمل عدة صفوف. أي صف تحضر له؟",
            "options": clean_options,
            "context": {"type": "grade", "detected_grades": list(grades)},
        }

    source_types = _extract_source_types(hits)
    if len(source_types) > 1:
        return {
            "question": "السؤال عام، هل تفضل التحضير من كتب الوزارة/المنهج أم الاستعانة بالمراجع؟",
            "options": sorted(source_types),
            "context": {"type": "source_type", "detected_types": sorted(source_types)},
        }
    return None
