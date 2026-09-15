"""النماذج — SQLAlchemy، نقطة التوسع SaaS."""
from app.db.base import Base  # noqa: F401 — يُصدَّر للترحيلات القادمة
from app.models.knowledge_chunk import KnowledgeChunk  # noqa: F401

__all__ = ["Base", "KnowledgeChunk"]
