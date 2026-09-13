import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sqlalchemy import func, select
from src.knowledge.models import KnowledgeChunk
from src.knowledge.search import _normalize_arabic
from src.knowledge.store import VectorStore

BATCH = 500
vs = VectorStore()
session = vs.Session()
try:
    q = session.execute(
        select(KnowledgeChunk).where(
            (KnowledgeChunk.search_text.is_(None)) | (KnowledgeChunk.search_text == "")
        ).limit(BATCH)
    ).scalars().all()
    total = 0
    while q:
        for row in q:
            parts = [
                row.title or "",
                (row.text or "")[:2000],
                row.lesson or "",
                row.unit or "",
                row.source or "",
                " ".join(row.concepts or [] if isinstance(row.concepts, list) else [str(row.concepts)]),
            ]
            stext = _normalize_arabic(" ".join(p for p in parts if p))
            row.search_text = stext
            row.search_vector = func.to_tsvector("simple", stext)
        session.commit()
        total += len(q)
        print(f"backfilled {total}")
        q = session.execute(
            select(KnowledgeChunk).where(
                (KnowledgeChunk.search_text.is_(None)) | (KnowledgeChunk.search_text == "")
            ).limit(BATCH)
        ).scalars().all()
    print(f"done total={total}")
finally:
    session.close()
