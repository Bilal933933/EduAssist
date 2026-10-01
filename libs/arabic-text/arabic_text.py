"""أدوات نص عربية نقية ومشتركة — مكتبة مستقلة عن أي خدمة.

قاعدة معمارية ملزمة: يُمنع استيراد أي شيء من `app` (الباك) أو أي خدمة
داخل هذه الحزمة. الاعتماد اتجاه واحد فقط: الخدمات ← libs.
الدوال حتمية بلا شبكة ولا حالة — صالحة للباك والسكربتات معًا.
"""

import json
import re

__all__ = [
    "normalize_whitespace",
    "extract_topic",
    "split_subtopics",
    "extract_grade_code",
    "extract_json_block",
    "parse_json_block",
    "GRADE_NUM_WORDS",
    "SUBJECT_ALIASES",
    "ARABIC_BRANCHES",
    "extract_subject",
    "extract_branch",
]

_WHITESPACE = re.compile(r"\s+")

# حدود الموضوع بعد درس/وحدة/حول (مُجمّعة من النسخ الميدانية المُثبتة):
# فواصل، للصف/للمرحلة/لل، مع، علامات استفهام، نهاية النص.
_TOPIC_BOUNDARY = r"(?:\s*[-–،,]\s*|\s+للصف|\s+للمرحلة|\s+لل\b|\s+مع\s+|\?|؟|$)"
_TOPIC_RE = re.compile(r"(?:درس|وحدة|حول|لدرس|لوحدة)\s+(.+?)" + _TOPIC_BOUNDARY)

_GRADE_PATTERNS = [
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

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


# --- بيانات نطاق المنهج (كانت مبعثرة في clarifier) ---------------------------
# خرائط كلمات نقية بلا اعتماد على أي خدمة — قابلة للتركيب مع دوال الاستخراج.

GRADE_NUM_WORDS = {
    "1": "الأول", "2": "الثاني", "3": "الثالث", "4": "الرابع", "5": "الخامس",
    "6": "السادس", "7": "السابع", "8": "الثامن", "9": "التاسع", "10": "العاشر",
}

SUBJECT_ALIASES = {
    "اللغة العربية": ["اللغة العربية", "اللغة العربيه", "لغة عربية", "العربي", "عربي"],
    "الرياضيات": ["الرياضيات", "رياضيات", "الرياضه"],
    "العلوم": ["العلوم", "علوم"],
    "الدراسات الاجتماعية": ["الدراسات الاجتماعية", "الدراسات الاجتماعيه", "دراسات اجتماعية", "دراسات"],
    "اللغة الإنجليزية": ["اللغة الإنجليزية", "اللغة الانجليزية", "الانجليزي", "الإنجليزي", "انجليزي", "إنجليزي"],
}

ARABIC_BRANCHES = {
    "نحو": ["نحو", "النحو", "قواعد", "إعراب", "الإعراب", "الفاعل", "المبتدأ"],
    "صرف": ["صرف", "الصرف", "وزن", "الوزن", "الميزان", "اشتقاق", "الاشتقاق", "جذر"],
    "بلاغة": ["بلاغة", "البلاغة", "تشبيه", "استعارة", "كناية", "محسنات"],
    "أدب": ["أدب", "الأدب", "أدب عربي"],
    "قراءة": ["قراءة", "القراءة", "الفهم القرائي"],
    "نصوص": ["نصوص", "النصوص"],
    "إملاء": ["إملاء", "الإملاء", "املاء", "همزة", "الهمزة", "التاء المربوطة"],
    "تعبير": ["تعبير", "التعبير", "موضوع تعبير", "كتابة موضوع"],
}


def extract_subject(question: str | None) -> str | None:
    """أول مادة يظهر اسمها في النص أو None."""
    q = question or ""
    for subject, aliases in SUBJECT_ALIASES.items():
        if any(alias in q for alias in aliases):
            return subject
    return None


def extract_branch(question: str | None) -> str | None:
    """أول فرع عربي يظهر في النص أو None."""
    q = question or ""
    for branch, aliases in ARABIC_BRANCHES.items():
        if any(alias in q for alias in aliases):
            return branch
    return None


def normalize_whitespace(text: str | None) -> str:
    """يطوي كل المسافات البيضاء إلى مسافة واحدة ويقص الأطراف."""
    return _WHITESPACE.sub(" ", text or "").strip()


def extract_topic(question: str | None) -> str | None:
    """يستخرج الموضوع بعد درس/وحدة/حول/لدرس/لوحدة.

    يحافظ على الحروف م/ع (كان الخلل السابق يستبعدها كأحرف).
    يعيد None عند غياب الموضوع.
    """
    q = (question or "").strip()
    m = _TOPIC_RE.search(q)
    if not m:
        return None
    return m.group(1).strip(" ،ـ") or None


def split_subtopics(topic: str | None) -> list[str]:
    """يشق الموضوع المركب عند واو العطف المسبوقة بمسافة فقط.

    يحافظ على ال ("المبتدأ والخبر" → ["المبتدأ", "الخبر"]) ولا يمس واو
    داخل الكلمة ("المؤول بالصريح" يبقى واحدًا). المفرد يعيد [topic].
    """
    parts = [p.strip(" -،") for p in re.split(r"\s+و", topic or "") if p.strip(" -،")]
    return parts or ([topic.strip(" -،")] if (topic or "").strip(" -،") else [])


def extract_grade_code(question: str | None) -> tuple[str | None, str | None]:
    """يستخرج (grade_code, stage) مثل ("primary_5", "primary") أو (None, None).

    بلا كلمة مرحلة يُفترض primary (سلوك المحلل المجمّد: "للصف الثاني" → primary_2).
    """
    q = question or ""
    for grade, patterns in _GRADE_PATTERNS:
        if any(re.search(p, q, re.IGNORECASE) for p in patterns):
            return grade, grade.split("_")[0]
    m = re.search(r"(?:للصف|الصف)\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس)\b", q)
    if not m:
        return None, None
    num = {"الأول": "1", "الثاني": "2", "الثالث": "3", "الرابع": "4", "الخامس": "5", "السادس": "6"}[m.group(1)]
    # بلا مرحلة ملاصقة: امسح النص كله (سلوك المحلل المجمّد)، وإلا primary.
    if "إعدادي" in q or "اعدادي" in q:
        return f"prep_{num}", "prep"
    return f"primary_{num}", "primary"


def extract_json_block(raw: str | None) -> str | None:
    """يستخرج أول كتلة {...} من رد النموذج (تحل محل 7 نسخ حرفية)."""
    if not raw:
        return None
    m = _JSON_BLOCK_RE.search(raw)
    return m.group() if m else None


def parse_json_block(raw: str | None) -> dict | None:
    """extract_json_block + json.loads آمن (None عند الفشل)."""
    block = extract_json_block(raw)
    if not block:
        return None
    try:
        data = json.loads(block)
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, ValueError):
        return None
