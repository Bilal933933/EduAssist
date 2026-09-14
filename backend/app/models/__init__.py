"""النماذج — SQLAlchemy. التخزين الفعلي حالياً في src/storage؛ هذا الملف نقطة التوسع SaaS."""
from app.db.base import Base  # noqa: F401 — يُصدَّر للترحيلات القادمة

__all__ = ["Base"]
