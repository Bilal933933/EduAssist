"""واجهة ذاكرة المدرس — HTTP فقط (M1/M2)."""
from typing import Optional

from fastapi import APIRouter, Query

from app.core.errors import AppError
from app.core.response import ok
from app.modules.memory.schemas import InteractionUpdate, ManualUpdate, MistakeBody
from app.modules.memory.service import MemoryService

router = APIRouter(prefix="/api/memory", tags=["teacher-memory"])
_service = MemoryService()


@router.get("/grades/catalog")
def grades_catalog():
    try:
        return ok(_service.list_grades())
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.get("")
def get_memory_default(grade: Optional[str] = Query(None)):
    try:
        return ok(_service.get_memory("default", grade))
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.get("/{teacher_id}")
def get_memory(teacher_id: str, grade: Optional[str] = Query(None)):
    try:
        return ok(_service.get_memory(teacher_id, grade))
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.put("")
def update_memory_manual(body: ManualUpdate):
    try:
        return ok(_service.update_manual(body))
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.post("/interaction")
def update_from_interaction(body: InteractionUpdate):
    try:
        return ok(_service.update_interaction(body))
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.post("/mistakes")
def add_mistake(body: MistakeBody):
    try:
        return ok(_service.add_mistake(body))
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.get("/{teacher_id}/mistakes")
def list_mistakes(teacher_id: str, grade: Optional[str] = Query(None)):
    try:
        return ok(_service.list_mistakes(teacher_id, grade))
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.get("/{teacher_id}/lessons")
def list_lessons(teacher_id: str, grade: Optional[str] = Query(None)):
    try:
        return ok(_service.list_lessons(teacher_id, grade))
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.delete("/{teacher_id}")
def reset_memory(teacher_id: str = "default"):
    try:
        return ok(_service.reset(teacher_id))
    except Exception:
        raise AppError("INTERNAL_ERROR")
