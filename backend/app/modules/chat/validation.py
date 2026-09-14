"""تحقق نطاق المحادثة — ملك الفيتشر، لا core.

validate_question مفهوم نطاق (طول/علامات/تقليم عربي).
المعرفات العامة (teacher/thread) تبقى في core وتُستورد عند الحاجة.
"""
import string

from app.core.errors import AppError

MAX_QUESTION = 2000
MIN_QUESTION = 2

_ARABIC_PUNCT = "؟،؛«»…ـ"
_PUNCT_SET = set(string.punctuation + string.whitespace + _ARABIC_PUNCT)


def validate_question(question: str | None) -> str:
    """تقليم ← فارغ/علامات ← طول → نص نظيف. يرفع AppError قبل أي IO."""
    q = (question or "").strip()
    if not q:
        raise AppError("QUESTION_EMPTY")
    if len(q) < MIN_QUESTION:
        raise AppError("QUESTION_TOO_SHORT")
    if len(q) > MAX_QUESTION:
        raise AppError("QUESTION_TOO_LONG")
    if all(ch in _PUNCT_SET for ch in q):
        raise AppError("QUESTION_EMPTY")
    return q
