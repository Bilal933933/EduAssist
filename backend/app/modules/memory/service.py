"""خدمة الذاكرة — Application orchestration فوق TeacherMemoryStore.

الـ Router يمرر فقط. كل استدعاءات المخزن الـ 10 كانت في الـ endpoint
أصبحت هنا: تحقق ← مخزن ← نتيجة.
"""
from src.storage.teacher_memory import TeacherMemoryStore

from app.core.validation import validate_teacher_id
from app.modules.cards.validation import validate_topic
from app.modules.memory.validation import validate_grade


def _catalog_or_none() -> list[str] | None:
    try:
        grades = TeacherMemoryStore().list_grades()
        return [g.get("code") or g.get("label_ar") for g in grades if isinstance(g, dict)] or None
    except Exception:
        return None


class MemoryService:
    def list_grades(self) -> dict:
        return {"grades": TeacherMemoryStore().list_grades()}

    def get_memory(self, teacher_id: str, grade: str | None) -> dict:
        teacher_id = validate_teacher_id(teacher_id)
        grade = validate_grade(grade, catalog=_catalog_or_none())
        store = TeacherMemoryStore()
        return {
            "profile": store.get_profile(teacher_id),
            "prompt_block": store.get_prompt_block(teacher_id, current_grade=grade),
            "mistakes_for_grade": store.list_mistakes(teacher_id, grade=grade),
            "recent_for_grade": store.list_recent_lessons(teacher_id, grade=grade),
            "filter_grade": grade,
        }

    def update_manual(self, body) -> dict:
        teacher_id = validate_teacher_id(body.teacher_id)
        profile = TeacherMemoryStore().set_manual(
            teacher_id,
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

    def update_interaction(self, body) -> dict:
        teacher_id = validate_teacher_id(body.teacher_id)
        grade = validate_grade(body.grade)
        profile = TeacherMemoryStore().update_from_interaction(
            teacher_id,
            grade=grade,
            topic=body.topic,
            style_hint=body.style_hint,
            question=body.question,
            is_lesson_prep=body.is_lesson_prep,
            mistake_text=body.mistake_text,
            thread_id=body.thread_id,
        )
        return {"ok": True, "profile": profile}

    def add_mistake(self, body) -> dict:
        teacher_id = validate_teacher_id(body.teacher_id)
        mistake = validate_topic(body.mistake)
        grade = validate_grade(body.grade)
        profile = TeacherMemoryStore().add_mistake(
            teacher_id,
            mistake=mistake,
            topic=body.topic,
            grade=grade,
        )
        return {"ok": True, "profile": profile}

    def list_mistakes(self, teacher_id: str, grade: str | None) -> dict:
        teacher_id = validate_teacher_id(teacher_id)
        grade = validate_grade(grade)
        return {"mistakes": TeacherMemoryStore().list_mistakes(teacher_id, grade=grade)}

    def list_lessons(self, teacher_id: str, grade: str | None) -> dict:
        teacher_id = validate_teacher_id(teacher_id)
        grade = validate_grade(grade)
        return {"recent_lessons": TeacherMemoryStore().list_recent_lessons(teacher_id, grade=grade)}

    def reset(self, teacher_id: str = "default") -> dict:
        deleted = TeacherMemoryStore().reset(teacher_id)
        return {"ok": True, "deleted": deleted}
