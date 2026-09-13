"""واجهة ذاكرة المدرس — النموذج المعياري M1/M2."""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.storage.teacher_memory import TeacherMemoryStore

router = APIRouter(prefix="/api/memory", tags=["teacher-memory"])


class ManualUpdate(BaseModel):
    teacher_id: str = "default"
    display_name: Optional[str] = None
    preferred_grades: Optional[List[str]] = None
    style_notes: Optional[List[str]] = None
    summary: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    class_context: Optional[str] = None
    common_mistakes: Optional[List[Any]] = None
    recent_lessons: Optional[List[Any]] = None


class InteractionUpdate(BaseModel):
    teacher_id: str = "default"
    grade: Optional[str] = None
    topic: Optional[str] = None
    style_hint: Optional[str] = None
    question: Optional[str] = None
    is_lesson_prep: bool = False
    mistake_text: Optional[str] = None
    thread_id: Optional[int] = None


class MistakeBody(BaseModel):
    teacher_id: str = "default"
    mistake: str
    topic: Optional[str] = None
    grade: Optional[str] = None


@router.get("/grades/catalog")
def grades_catalog():
    """قائمة الصفوف المعيارية."""
    try:
        return {"grades": TeacherMemoryStore().list_grades()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
def get_memory_default(grade: Optional[str] = Query(None)):
    return _get("default", grade)


@router.get("/{teacher_id}")
def get_memory(teacher_id: str, grade: Optional[str] = Query(None)):
    return _get(teacher_id, grade)


def _get(teacher_id: str, grade: str | None):
    try:
        store = TeacherMemoryStore()
        profile = store.get_profile(teacher_id)
        prompt_block = store.get_prompt_block(teacher_id, current_grade=grade)
        return {
            "profile": profile,
            "prompt_block": prompt_block,
            "mistakes_for_grade": store.list_mistakes(teacher_id, grade=grade),
            "recent_for_grade": store.list_recent_lessons(teacher_id, grade=grade),
            "filter_grade": grade,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("")
def update_memory_manual(body: ManualUpdate):
    try:
        profile = TeacherMemoryStore().set_manual(
            body.teacher_id,
            display_name=body.display_name,
            preferred_grades=body.preferred_grades,
            style_notes=body.style_notes,
            summary=body.summary,
            preferences=body.preferences,
            class_context=body.class_context,
            common_mistakes=body.common_mistakes,
            recent_lessons=body.recent_lessons,
        )
        return {"ok": True, "profile": profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interaction")
def update_from_interaction(body: InteractionUpdate):
    try:
        profile = TeacherMemoryStore().update_from_interaction(
            body.teacher_id,
            grade=body.grade,
            topic=body.topic,
            style_hint=body.style_hint,
            question=body.question,
            is_lesson_prep=body.is_lesson_prep,
            mistake_text=body.mistake_text,
            thread_id=body.thread_id,
        )
        return {"ok": True, "profile": profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mistakes")
def add_mistake(body: MistakeBody):
    try:
        profile = TeacherMemoryStore().add_mistake(
            body.teacher_id,
            mistake=body.mistake,
            topic=body.topic,
            grade=body.grade,
        )
        return {"ok": True, "profile": profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{teacher_id}/mistakes")
def list_mistakes(teacher_id: str, grade: Optional[str] = Query(None)):
    try:
        return {"mistakes": TeacherMemoryStore().list_mistakes(teacher_id, grade=grade)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{teacher_id}/lessons")
def list_lessons(teacher_id: str, grade: Optional[str] = Query(None)):
    try:
        return {
            "recent_lessons": TeacherMemoryStore().list_recent_lessons(
                teacher_id, grade=grade
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{teacher_id}")
def reset_memory(teacher_id: str = "default"):
    try:
        deleted = TeacherMemoryStore().reset(teacher_id)
        return {"ok": True, "deleted": deleted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
