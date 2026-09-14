"""طبقة التحقق — نوعان فقط، دوال خالصة بلا FastAPI لتبقى قابلة لإعادة الاستخدام والاختبار.

النوع 1 (شكلي): يُغطى بقيود Pydantic Field في schemas + validation_error_handler.
النوع 2 (منطقي): دوال هنا ترفع AppError برمز دقيق قبل أي IO (store/kb/LLM).
"""
import re
import string

from app.core.errors import AppError

MAX_QUESTION = 2000
MIN_QUESTION = 2
MAX_TOPIC = 200
MAX_TITLE = 120
MAX_TEACHER_ID = 64

_TEACHER_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")
_ARABIC_PUNCT = "؟،؛«»…ـ"
_PUNCT_SET = set(string.punctuation + string.whitespace + _ARABIC_PUNCT)


def _strip(text: str | None) -> str:
    return (text or "").strip()


def validate_question(question: str | None) -> str:
    """تحقق منطقي من السؤال. يعيد النص المقلم أو يرفع AppError."""
    q = _strip(question)
    if not q:
        raise AppError("QUESTION_EMPTY")
    if len(q) < MIN_QUESTION:
        raise AppError("QUESTION_TOO_SHORT")
    if len(q) > MAX_QUESTION:
        raise AppError("QUESTION_TOO_LONG")
    if all(ch in _PUNCT_SET for ch in q):
        raise AppError("QUESTION_EMPTY")
    return q


def validate_topic(topic: str | None) -> str:
    t = _strip(topic)
    if not t:
        raise AppError("TOPIC_EMPTY")
    if len(t) > MAX_TOPIC:
        raise AppError("TOPIC_TOO_LONG")
    return t


def validate_teacher_id(teacher_id: str | None) -> str:
    t = _strip(teacher_id) or "default"
    if len(t) > MAX_TEACHER_ID or not _TEACHER_RE.match(t):
        raise AppError("TEACHER_ID_INVALID")
    return t


def validate_thread_id(thread_id: int | None) -> int | None:
    if thread_id is None:
        return None
    if not isinstance(thread_id, int) or isinstance(thread_id, bool) or thread_id <= 0:
        raise AppError("VALIDATION_ERROR")
    return thread_id


def validate_title(title: str | None) -> str | None:
    if title is None:
        return None
    t = title.strip()
    if len(t) > MAX_TITLE:
        raise AppError("TITLE_TOO_LONG")
    return t or None


def validate_grade(grade: str | None, catalog: list[str] | None = None) -> str | None:
    """إن توفر الكتالوج تحقق منطقي صارم، وإلا فحص شكلي فقط (لا يكسر بدون DB)."""
    g = _strip(grade)
    if not g:
        return None
    if catalog is not None and g not in catalog:
        raise AppError("GRADE_UNKNOWN")
    return g


def ensure_thread_exists(store, thread_id: int) -> None:
    if not store.thread_exists(thread_id):
        raise AppError("THREAD_NOT_FOUND")
