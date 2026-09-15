from app.knowledge.vector_service import VectorService
from app.modules.knowledge_ingestion.infrastructure.loaders import load_all_sources
from app.modules.knowledge_ingestion.infrastructure.loaders.chunker import chunk_sections
from app.modules.knowledge_ingestion.infrastructure.loaders.semantic_chunker import chunk_sections_semantic

class IndexerService:
    """Domain service — فصل indexing عن retrieval. مسؤول عن documents → chunks → embeddings → DB."""

    def __init__(self, vector_service: VectorService | None = None):
        self.vs = vector_service or VectorService()

    def load_sections(self):
        return load_all_sources()

    def chunk(self, sections, use_semantic: bool = True):
        if use_semantic:
            try:
                return chunk_sections_semantic(sections)
            except Exception:
                return chunk_sections(sections)
        return chunk_sections(sections)

    def sync_metadata(self, chunks) -> int:
        return self.vs.sync_metadata(chunks)

    def existing_keys(self) -> set:
        return self.vs.existing_doc_keys()

    def load_progress(self) -> tuple:
        """يعيد (count, existing_keys) بنفس دلالة _load_progress في indexer.py القديم."""
        return self.count(), self.existing_keys()

    def prune_stale(self, active_keys: set) -> int:
        """غلاف رقيق فوق VectorStore.prune_not_in — يحذف القطع خارج corpus الحالي."""
        return self.vs.prune_not_in(active_keys)

    @staticmethod
    def embedding_text(chunk: dict) -> str:
        """تمثيل embedding غني بالـhierarchy — منقول حرفياً من _embedding_text في indexer.py."""
        labels = [
            chunk.get("subject"),
            chunk.get("stage"),
            chunk.get("grade"),
            chunk.get("branch"),
            chunk.get("unit"),
            chunk.get("lesson"),
            ", ".join(chunk.get("concepts") or []) if isinstance(chunk.get("concepts"), list) else chunk.get("concepts"),
        ]
        context = " | ".join(str(x).strip() for x in labels if x and str(x).strip())
        title = chunk.get("title") or ""
        source = chunk.get("source") or ""
        prefix = f"{context}\n{title}\n{source}" if context else f"{title}\n{source}"
        return f"{prefix}\n{chunk.get('text', '')}".strip()

    def upsert(self, chunk: dict, vector: list):
        self.vs.upsert(chunk, vector)

    def count(self) -> int:
        return self.vs.count()
