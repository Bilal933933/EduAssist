"""إحصائيات الفهرسة — قدرة منصة (HTTP فقط)."""
from fastapi import APIRouter

from app.core.response import ok
from app.dependencies import get_kb

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
async def stats_endpoint():
    try:
        kb = get_kb()
        return ok({
            "total_chunks": kb.vector_service.count(),
            "indexed": True,
            "by_subject": kb.vector_service.counts_by_subject(),
        })
    except Exception:
        return ok({"total_chunks": 0, "indexed": False, "by_subject": []})
