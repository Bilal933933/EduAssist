"""تحقق نطاق البطاقات — ملك الفيتشر."""
from app.core.errors import AppError

MAX_TOPIC = 200


def validate_topic(topic: str | None) -> str:
    t = (topic or "").strip()
    if not t:
        raise AppError("TOPIC_EMPTY")
    if len(t) > MAX_TOPIC:
        raise AppError("TOPIC_TOO_LONG")
    return t
