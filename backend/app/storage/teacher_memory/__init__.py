"""ذاكرة المدرس — حزمة M1/M2 (كانت ملفاً واحداً، قُسّمت حسب المسؤولية).

التوافق: `from app.storage.teacher_memory import TeacherMemoryStore` يعمل كما كان.
"""
from app.storage.teacher_memory.models import Base
from app.storage.teacher_memory.store import TeacherMemoryStore

__all__ = ["Base", "TeacherMemoryStore"]
