from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, func, Index
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from pgvector.sqlalchemy import Vector
from app.db.base import Base
from app.core.config import settings

# الرابط الموحد — كان os.getenv هنا يكرر config ويتجاوزه
DB_URL = settings.DATABASE_URL or settings.VECTOR_DATABASE_URL


class KnowledgeChunk(Base):
    """قطعة معرفة مع سياقها المنهجي الكامل.

    حقول النطاق ليست للعرض فقط؛ يستخدمها Retrieval لعمل pre-filter قبل التشابه.
    """

    __tablename__ = "knowledge_chunks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    doc_key = Column(String(64), unique=True, index=True)
    doc_path = Column(String(512))
    doc_type = Column(String(32), default="general")

    # Retrieval scope / metadata
    grade = Column(String(32), index=True)          # primary_4 / prep_3 / ...
    stage = Column(String(32), index=True)          # primary / prep / secondary / general
    subject = Column(String(128), index=True)       # اللغة العربية / الرياضيات / ...
    branch = Column(String(128), index=True)        # نحو / صرف / بلاغة / ...
    source_type = Column(String(32), index=True)    # textbook | teacher_guide | reference | pedagogy | general
    book_id = Column(String(128), index=True)
    unit = Column(String(255))
    lesson = Column(String(255))
    term = Column(String(32), index=True)              # الفصل الدراسي
    parent_section = Column(String(512), index=True)  # book_id|unit|lesson لدمج مقاطع الدرس
    chunk_index = Column(Integer)                     # ترتيب المقطع داخل القسم
    chunk_token_count = Column(Integer)
    concepts = Column(ARRAY(String), default=list)

    title = Column(String(255))
    text = Column(Text)
    source = Column(String(255))
    page = Column(Integer)
    embedding = Column(Vector(384))  # محلي e5-small للبناء؛ bge-m3 (1024) قبل الإطلاق
    search_text = Column(Text)
    search_vector = Column(TSVECTOR)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


Index("ix_knowledge_chunks_grade_subject", KnowledgeChunk.grade, KnowledgeChunk.subject)
Index("ix_knowledge_chunks_stage_subject", KnowledgeChunk.stage, KnowledgeChunk.subject)
Index("ix_knowledge_chunks_source_type_subject", KnowledgeChunk.source_type, KnowledgeChunk.subject)
Index("ix_knowledge_chunks_search_vector_gin", KnowledgeChunk.search_vector, postgresql_using="gin")
Index("ix_chunks_term", KnowledgeChunk.term)
Index("ix_chunks_parent", KnowledgeChunk.parent_section)
Index("ix_chunks_book_lesson", KnowledgeChunk.book_id, KnowledgeChunk.lesson)
