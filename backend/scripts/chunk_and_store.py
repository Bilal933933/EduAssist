"""تقطيع مهيكل لكتب content/ وتخزينها في knowledge_chunks (جدول واحد: نصي + دلالي).

المعمارية: اكتشاف ← تحقق أقسام ← تقطيع بحدود ← تحقق مقاطع ← تخزين ← تقرير.
- يتجاهل مجلدات #UXXXX المشفرة (مكررة من نفس الكتاب).
- يرفض الأقسام الفارغة والناقصة metadata بدل تخزينها صامتًا.
- --dry-run للتحقق بلا كتابة.

الاستخدام:
    cd backend && python scripts/chunk_and_store.py --book-dir "<مجلد الكتاب>" --content-root "<content>"
    cd backend && python scripts/chunk_and_store.py --all --content-root "<content>" --dry-run
"""
import argparse
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from app.modules.knowledge_ingestion.infrastructure.loaders.book_loader import (
    _iter_book_dirs,
    _load_simple_book,
)
from app.knowledge.store import VectorStore

HEADERS = [("##", "section")]
SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1600, chunk_overlap=240, separators=["\n\n", "\n", "؟", ".", " ", ""]
)
MIN_TOKENS, MAX_TOKENS = 300, 500
ENCODED_DIR = re.compile(r"#U[0-9A-Fa-f]{4,6}")
ARABIC = re.compile(r"[\u0600-\u06FF]")


def is_encoded_duplicate(path: str) -> bool:
    """المجلدات المشفرة #UXXXX مكررة من نفس الكتاب — تُتجاهل."""
    return bool(ENCODED_DIR.search(path))


def validate_section(section: dict) -> str | None:
    """يعيد سبب الرفض أو None عند القبول."""
    if not (section.get("text") or "").strip():
        return "نص فارغ"
    if not section.get("subject"):
        return "subject مفقود"
    if not section.get("book_id"):
        return "book_id مفقود"
    return None


def validate_chunk(chunk: dict, report: dict) -> None:
    """تحذيرات غير رافضة: خارج الحدود يُسجل في التقرير."""
    n = chunk.get("chunk_token_count", 0)
    if n > MAX_TOKENS:
        report["over_max"] += 1
    elif n < 60:
        report["tiny"] += 1


def chunk_section(section: dict, report: dict) -> list[dict]:
    reason = validate_section(section)
    if reason:
        report["rejected_sections"] += 1
        report.setdefault("reject_reasons", {}).setdefault(reason, 0)
        report["reject_reasons"][reason] += 1
        return []
    try:
        docs = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS).split_text(section.get("text", ""))
        texts = [d.page_content for d in docs] or [section.get("text", "")]
    except Exception as e:
        report["split_errors"] += 1
        print(f"  [خطأ تقسيم] {section.get('title', '?')}: {e}")
        return []
    chunks = []
    for text in texts:
        parts = SPLITTER.split_text(text) if len(text.split()) > MAX_TOKENS else [text]
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            c = dict(section)
            c["text"] = part
            c["chunk_index"] = i
            c["chunk_token_count"] = len(part.split())
            c["parent_section"] = "|".join([
                str(c.get("book_id") or ""),
                str(c.get("unit") or ""),
                str(c.get("lesson") or c.get("title") or ""),
            ])
            validate_chunk(c, report)
            chunks.append(c)
    return chunks


def process_book(book_dir: str, content_root: str, store: VectorStore | None, report: dict) -> int:
    if is_encoded_duplicate(book_dir):
        report["skipped_encoded"] += 1
        return 0
    try:
        segments = os.path.relpath(book_dir, content_root).replace(os.sep, "/").split("/")
        sections = _load_simple_book(book_dir, segments, content_root)
    except Exception as e:
        report["book_errors"] += 1
        print(f"  [خطأ كتاب] {book_dir}: {e}")
        return 0
    n = 0
    for section in sections:
        for chunk in chunk_section(section, report):
            if store is not None:
                try:
                    store.upsert(chunk, None)  # نصي وبنية الآن، والتضمين لاحقًا
                except Exception as e:
                    report["store_errors"] += 1
                    print(f"  [خطأ تخزين] {chunk.get('title', '?')}: {e}")
                    continue
            n += 1
    report["books_ok"] += 1
    return n


def main() -> int:
    parser = argparse.ArgumentParser(description="تقطيع مهيكل + تخزين (جدول واحد)")
    parser.add_argument("--book-dir", default=None)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="تحقق فقط بلا كتابة")
    parser.add_argument("--content-root", default=os.path.join("..", "content"))
    args = parser.parse_args()

    report = {"books_ok": 0, "rejected_sections": 0, "over_max": 0, "tiny": 0,
              "split_errors": 0, "book_errors": 0, "store_errors": 0, "skipped_encoded": 0}
    store = None if args.dry_run else VectorStore()
    total = 0
    if args.all:
        for book_dir in _iter_book_dirs(args.content_root):
            n = process_book(book_dir, args.content_root, store, report)
            if n:
                print(f"  {book_dir}: {n}")
            total += n
    elif args.book_dir:
        total = process_book(args.book_dir, args.content_root, store, report)
    else:
        print("حدد --book-dir أو --all")
        return 1

    print(f"تم: {total} مقطع | كتب سليمة: {report['books_ok']} | أقسام مرفوضة: {report['rejected_sections']}")
    print(f"تجاوز الحد: {report['over_max']} | صغيرة جدًا: {report['tiny']} | أخطاء: {report['split_errors'] + report['book_errors'] + report['store_errors']} | مكررة متجاهلة: {report['skipped_encoded']}")
    if report.get("reject_reasons"):
        print(f"أسباب الرفض: {report['reject_reasons']}")
    if report["book_errors"] or report["store_errors"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
