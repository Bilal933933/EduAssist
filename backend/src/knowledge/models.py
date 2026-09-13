import os
from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, Float, func, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("VECTOR_DATABASE_URL", "postgresql://postgres:12345678@localhost:5432/ai_grammar_tutor")
Base = declarative_base()


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
    concepts = Column(ARRAY(String), default=list)

    title = Column(String(255))
    text = Column(Text)
    source = Column(String(255))
    page = Column(Integer)
    embedding = Column(ARRAY(Float))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


Index("ix_knowledge_chunks_grade_subject", KnowledgeChunk.grade, KnowledgeChunk.subject)
Index("ix_knowledge_chunks_stage_subject", KnowledgeChunk.stage, KnowledgeChunk.subject)
Index("ix_knowledge_chunks_source_type_subject", KnowledgeChunk.source_type, KnowledgeChunk.subject)
