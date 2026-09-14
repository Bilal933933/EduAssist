"""واجهة ذاكرة المدرس — النموذج المعياري M1/M2."""
from typing import Optional

from fastapi import APIRouter, Query

from app.core.errors import AppError
from app.core.response import ok
from app.core.validation import validate_grade, validate_teacher_id
from app.repositories import TeacherMemoryStore
from app.schemas.memory import InteractionUpdate, ManualUpdate, MistakeBody

router = APIRouter(prefix="/api/memory", tags=["teacher-memory"])


@router.get("/grades/catalog")
def grades_catalog():
    try:
        return ok({"grades": TeacherMemoryStore().list_grades()})
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.get("")
def get_memory_default(grade: Optional[str] = Query(None)):
    return _get("default", grade)


@router.get("/{teacher_id}")
def get_memory(teacher_id: str, grade: Optional[str] = Query(None)):
    return _get(teacher_id, grade)


def _catalog_or_none() -> list[str] | None:
    try:
        grades = TeacherMemoryStore().list_grades()
        return [g.get("code") or g.get("label_ar") for g in grades if isinstance(g, dict)] or None
    except Exception:
        return None


def _get(teacher_id: str, grade: str | None):
    teacher_id = validate_teacher_id(teacher_id)
    grade = validate_grade(grade, catalog=_catalog_or_none())
    try:
        store = TeacherMemoryStore()
        profile = store.get_profile(teacher_id)
        prompt_block = store.get_prompt_block(teacher_id, current_grade=grade)
        return ok({
            "profile": profile,
            "prompt_block": prompt_block,
            "mistakes_for_grade": store.list_mistakes(teacher_id, grade=grade),
            "recent_for_grade": store.list_recent_lessons(teacher_id, grade=grade),
            "filter_grade": grade,
        })
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.put("")
def update_memory_manual(body: ManualUpdate):
    body.teacher_id = validate_teacher_id(body.teacher_id)
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
        return ok({"ok": True, "profile": profile})
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.post("/interaction")
def update_from_interaction(body: InteractionUpdate):
    body.teacher_id = validate_teacher_id(body.teacher_id)
    body.grade = validate_grade(body.grade)
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
        return ok({"ok": True, "profile": profile})
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.post("/mistakes")
def add_mistake(body: MistakeBody):
    from app.core.validation import validate_topic

    body.teacher_id = validate_teacher_id(body.teacher_id)
    body.mistake = validate_topic(body.mistake)
    body.grade = validate_grade(body.grade)
    try:
        profile = TeacherMemoryStore().add_mistake(
            body.teacher_id,
            mistake=body.mistake,
            topic=body.topic,
            grade=body.grade,
        )
        return ok({"ok": True, "profile": profile})
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.get("/{teacher_id}/mistakes")
def list_mistakes(teacher_id: str, grade: Optional[str] = Query(None)):
    teacher_id = validate_teacher_id(teacher_id)
    grade = validate_grade(grade)
    try:
        return ok({"mistakes": TeacherMemoryStore().list_mistakes(teacher_id, grade=grade)})
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.get("/{teacher_id}/lessons")
def list_lessons(teacher_id: str, grade: Optional[str] = Query(None)):
    teacher_id = validate_teacher_id(teacher_id)
    grade = validate_grade(grade)
    try:
        return ok({"recent_lessons": TeacherMemoryStore().list_recent_lessons(teacher_id, grade=grade)})
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.delete("/{teacher_id}")
def reset_memory(teacher_id: str = "default"):
    try:
        deleted = TeacherMemoryStore().reset(teacher_id)
        return ok({"ok": True, "deleted": deleted})
    except Exception:
        raise AppError("INTERNAL_ERROR")
