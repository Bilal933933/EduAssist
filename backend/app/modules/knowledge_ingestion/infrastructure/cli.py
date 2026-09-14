"""نقطة دخول CLI للفهرسة — بديل src/indexer.py على المسار الموحد (مع حذف)."""

import argparse
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from app.dependencies import get_gemini_client, get_indexer
from app.modules.knowledge_ingestion.application.run_indexing_use_case import (
    run_indexing,
)


def main(prune: bool = True) -> int:
    """يبني العميل والخدمة (Composition Root) ويشغّل الفهرسة مع طباعة التقدم."""
    indexer = get_indexer()
    client = get_gemini_client()

    def on_progress(done: int) -> None:
        print(f"  تقدم: {done} قطعة")
        time.sleep(0.5)

    result = run_indexing(indexer, client, prune=prune, on_progress=on_progress)
    print(result["message"])
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="فهرسة مصادر المعرفة (المسار الموحد)")
    parser.add_argument("--no-prune", action="store_true", help="تخطي حذف القطع القديمة")
    args = parser.parse_args()
    sys.exit(main(prune=not args.no_prune))
