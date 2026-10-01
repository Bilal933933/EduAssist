"""تحديث ذاكرة المدرس — interaction/manual/mistakes/reset."""
from __future__ import annotations

from app.storage.teacher_memory.constants import (
    DEFAULT_PREFERENCES,
    MAX_GRADES,
)
from app.storage.teacher_memory.helpers import _utcnow
from app.storage.teacher_memory.inference import (
    extract_mistake_from_question,
    infer_preferences,
    looks_like_lesson_prep,
)
from app.storage.teacher_memory.models import (
    Teacher,
    TeacherGradeAssignment,
    TeacherLessonEvent,
    TeacherMistake,
    TeacherPreference,
)


class WritersMixin:
    def update_from_interaction(
        self,
        teacher_key: str = "default",
        *,
        grade: str | None = None,
        topic: str | None = None,
        style_hint: str | None = None,
        question: str | None = None,
        is_lesson_prep: bool = False,
        mistake_text: str | None = None,
        thread_id: int | None = None,
    ) -> dict:
        session = self.Session()
        try:
            teacher = self._get_or_create_teacher(session, teacher_key, commit=False)
            grade_id = self.resolve_grade_id(session, grade)
            topic = (topic or "").strip() or None

            if grade_id:
                self._assign_grade(session, teacher.id, grade_id)

            if topic:
                self._bump_topic_stat(session, teacher.id, topic, grade_id)

            if is_lesson_prep and topic:
                session.add(
                    TeacherLessonEvent(
                        teacher_id=teacher.id,
                        grade_id=grade_id,
                        topic=topic[:120],
                        event_type="prep",
                        thread_id=thread_id,
                        created_at=_utcnow(),
                    )
                )
            elif question and looks_like_lesson_prep(question) and topic:
                session.add(
                    TeacherLessonEvent(
                        teacher_id=teacher.id,
                        grade_id=grade_id,
                        topic=topic[:120],
                        event_type="prep",
                        thread_id=thread_id,
                        created_at=_utcnow(),
                    )
                )

            if mistake_text and mistake_text.strip():
                self._upsert_mistake(
                    session,
                    teacher.id,
                    mistake_text.strip(),
                    topic=topic,
                    grade_id=grade_id,
                    source="auto",
                )
            elif question:
                extracted = extract_mistake_from_question(question)
                if extracted:
                    self._upsert_mistake(
                        session,
                        teacher.id,
                        extracted,
                        topic=topic,
                        grade_id=grade_id,
                        source="auto",
                    )

            prefs_row = session.query(TeacherPreference).filter_by(teacher_id=teacher.id).first()
            prefs = {
                "detail_level": prefs_row.detail_level if prefs_row else "متوسط",
                "example_style": prefs_row.example_style if prefs_row else "منهجية",
                "tone": (prefs_row.tone if prefs_row else None) or "احترافي",
                "prefers_lesson_plans": prefs_row.prefers_lesson_plans if prefs_row else True,
                "prefers_exercises": prefs_row.prefers_exercises if prefs_row else True,
            }
            if question:
                prefs = infer_preferences(question, prefs)
                self._upsert_preferences(session, teacher.id, prefs)

            teacher.interaction_count = (teacher.interaction_count or 0) + 1
            teacher.updated_at = _utcnow()

            if teacher.interaction_count == 1 or teacher.interaction_count % 2 == 0:
                teacher.summary = self._build_summary(session, teacher)

            session.commit()
            session.refresh(teacher)
            return self._profile_dict(session, teacher)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def set_manual(
        self,
        teacher_key: str = "default",
        *,
        display_name: str | None = None,
        preferred_grades: list | None = None,
        summary: str | None = None,
        preferences: dict | None = None,
        class_context: str | None = None,
        common_mistakes: list | None = None,
        recent_lessons: list | None = None,
        style_notes: list | None = None,  # للتوافق؛ يُتجاهل أو يُدمج في summary
    ) -> dict:
        session = self.Session()
        try:
            teacher = self._get_or_create_teacher(session, teacher_key, commit=False)
            if display_name is not None:
                teacher.display_name = display_name[:120]
            if class_context is not None:
                teacher.class_context = class_context[:500]
            if summary is not None:
                teacher.summary = summary[:800]
            if preferred_grades is not None:
                session.query(TeacherGradeAssignment).filter_by(teacher_id=teacher.id).delete()
                for i, g in enumerate(preferred_grades[:MAX_GRADES]):
                    gid = self.resolve_grade_id(session, str(g))
                    if gid:
                        self._assign_grade(session, teacher.id, gid, is_primary=(i == 0))
            if preferences is not None:
                prefs = {**DEFAULT_PREFERENCES, **preferences}
                if not prefs.get("tone"):
                    prefs["tone"] = "احترافي"
                self._upsert_preferences(session, teacher.id, prefs)
            if common_mistakes is not None:
                session.query(TeacherMistake).filter_by(teacher_id=teacher.id).delete()
                for m in common_mistakes[:40]:
                    if isinstance(m, dict) and m.get("mistake"):
                        self._upsert_mistake(
                            session,
                            teacher.id,
                            str(m["mistake"]),
                            topic=m.get("topic"),
                            grade_text=m.get("grade"),
                            count=int(m.get("count", 1)),
                            source="manual",
                        )
                    elif isinstance(m, str) and m.strip():
                        self._upsert_mistake(
                            session, teacher.id, m.strip(), source="manual"
                        )
            if recent_lessons is not None:
                session.query(TeacherLessonEvent).filter_by(teacher_id=teacher.id).delete()
                for item in recent_lessons[:20]:
                    if isinstance(item, dict) and item.get("topic"):
                        gid = self.resolve_grade_id(session, item.get("grade"))
                        session.add(
                            TeacherLessonEvent(
                                teacher_id=teacher.id,
                                grade_id=gid,
                                topic=str(item["topic"])[:120],
                                event_type="prep",
                                created_at=_utcnow(),
                            )
                        )
                    elif isinstance(item, str) and item.strip():
                        session.add(
                            TeacherLessonEvent(
                                teacher_id=teacher.id,
                                topic=item.strip()[:120],
                                event_type="prep",
                            )
                        )

            if summary is None:
                teacher.summary = self._build_summary(session, teacher)
            teacher.updated_at = _utcnow()
            session.commit()
            session.refresh(teacher)
            return self._profile_dict(session, teacher)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def add_mistake(
        self,
        teacher_key: str = "default",
        mistake: str = "",
        topic: str | None = None,
        grade: str | None = None,
    ) -> dict:
        if not mistake.strip():
            return self.get_profile(teacher_key)
        return self.update_from_interaction(
            teacher_key, topic=topic, grade=grade, mistake_text=mistake.strip()
        )

    def reset(self, teacher_key: str = "default") -> bool:
        session = self.Session()
        try:
            teacher = session.query(Teacher).filter_by(external_key=teacher_key).first()
            if not teacher:
                return False
            session.delete(teacher)  # CASCADE
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # توافق خلفي: كانت staticmethods على الكلاس الأصلي
    @staticmethod
    def _looks_like_lesson_prep(question: str) -> bool:
        return looks_like_lesson_prep(question)

    @staticmethod
    def _extract_mistake_from_question(question: str):
        return extract_mistake_from_question(question)

    @staticmethod
    def _infer_preferences(question: str, prefs: dict) -> dict:
        return infer_preferences(question, prefs)
