from src.loader import load_all_sources
from src.loader.chunker import chunk_sections
from src.knowledge.vector_service import VectorService
from src.loader.semantic_chunker import chunk_sections_semantic
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

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

    def upsert(self, chunk: dict, vector: list):
        self.vs.upsert(chunk, vector)

    def count(self) -> int:
        return self.vs.count()
