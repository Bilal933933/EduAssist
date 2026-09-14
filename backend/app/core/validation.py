"""التحقق العام — cross-cutting فقط (Modular Monolith).

القاعدة: العام الشكلي فقط يبقى هنا (teacher/thread/title).
تحقق النطاق (question/topic/grade) مالكه modules/*، وهنا وكلاء توافقية
بتحميل كسول (lazy) لتفادي الاستيراد الدائري: core ← modules عند التحميل.
"""
import re

from app.core.errors import AppError

MAX_TITLE = 120
MAX_TEACHER_ID = 64
# ثوابت توافقية (المصدر المعتمد modules/*/validation.py — نسخ ثابتة بلا استيراد)
MAX_TOPIC = 200
MAX_QUESTION = 2000
MIN_QUESTION = 2

_TEACHER_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")


def _strip(text: str | None) -> str:
    return (text or "").strip()


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


def ensure_thread_exists(store, thread_id: int) -> None:
    if not store.thread_exists(thread_id):
        raise AppError("THREAD_NOT_FOUND")


# --- توافقية كسولة (لا استيراد علوي من modules لتفادي الدورة) ---
def validate_question(question: str | None) -> str:
    from app.modules.chat.validation import validate_question as _v
    return _v(question)


def validate_topic(topic: str | None) -> str:
    from app.modules.cards.validation import validate_topic as _v
    return _v(topic)


def validate_grade(grade: str | None, catalog: list[str] | None = None) -> str | None:
    from app.modules.memory.validation import validate_grade as _v
    return _v(grade, catalog)
