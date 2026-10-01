"""خدمة ذاكرة المدرس — Facade فقط (النموذج المعياري M1/M2).

المنطق موزع حسب المسؤولية:
- base.py ← engine/session/seed/indexes
- migration_v3.py ← ترحيل جداول v3
- identity.py ← مدرس/صف
- readers.py ← قراءة + Dicts
- prompt.py ← برومبت + ملخص
- writers.py ← تحديث/يدوي/reset
- inference.py ← استدلال نصي نقي
"""
from __future__ import annotations

from app.storage.teacher_memory.base import TeacherMemoryBase
from app.storage.teacher_memory.identity import IdentityMixin
from app.storage.teacher_memory.migration_v3 import MigrationV3Mixin
from app.storage.teacher_memory.prompt import PromptMixin
from app.storage.teacher_memory.readers import ReadersMixin
from app.storage.teacher_memory.writers import WritersMixin


class TeacherMemoryStore(
    TeacherMemoryBase,
    MigrationV3Mixin,
    IdentityMixin,
    ReadersMixin,
    PromptMixin,
    WritersMixin,
):
    """Facade يحافظ على نفس الواجهة العامة — لا منطق هنا."""

    def __init__(self, db_url: str | None = None):
        self._init_engine(db_url)
        self._seed_grades()
        self._ensure_indexes()
        self._migrate_from_v3()
