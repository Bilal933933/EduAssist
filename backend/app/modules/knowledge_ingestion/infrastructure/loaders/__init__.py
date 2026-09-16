"""محملات المصادر — كتب content/ مع metadata.json لكل كتاب/مرجع."""
import os
from pathlib import Path

from app.modules.knowledge_ingestion.infrastructure.loaders.knowledge_loader import load_knowledge_sections
from app.modules.knowledge_ingestion.infrastructure.loaders.book_loader import (
    load_book,
    _load_simple_book,
    _iter_book_dirs,
)

# backend/data (قديم) — backend/content و content/ الجذر (الحي)
_BACKEND = Path(__file__).resolve().parents[5]
DATA_DIR = str(_BACKEND / "data")
BOOKS_DIR = os.path.join(DATA_DIR, "books")
KNOWLEDGE_PATH = os.path.join(DATA_DIR, "grammar_knowledge.md")
CONTENT_DIR = str(_BACKEND / "content")
PROJECT_CONTENT_DIR = str(_BACKEND.parent / "content")


def load_book_units():
    """يجمع المصادر من المسار الحي الوحيد (جذر المشروع)، مع fallback لحاوية Docker."""
    sections = []
    # المصدر الوحيد: content/ الجذر. backend/content للتوافق مع Docker فقط.
    # كان الكود السابق يلف على الاثنين معاً فيسبب تكرار كل قسم مرتين.
    cdir = PROJECT_CONTENT_DIR if os.path.exists(PROJECT_CONTENT_DIR) else CONTENT_DIR
    if not os.path.exists(cdir):
        return sections
    for book_dir in _iter_book_dirs(cdir):
        if "backup" in book_dir.lower():
            continue
        segments = os.path.relpath(book_dir, cdir).split(os.sep)
        loaded = _load_simple_book(book_dir, segments, content_root=cdir)
        print(f"  content/{'/'.join(segments)}: {len(loaded)} قسماً")
        sections.extend(loaded)
    return sections


def load_all_sources():
    """مصادر المنهج والمراجع مع metadata موحدة."""
    return load_book_units()


__all__ = [
    "load_all_sources",
    "load_book_units",
    "load_knowledge_sections",
    "load_book",
    "DATA_DIR",
    "BOOKS_DIR",
    "KNOWLEDGE_PATH",
    "CONTENT_DIR",
    "PROJECT_CONTENT_DIR",
]
