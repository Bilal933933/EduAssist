import os

from src.loader.knowledge_loader import load_knowledge_sections
from src.loader.book_loader import load_book, _load_simple_book, _iter_book_dirs

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BOOKS_DIR = os.path.join(DATA_DIR, "books")
KNOWLEDGE_PATH = os.path.join(DATA_DIR, "grammar_knowledge.md")
CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "content")
PROJECT_CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "content")


def load_book_units():
    """يجمع المصادر مع تمرير metadata.json الحقيقي لكل كتاب/مرجع."""
    sections = []
    seen_dirs = set()
    for cdir in [PROJECT_CONTENT_DIR, CONTENT_DIR]:
        if not os.path.exists(cdir):
            continue
        real = os.path.realpath(cdir)
        if real in seen_dirs:
            continue
        seen_dirs.add(real)
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
