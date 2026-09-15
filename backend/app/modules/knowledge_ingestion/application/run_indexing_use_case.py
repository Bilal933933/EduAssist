"""المسار الموحد للفهرسة — يستهلكه زر الواجهة (بلا حذف) وسكربت CLI (مع حذف).

يستدعي IndexerService ولا يعيد تنفيذ منطقه: تحميل ← تقسيم ← نص هرمي
← ترشيح الجديد ← تضمين ← تخزين ← حذف اختياري.
"""

from app.modules.knowledge_ingestion.application.indexer_service import IndexerService
from app.knowledge.embeddings import BATCH_SIZE, embed_batches


def run_indexing(indexer: IndexerService, client, prune: bool = False,
                 embed_fn=None, on_progress=None) -> dict:
    """يفهرس القطع الجديدة تفاضلياً. يعيد {indexed, total, deleted, message}.

    prune=False افتراضياً (زر الواجهة: إضافة/تحديث فقط) — الحذف opt-in
    للـ CLI الواعي فقط، حتى لا يحذف الزر بصمت محتوى حياً.
    """
    embed = embed_fn or embed_batches
    sections = indexer.load_sections()
    chunks = indexer.chunk(sections)
    indexer.sync_metadata(chunks)
    _, existing = indexer.load_progress()
    new_chunks = []
    new_texts = []
    for chunk in chunks:
        if indexer.vs._generate_doc_key(chunk) not in existing:
            new_chunks.append(chunk)
            new_texts.append(indexer.embedding_text(chunk))
    added = 0
    for batch_vectors in (embed(client, new_texts, BATCH_SIZE) if new_chunks else []):
        for chunk, vector in zip(new_chunks[:len(batch_vectors)], batch_vectors):
            indexer.upsert(chunk, vector)
        added += len(batch_vectors)
        new_chunks = new_chunks[len(batch_vectors):]
        if on_progress:
            on_progress(added)
    deleted = 0
    if prune:
        active_keys = {indexer.vs._generate_doc_key(c) for c in chunks}
        deleted = indexer.prune_stale(active_keys)
    total = indexer.count()
    if added == 0 and deleted == 0:
        message = "جميع القطع مفهرسة"
    else:
        message = f"تمت فهرسة {added} قطعة جديدة"
        if deleted:
            message += f" وحذف {deleted} قطعة قديمة"
    return {"indexed": added, "total": total, "deleted": deleted, "message": message}
