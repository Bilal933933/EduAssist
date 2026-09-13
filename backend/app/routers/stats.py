from fastapi import APIRouter

from app.dependencies import get_kb

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
async def stats_endpoint():
    try:
        return {"total_chunks": get_kb().vector_service.count(), "indexed": True}
    except Exception:
        # إن لم تكن قاعدة المعرفة مهيأة نعيد رداً لطيفاً بدل خطأ 500
        return {"total_chunks": 0, "indexed": False}
