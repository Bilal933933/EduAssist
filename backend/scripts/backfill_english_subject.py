"""ردم وسم المادة للكتاب الإنجليزي غير الموسوم (296 مقتطفاً، subject/stage فارغان).

السبب: دخل من مسار قديم بلا doc_path ففشل استدلال المسار، وكان يتسرب
لنتائج مساعد العربية. يُنفَّذ مرة واحدة ويُسجَّل في اللوج (قابل لإعادة التشغيل بأمان).
"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sqlalchemy import select
from app.models.knowledge_chunk import KnowledgeChunk
from app.knowledge.store import VectorStore

ENGLISH_SOURCE = "بروفيشنال في تأسيس ومهارات اللغة الإنجليزية للمرحلة الإعدادية"

vs = VectorStore()
session = vs.Session()
try:
    rows = session.execute(
        select(KnowledgeChunk).where(
            KnowledgeChunk.source == ENGLISH_SOURCE,
            KnowledgeChunk.subject.is_(None),
        )
    ).scalars().all()
    print(f"found unclassified english rows: {len(rows)}")
    for row in rows:
        row.subject = "اللغة الإنجليزية"
        if not row.stage:
            row.stage = "prep"  # من عنوان الكتاب: للمرحلة الإعدادية
    session.commit()
    print(f"backfilled subject for {len(rows)} rows (source={ENGLISH_SOURCE})")
    remaining = session.execute(
        select(KnowledgeChunk).where(
            KnowledgeChunk.source == ENGLISH_SOURCE,
            KnowledgeChunk.subject.is_(None),
        )
    ).scalars().all()
    print(f"remaining unclassified: {len(remaining)}")
finally:
    session.close()
