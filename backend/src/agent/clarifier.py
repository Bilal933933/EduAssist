"""استخراج نطاق الاستعلام قبل الاسترجاع مع الحفاظ على الاستيضاح القديم."""
import re

GRADE_PATTERN = re.compile(r"الصف\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر).*?(ابتدائي|إعدادي|اعدادي|ثانوي)")
GRADE_KEYWORDS = [
    "الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر",
    "ابتدائي", "إعدادي", "اعدادي", "ثانوي"
]
GRADE_FOLDER_PATTERN = re.compile(r"(?:grade|primary[_\-]?|row[_\-]?)(\d+)")
GRADE_MAP = {
    "1": "الأول", "2": "الثاني", "3": "الثالث", "4": "الرابع", "5": "الخامس",
    "6": "السادس", "7": "السابع", "8": "الثامن", "9": "التاسع", "10": "العاشر"
}

GRADE_PATTERNS = [
    ("primary_1", [r"الأول\s+الابتدائي", r"اول\s+ابتدائي"]),
    ("primary_4", [r"الرابع\s+الابتدائي", r"رابع\s+ابتدائي"]),
    ("primary_5", [r"الخامس\s+الابتدائي", r"خامس\s+ابتدائي"]),
    ("primary_6", [r"السادس\s+الابتدائي", r"سادس\s+ابتدائي"]),
    ("prep_1", [r"الأول\s+الإعدادي", r"اول\s+اعدادي", r"أولى?\s+إعدادي"]),
    ("prep_2", [r"الثاني\s+الإعدادي", r"ثاني\s+اعدادي", r"ثانية?\s+إعدادي"]),
    ("prep_3", [r"الثالث\s+الإعدادي", r"ثالث\s+اعدادي", r"ثالثة?\s+إعدادي"]),
    ("secondary_1", [r"الأول\s+الثانوي", r"اول\s+ثانوي"]),
    ("secondary_2", [r"الثاني\s+الثانوي", r"ثاني\s+ثانوي"]),
    ("secondary_3", [r"الثالث\s+الثانوي", r"ثالث\s+ثانوي"]),
]

SUBJECT_ALIASES = {
    "اللغة العربية": ["اللغة العربية", "اللغة العربيه", "لغة عربية", "العربي", "عربي"],
    "الرياضيات": ["الرياضيات", "رياضيات", "الرياضه"],
    "العلوم": ["العلوم", "علوم"],
    "الدراسات الاجتماعية": ["الدراسات الاجتماعية", "الدراسات الاجتماعيه", "دراسات اجتماعية", "دراسات"],
    "اللغة الإنجليزية": ["اللغة الإنجليزية", "اللغة الانجليزية", "الانجليزي", "الإنجليزي", "انجليزي", "إنجليزي"],
}

ARABIC_BRANCHES = {
    "نحو": ["نحو", "النحو", "قواعد"],
    "صرف": ["صرف", "الصرف"],
    "بلاغة": ["بلاغة", "البلاغة"],
    "أدب": ["أدب", "الأدب", "أدب عربي"],
    "قراءة": ["قراءة", "القراءة"],
    "نصوص": ["نصوص", "النصوص"],
}


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def extract_scope(question: str) -> dict:
    q = _clean(question)
    scope = {}
    for grade, patterns in GRADE_PATTERNS:
        if any(re.search(pattern, q, re.IGNORECASE) for pattern in patterns):
            scope["grade"] = grade
            scope["stage"] = grade.split("_")[0]
            break

    for subject, aliases in SUBJECT_ALIASES.items():
        if any(alias in q for alias in aliases):
            scope["subject"] = subject
            break

    for branch, aliases in ARABIC_BRANCHES.items():
        if any(alias in q for alias in aliases):
            scope["branch"] = branch
            scope.setdefault("subject", "اللغة العربية")
            break

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
            if num in GRADE_MAP:
                grades.add(f"الصف {GRADE_MAP[num]}")
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
