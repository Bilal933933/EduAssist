"""دوال نقية لذاكرة المدرس — بلا اعتماد على قاعدة البيانات."""
from __future__ import annotations

import hashlib
import re
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _norm_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _valid_grade_label(label: str | None) -> str | None:
    """يرفض تسميات الصفوف الفاسدة (كائنات قديمة/أكواد) — تسمية العرض يجب أن تكون عربية."""
    if not label:
        return None
    text = str(label).strip()
    if not text or "(" in text or "=" in text:
        return None
    if not re.search(r"[\u0600-\u06FF]", text):
        return None
    return text


def _mistake_key(mistake: str, grade_id: int | None, topic: str | None) -> str:
    base = f"{_norm_text(mistake)}|{grade_id or ''}|{_norm_text(topic or '')}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:40]
