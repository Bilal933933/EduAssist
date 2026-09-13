import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# يسمح بالتشغيل المباشر python src/indexer.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from google import genai

try:
    from src.loader import load_all_sources
    from src.loader.chunker import chunk_sections
    from src.knowledge.embeddings import embed_batches, BATCH_SIZE
    from src.knowledge.vector_service import VectorService
except ImportError:
    from loader import load_all_sources
    from loader.chunker import chunk_sections
    from knowledge.embeddings import embed_batches, BATCH_SIZE
    from knowledge.vector_service import VectorService

load_dotenv()

# تهيئة خدمة قاعدة البيانات المتجهية
vector_service = VectorService()


def _load_progress():
    """يعيد عدد القطع المفهرسة سابقاً ومفاتيحها (للاستئناف الآمن)."""
    count = vector_service.count()
    existing_keys = vector_service.existing_doc_keys()
    return count, existing_keys


def _save(chunks, vectors):
    """يحفظ القطع والمتجهات في قاعدة البيانات."""
    for chunk, vector in zip(chunks, vectors):
        vector_service.upsert(chunk, vector)


def _embedding_text(chunk: dict) -> str:
    """يبني تمثيل embedding غنيًا بالـhierarchy دون تغيير النص المعروض للمدرس."""
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


def index():
    """المنسق: يحمّل المصادر، يقسمها، يضمّنها بحفظ تدريجي، ثم يطبع الملخص."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY غير مضبوطة في .env")

    sections = load_all_sources()
    chunks = chunk_sections(sections)
    texts = [_embedding_text(c) for c in chunks]

    done, existing_keys = _load_progress()

    # ترحيل metadata للقطع الموجودة دون إعادة حساب embeddings.
    synced = vector_service.sync_metadata(chunks)
    print(f"تم تحديث metadata لـ {synced} قطعة موجودة")

    # تحديد القطع الجديدة التي لم يتم فهرستها بعد
    new_chunks = []
    new_texts = []
    for i, chunk in enumerate(chunks):
        doc_key = vector_service._generate_doc_key(chunk)
        if doc_key not in existing_keys:
            new_chunks.append(chunk)
            new_texts.append(texts[i])
    
    if not new_chunks:
        print("جميع القطع مفهرسة بالفعل.")
        return
    
    print(f"استئناف: {done} قطعة مفهرسة سابقاً، يتبقى {len(new_chunks)} قطعة جديدة")

    for batch_vectors in embed_batches(client, new_texts, BATCH_SIZE):
        batch_chunks = new_chunks[:len(batch_vectors)]
        for chunk, vector in zip(batch_chunks, batch_vectors):
            vector_service.upsert(chunk, vector)
        done += len(batch_vectors)
        new_chunks = new_chunks[len(batch_vectors):]
        new_texts = new_texts[len(batch_vectors):]
        print(f"  تقدم: {done}/{len(chunks)} قطعة", end="\r")
        time.sleep(0.5)

    active_keys = {vector_service._generate_doc_key(c) for c in chunks}
    deleted = vector_service.prune_not_in(active_keys)
    if deleted:
        print(f"تم حذف {deleted} قطعة قديمة لم تعد ضمن corpus الحالي")

    total_chunks = vector_service.count()
    print(f"\nتمت فهرسة {total_chunks} قطعة من {len(sections)} قسماً")
    print(f"(المتجهات محفوظة في قاعدة البيانات المتجهية)")


if __name__ == "__main__":
    index()