from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_kb

router = APIRouter(prefix="/api", tags=["reindex"])

@router.post("/reindex")
async def reindex_endpoint(kb=Depends(get_kb)):
    """زر يدوي: يعيد فهرسة المصادر الجديدة (FR-06)."""
    try:
        from src.loader import load_all_sources
        from src.loader.chunker import chunk_sections
        from src.knowledge.embeddings import embed_batches, BATCH_SIZE
        from src.knowledge.vector_service import VectorService
        from google import genai
        import os
        from dotenv import load_dotenv
        load_dotenv()
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        sections = load_all_sources()
        chunks = chunk_sections(sections)
        texts = [f"{c.get('source','')} — {c['title']}: {c['text']}" for c in chunks]
        kb.vector_service.sync_metadata(chunks)
        existing = kb.vector_service.existing_doc_keys()
        new_chunks = []
        new_texts = []
        for i, c in enumerate(chunks):
            if kb.vector_service._generate_doc_key(c) not in existing:
                new_chunks.append(c)
                new_texts.append(texts[i])
        if not new_chunks:
            return {"indexed": 0, "total": kb.vector_service.count(), "message": "جميع القطع مفهرسة"}
        added = 0
        for batch_vectors in embed_batches(client, new_texts, BATCH_SIZE):
            for chunk, vec in zip(new_chunks[:len(batch_vectors)], batch_vectors):
                kb.vector_service.upsert(chunk, vec)
            added += len(batch_vectors)
            new_chunks = new_chunks[len(batch_vectors):]
        return {"indexed": added, "total": kb.vector_service.count(), "message": f"تمت فهرسة {added} قطعة جديدة"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
