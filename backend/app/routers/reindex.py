from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_gemini_client, get_indexer
from app.modules.knowledge_ingestion.application.run_indexing_use_case import (
    run_indexing,
)

router = APIRouter(prefix="/api", tags=["reindex"])

@router.post("/reindex")
async def reindex_endpoint(indexer=Depends(get_indexer), client=Depends(get_gemini_client)):
    """زر يدوي: يعيد فهرسة المصادر الجديدة (FR-06) — إضافة/تحديث فقط، بلا حذف."""
    try:
        return run_indexing(indexer, client, prune=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
