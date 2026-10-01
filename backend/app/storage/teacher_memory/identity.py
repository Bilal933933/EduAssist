"""حل الهوية والصف — Teacher/Grade فقط."""
from __future__ import annotations

import hashlib
import uuid

from app.storage.teacher_memory.constants import GRADE_ALIASES
from app.storage.teacher_memory.helpers import _mistake_key, _utcnow
from app.storage.teacher_memory.models import (
    Grade,
    Teacher,
    TeacherGradeAssignment,
    TeacherMistake,
    TeacherPreference,
    TeacherTopicStat,
)


class IdentityMixin:
    def resolve_teacher_id(self, external_key: str = "default") -> uuid.UUID:
        session = self.Session()
        try:
            t = self._get_or_create_teacher(session, external_key or "default")
            return t.id
        finally:
            session.close()

    def resolve_grade_id(self, session, grade_text: str | None) -> int | None:
        if not grade_text:
            return None
        raw = str(grade_text).strip()
        if raw in ("", "unknown", "غير محدد", "None"):
            return None

        # مطابقة مباشرة على code (المحلل يولّد أكواداً مثل primary_5)
        g = session.query(Grade).filter_by(code=raw).first()
        if g:
            return g.id

        # مطابقة مباشرة على label
        g = session.query(Grade).filter(Grade.label_ar == raw).first()
        if g:
            return g.id

        # aliases
        code = GRADE_ALIASES.get(raw) or GRADE_ALIASES.get(raw.replace("أ", "ا"))
        if not code:
            # بحث جزئي
            for alias, c in GRADE_ALIASES.items():
                if alias in raw or raw in alias:
                    code = c
                    break
        if code:
            g = session.query(Grade).filter_by(code=code).first()
            if g:
                return g.id

        # إنشاء صف مخصص إن لم يُعرف (نص حر محفوظ كـ custom)
        code_custom = "custom_" + hashlib.sha1(raw.encode()).hexdigest()[:8]
        g = session.query(Grade).filter_by(code=code_custom).first()
        if not g:
            g = Grade(
                code=code_custom,
                label_ar=raw[:80],
                stage="custom",
                level_order=100,
            )
            session.add(g)
            session.flush()
        return g.id

    def _get_or_create_teacher(self, session, external_key: str, commit: bool = True) -> Teacher:
        external_key = (external_key or "default").strip() or "default"
        t = session.query(Teacher).filter_by(external_key=external_key).first()
        if t:
            return t
        t = Teacher(external_key=external_key, display_name="المدرس")
        session.add(t)
        session.flush()
        session.add(
            TeacherPreference(
                teacher_id=t.id,
                detail_level="متوسط",
                example_style="منهجية",
                tone="احترافي",
                prefers_lesson_plans=True,
                prefers_exercises=True,
            )
        )
        if commit:
            session.commit()
            session.refresh(t)
        return t

    def _assign_grade(self, session, teacher_uuid, grade_id: int, is_primary: bool = False):
        exists = (
            session.query(TeacherGradeAssignment)
            .filter_by(teacher_id=teacher_uuid, grade_id=grade_id)
            .first()
        )
        if not exists:
            session.add(
                TeacherGradeAssignment(
                    teacher_id=teacher_uuid, grade_id=grade_id, is_primary=is_primary
                )
            )

    def _upsert_preferences(self, session, teacher_uuid, prefs: dict):
        row = session.query(TeacherPreference).filter_by(teacher_id=teacher_uuid).first()
        if not row:
            row = TeacherPreference(teacher_id=teacher_uuid)
            session.add(row)
        row.detail_level = prefs.get("detail_level", row.detail_level or "متوسط")
        row.example_style = prefs.get("example_style", row.example_style or "منهجية")
        row.tone = prefs.get("tone") or "احترافي"
        row.prefers_lesson_plans = bool(
            prefs.get("prefers_lesson_plans", row.prefers_lesson_plans if row.prefers_lesson_plans is not None else True)
        )
        row.prefers_exercises = bool(
            prefs.get("prefers_exercises", row.prefers_exercises if row.prefers_exercises is not None else True)
        )
        row.updated_at = _utcnow()

    def _bump_topic_stat(self, session, teacher_uuid, topic: str, grade_id: int | None, add: int = 1):
        topic = topic.strip()[:120]
        if not topic:
            return
        row = (
            session.query(TeacherTopicStat)
            .filter_by(teacher_id=teacher_uuid, topic=topic, grade_id=grade_id)
            .first()
        )
        if row:
            row.ask_count = (row.ask_count or 0) + add
            row.last_asked_at = _utcnow()
        else:
            session.add(
                TeacherTopicStat(
                    teacher_id=teacher_uuid,
                    topic=topic,
                    grade_id=grade_id,
                    ask_count=add,
                    last_asked_at=_utcnow(),
                )
            )

    def _upsert_mistake(
        self,
        session,
        teacher_uuid,
        mistake: str,
        topic: str | None = None,
        grade_text: str | None = None,
        grade_id: int | None = None,
        count: int = 1,
        source: str = "auto",
    ):
        mistake = (mistake or "").strip()[:300]
        if not mistake:
            return
        if grade_id is None:
            grade_id = self.resolve_grade_id(session, grade_text)
        key = _mistake_key(mistake, grade_id, topic)
        row = (
            session.query(TeacherMistake)
            .filter_by(teacher_id=teacher_uuid, normalized_key=key)
            .first()
        )
        if row:
            row.count = max(row.count or 1, count) if source == "manual" else (row.count or 0) + max(1, count)
            row.last_seen_at = _utcnow()
            row.is_active = True
            if topic:
                row.topic = topic[:120]
            if grade_id:
                row.grade_id = grade_id
        else:
            session.add(
                TeacherMistake(
                    teacher_id=teacher_uuid,
                    grade_id=grade_id,
                    topic=(topic[:120] if topic else None),
                    mistake=mistake,
                    normalized_key=key,
                    count=max(1, count),
                    source=source,
                    is_active=True,
                    last_seen_at=_utcnow(),
                )
            )
