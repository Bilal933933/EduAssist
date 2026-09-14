from fastapi import APIRouter, Depends

from app.core.errors import AppError
from app.core.response import ok
from app.dependencies import get_gemini_client, get_indexer
from app.modules.knowledge_ingestion.application.run_indexing_use_case import run_indexing

router = APIRouter(prefix="/api", tags=["reindex"])


@router.post("/reindex")
async def reindex_endpoint(indexer=Depends(get_indexer), client=Depends(get_gemini_client)):
    """زر يدوي: يعيد فهرسة المصادر الجديدة — إضافة/تحديث فقط، بلا حذف."""
    try:
        return ok(run_indexing(indexer, client, prune=False))
    except AppError:
        raise
    except Exception:
        raise AppError("REINDEX_FAILED")
