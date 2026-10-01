"""قراءة ذاكرة المدرس — profile/lists + تسلسل Dicts."""
from __future__ import annotations

from app.storage.teacher_memory.constants import (
    MAX_MISTAKES_PROMPT,
    MAX_RECENT_PROMPT,
    MAX_TOPICS,
)
from app.storage.teacher_memory.helpers import _valid_grade_label
from app.storage.teacher_memory.models import (
    Grade,
    Teacher,
    TeacherGradeAssignment,
    TeacherLessonEvent,
    TeacherMistake,
    TeacherPreference,
    TeacherTopicStat,
)


class ReadersMixin:
    def get_profile(self, teacher_key: str = "default") -> dict:
        session = self.Session()
        try:
            teacher = self._get_or_create_teacher(session, teacher_key)
            return self._profile_dict(session, teacher)
        finally:
            session.close()

    def list_mistakes(self, teacher_key: str = "default", grade: str | None = None) -> list[dict]:
        session = self.Session()
        try:
            teacher = self._get_or_create_teacher(session, teacher_key)
            grade_id = self.resolve_grade_id(session, grade)
            rows = self._query_mistakes(session, teacher.id, grade_id=grade_id, limit=50)
            return [self._mistake_dict(session, r) for r in rows]
        finally:
            session.close()

    def list_recent_lessons(self, teacher_key: str = "default", grade: str | None = None) -> list[dict]:
        session = self.Session()
        try:
            teacher = self._get_or_create_teacher(session, teacher_key)
            grade_id = self.resolve_grade_id(session, grade)
            rows = self._query_events(session, teacher.id, grade_id=grade_id, limit=20)
            out = []
            for r in rows:
                g = session.query(Grade).get(r.grade_id) if r.grade_id else None
                out.append(
                    {
                        "id": r.id,
                        "topic": r.topic,
                        "grade": _valid_grade_label(g.label_ar) if g else None,
                        "grade_id": r.grade_id,
                        "event_type": r.event_type,
                        "at": r.created_at.isoformat() if r.created_at else None,
                    }
                )
            return out
        finally:
            session.close()

    def list_grades(self) -> list[dict]:
        session = self.Session()
        try:
            rows = session.query(Grade).order_by(Grade.level_order).all()
            return [
                {
                    "id": r.id,
                    "code": r.code,
                    "label_ar": r.label_ar,
                    "stage": r.stage,
                }
                for r in rows
            ]
        finally:
            session.close()

    def _query_mistakes(self, session, teacher_uuid, grade_id=None, topic=None, limit=MAX_MISTAKES_PROMPT):
        q = session.query(TeacherMistake).filter_by(teacher_id=teacher_uuid, is_active=True)
        if grade_id:
            rows = (
                q.filter(
                    (TeacherMistake.grade_id == grade_id)
                    | (TeacherMistake.grade_id.is_(None))
                )
                .order_by(TeacherMistake.count.desc(), TeacherMistake.last_seen_at.desc())
                .limit(limit * 2)
                .all()
            )
            rows = sorted(
                rows,
                key=lambda r: (0 if r.grade_id == grade_id else 1, -(r.count or 1)),
            )[:limit]
        else:
            rows = (
                q.order_by(TeacherMistake.count.desc(), TeacherMistake.last_seen_at.desc())
                .limit(limit)
                .all()
            )
        if topic:
            rows = sorted(rows, key=lambda r: (0 if r.topic == topic else 1, -(r.count or 1)))
        return rows

    def _query_events(self, session, teacher_uuid, grade_id=None, limit=MAX_RECENT_PROMPT):
        q = session.query(TeacherLessonEvent).filter_by(teacher_id=teacher_uuid)
        if grade_id:
            q = q.filter(
                (TeacherLessonEvent.grade_id == grade_id)
                | (TeacherLessonEvent.grade_id.is_(None))
            )
        return q.order_by(TeacherLessonEvent.created_at.desc()).limit(limit).all()

    def _profile_dict(self, session, teacher: Teacher) -> dict:
        prefs = session.query(TeacherPreference).filter_by(teacher_id=teacher.id).first()
        grades = (
            session.query(Grade)
            .join(TeacherGradeAssignment, TeacherGradeAssignment.grade_id == Grade.id)
            .filter(TeacherGradeAssignment.teacher_id == teacher.id)
            .order_by(Grade.level_order)
            .all()
        )
        topics = (
            session.query(TeacherTopicStat)
            .filter_by(teacher_id=teacher.id)
            .order_by(TeacherTopicStat.ask_count.desc())
            .limit(MAX_TOPICS)
            .all()
        )
        mistakes = self._query_mistakes(session, teacher.id, limit=30)
        events = self._query_events(session, teacher.id, limit=15)

        return {
            "teacher_id": teacher.external_key or str(teacher.id),
            "teacher_uuid": str(teacher.id),
            "display_name": teacher.display_name or "المدرس",
            "preferred_grades": [
                l for l in (_valid_grade_label(g.label_ar) for g in grades) if l
            ],
            "grades": [
                {"id": g.id, "code": g.code, "label_ar": label, "stage": g.stage}
                for g in grades
                if (label := _valid_grade_label(g.label_ar))
            ],
            "frequent_topics": [
                {"topic": t.topic, "count": t.ask_count, "grade_id": t.grade_id}
                for t in topics
            ],
            "preferences": {
                "detail_level": prefs.detail_level if prefs else "متوسط",
                "example_style": prefs.example_style if prefs else "منهجية",
                "tone": (prefs.tone if prefs else None) or "احترافي",
                "prefers_lesson_plans": prefs.prefers_lesson_plans if prefs else True,
                "prefers_exercises": prefs.prefers_exercises if prefs else True,
            },
            "class_context": teacher.class_context or "",
            "summary": teacher.summary or "",
            "interaction_count": teacher.interaction_count or 0,
            "common_mistakes": [self._mistake_dict(session, m) for m in mistakes],
            "recent_lessons": [
                {
                    "topic": e.topic,
                    "grade": (
                        _valid_grade_label(g.label_ar)
                        if e.grade_id and (g := session.query(Grade).get(e.grade_id))
                        else None
                    ),
                    "grade_id": e.grade_id,
                    "at": e.created_at.isoformat() if e.created_at else None,
                    "event_type": e.event_type,
                }
                for e in events
            ],
            "updated_at": teacher.updated_at.isoformat() if teacher.updated_at else None,
        }

    def _mistake_dict(self, session, m: TeacherMistake) -> dict:
        g = session.query(Grade).get(m.grade_id) if m.grade_id else None
        return {
            "id": m.id,
            "mistake": m.mistake,
            "topic": m.topic,
            "grade": _valid_grade_label(g.label_ar) if g else None,
            "grade_id": m.grade_id,
            "count": m.count,
            "source": m.source,
        }
