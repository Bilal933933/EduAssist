import numpy as np
from sqlalchemy import select, create_engine, func, text
from sqlalchemy.orm import sessionmaker
from src.knowledge.models import KnowledgeChunk, Base, DB_URL


METADATA_COLUMNS = {
    "grade": "VARCHAR(32)",
    "stage": "VARCHAR(32)",
    "subject": "VARCHAR(128)",
    "branch": "VARCHAR(128)",
    "source_type": "VARCHAR(32)",
    "book_id": "VARCHAR(128)",
    "unit": "VARCHAR(255)",
    "lesson": "VARCHAR(255)",
    "concepts": "TEXT[]",
}


class VectorStore:
    def __init__(self, db_url=None):
        self.db_url = db_url or DB_URL
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self._ensure_metadata_schema()
        self.Session = sessionmaker(bind=self.engine)

    def _ensure_metadata_schema(self):
        """ترقية جدول DB القديم بأمان. لا تعتمد create_all على ALTER TABLE."""
        if self.engine.dialect.name != "postgresql":
            return
        with self.engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            conn.execute(text('ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS "search_text" TEXT'))
            conn.execute(text('ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS "search_vector" TSVECTOR'))
            conn.execute(text('CREATE INDEX IF NOT EXISTS "ix_knowledge_chunks_search_vector_gin" ON knowledge_chunks USING GIN ("search_vector")'))
            for column, sql_type in METADATA_COLUMNS.items():
                conn.execute(text(
                    f'ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS "{column}" {sql_type}'
                ))
            for name, cols in {
                "ix_knowledge_chunks_grade_subject": '"grade", "subject"',
                "ix_knowledge_chunks_stage_subject": '"stage", "subject"',
                "ix_knowledge_chunks_source_type_subject": '"source_type", "subject"',
                "ix_knowledge_chunks_grade": '"grade"',
                "ix_knowledge_chunks_subject": '"subject"',
                "ix_knowledge_chunks_branch": '"branch"',
                "ix_knowledge_chunks_source_type": '"source_type"',
                "ix_knowledge_chunks_book_id": '"book_id"',
            }.items():
                conn.execute(text(
                    f'CREATE INDEX IF NOT EXISTS "{name}" ON knowledge_chunks ({cols})'
                ))

    def _metadata_values(self, chunk: dict):
        concepts = chunk.get("concepts") or []
        if isinstance(concepts, str):
            concepts = [concepts]
        return {
            "grade": chunk.get("grade") or None,
            "stage": chunk.get("stage") or None,
            "subject": chunk.get("subject") or None,
            "branch": chunk.get("branch") or None,
            "source_type": chunk.get("source_type") or chunk.get("doc_type") or "general",
            "book_id": chunk.get("book_id") or None,
            "unit": chunk.get("unit") or None,
            "lesson": chunk.get("lesson") or chunk.get("title") or None,
            "concepts": concepts,
        }

    def _search_text(self, chunk: dict) -> str:
        try:
            from src.knowledge.search import _normalize_arabic
        except ImportError:
            from knowledge.search import _normalize_arabic  # type: ignore
        parts = [
            chunk.get("title") or "",
            (chunk.get("text") or "")[:2000],
            chunk.get("lesson") or "",
            chunk.get("unit") or "",
            chunk.get("source") or "",
            " ".join(chunk.get("concepts") or [] if isinstance(chunk.get("concepts"), list) else [str(chunk.get("concepts"))]),
        ]
        return _normalize_arabic(" ".join(p for p in parts if p))

    def upsert(self, chunk: dict, embedding: list):
        session = self.Session()
        try:
            doc_key = self._generate_doc_key(chunk)
            existing = session.execute(
                select(KnowledgeChunk).where(KnowledgeChunk.doc_key == doc_key)
            ).scalar_one_or_none()
            values = self._metadata_values(chunk)
            stext = self._search_text(chunk)
            if existing:
                existing.doc_path = chunk.get("doc_path", existing.doc_path)
                existing.doc_type = chunk.get("doc_type", values["source_type"]) or existing.doc_type
                existing.title = chunk.get("title", existing.title)
                existing.text = chunk.get("text", existing.text)
                existing.source = chunk.get("source", existing.source)
                existing.page = chunk.get("page", existing.page)
                existing.embedding = np.array(embedding, dtype=np.float32).tolist()
                existing.search_text = stext
                existing.search_vector = func.to_tsvector("simple", stext)
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                new_chunk = KnowledgeChunk(
                    doc_key=doc_key,
                    doc_path=chunk.get("doc_path", ""),
                    doc_type=chunk.get("doc_type", values["source_type"]),
                    title=chunk.get("title", ""),
                    text=chunk.get("text", ""),
                    source=chunk.get("source", ""),
                    page=chunk.get("page"),
                    embedding=np.array(embedding, dtype=np.float32).tolist(),
                    search_text=stext,
                    search_vector=func.to_tsvector("simple", stext),
                    **values,
                )
                session.add(new_chunk)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def sync_metadata(self, chunks):
        """يحدّث metadata للقطع الموجودة دون إعادة حساب embeddings."""
        session = self.Session()
        try:
            keys = [self._generate_doc_key(c) for c in chunks]
            rows = session.execute(
                select(KnowledgeChunk).where(KnowledgeChunk.doc_key.in_(keys))
            ).scalars().all()
            by_key = {row.doc_key: row for row in rows}
            updated = 0
            for chunk, key in zip(chunks, keys):
                row = by_key.get(key)
                if not row:
                    continue
                values = self._metadata_values(chunk)
                row.doc_path = chunk.get("doc_path", row.doc_path)
                row.doc_type = chunk.get("doc_type", values["source_type"]) or row.doc_type
                row.title = chunk.get("title", row.title)
                row.text = chunk.get("text", row.text)
                row.source = chunk.get("source", row.source)
                row.page = chunk.get("page", row.page)
                stext = self._search_text({**{"title": row.title, "text": row.text, "source": row.source, "lesson": row.lesson, "unit": row.unit, "concepts": row.concepts}, **chunk})
                row.search_text = stext
                row.search_vector = func.to_tsvector("simple", stext)
                for field, value in values.items():
                    setattr(row, field, value)
                updated += 1
            session.commit()
            return updated
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _generate_doc_key(self, chunk: dict) -> str:
        import hashlib
        # حافظ على صيغة المفتاح التاريخية حتى لا تتسبب ترقية metadata في إعادة
        # embedding لكل القطع الموجودة.
        raw = f"{chunk.get('source','')}|{chunk.get('title','')}|{chunk.get('page','')}|{chunk.get('text','')[:200]}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:32]

    def count(self) -> int:
        session = self.Session()
        try:
            return session.query(KnowledgeChunk).count()
        finally:
            session.close()

    def existing_doc_keys(self) -> set:
        session = self.Session()
        try:
            return set(session.execute(select(KnowledgeChunk.doc_key)).scalars().all())
        finally:
            session.close()

    def prune_not_in(self, active_doc_keys: set[str]) -> int:
        """يحذف chunks لم تعد ضمن corpus الحالي بعد إعادة التقسيم/الـingestion."""
        session = self.Session()
        try:
            keys = list(active_doc_keys)
            if not keys:
                deleted = session.query(KnowledgeChunk).delete()
            else:
                # تنفيذ على دفعات لتفادي استعلام IN ضخم عند توسع القاعدة.
                existing = set(session.execute(select(KnowledgeChunk.doc_key)).scalars().all())
                stale = list(existing - active_doc_keys)
                deleted = 0
                for start in range(0, len(stale), 1000):
                    batch = stale[start:start + 1000]
                    if batch:
                        deleted += session.query(KnowledgeChunk).filter(KnowledgeChunk.doc_key.in_(batch)).delete(synchronize_session=False)
            session.commit()
            return deleted
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def clear(self):
        session = self.Session()
        try:
            session.query(KnowledgeChunk).delete()
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
