"""ترحيل لمرة واحدة من جداول v3 النصية."""
from __future__ import annotations

import json

from app.storage.teacher_memory.constants import DEFAULT_PREFERENCES
from app.storage.teacher_memory.helpers import _utcnow
from app.storage.teacher_memory.inference import loads_list
from app.storage.teacher_memory.models import (
    LegacyMistake,
    LegacyRecentLesson,
    LegacyTeacherProfile,
    TeacherLessonEvent,
)


class MigrationV3Mixin:
    def _migrate_from_v3(self):
        """ترحيل لمرة واحدة من جداول v3 النصية إن وُجدت بيانات."""
        session = self.Session()
        try:
            # إن وُجد مدرس default حديث ولا توجد ملفات قديمة، تجاهل
            legacy_profiles = []
            try:
                legacy_profiles = session.query(LegacyTeacherProfile).all()
            except Exception:
                session.rollback()
                return

            for lp in legacy_profiles:
                key = (lp.teacher_id or "default").strip() or "default"
                teacher = self._get_or_create_teacher(session, key, commit=False)
                if lp.display_name:
                    teacher.display_name = lp.display_name
                if lp.class_context:
                    teacher.class_context = lp.class_context or ""
                if lp.summary:
                    teacher.summary = lp.summary or ""
                teacher.interaction_count = max(
                    teacher.interaction_count or 0, lp.interaction_count or 0
                )

                # صفوف
                for g in loads_list(lp.preferred_grades):
                    gid = self.resolve_grade_id(session, str(g))
                    if gid:
                        self._assign_grade(session, teacher.id, gid)

                # تفضيلات
                prefs = DEFAULT_PREFERENCES.copy()
                try:
                    if lp.preferences:
                        data = json.loads(lp.preferences)
                        if isinstance(data, dict):
                            prefs.update(data)
                except Exception:
                    pass
                self._upsert_preferences(session, teacher.id, prefs)

                # مواضيع
                for t in loads_list(lp.frequent_topics):
                    if isinstance(t, dict) and t.get("topic"):
                        self._bump_topic_stat(
                            session, teacher.id, t["topic"], None, int(t.get("count", 1))
                        )
                    elif isinstance(t, str) and t.strip():
                        self._bump_topic_stat(session, teacher.id, t.strip(), None, 1)

                # أخطاء من عمود JSON القديم
                for m in loads_list(getattr(lp, "common_mistakes", None) or "[]"):
                    if isinstance(m, dict) and m.get("mistake"):
                        self._upsert_mistake(
                            session,
                            teacher.id,
                            m["mistake"],
                            topic=m.get("topic"),
                            grade_text=m.get("grade"),
                            count=int(m.get("count", 1)),
                            source="manual",
                        )

            # أخطاء جدول v3
            try:
                for m in session.query(LegacyMistake).all():
                    teacher = self._get_or_create_teacher(
                        session, m.teacher_id or "default", commit=False
                    )
                    self._upsert_mistake(
                        session,
                        teacher.id,
                        m.mistake or "",
                        topic=m.topic,
                        grade_text=m.grade,
                        count=int(m.count or 1),
                        source="auto",
                    )
            except Exception:
                session.rollback()
                session = self.Session()

            # دروس حديثة v3
            try:
                for r in session.query(LegacyRecentLesson).all():
                    teacher = self._get_or_create_teacher(
                        session, r.teacher_id or "default", commit=False
                    )
                    gid = self.resolve_grade_id(session, r.grade)
                    session.add(
                        TeacherLessonEvent(
                            teacher_id=teacher.id,
                            grade_id=gid,
                            topic=(r.topic or "درس")[:120],
                            event_type="prep",
                            created_at=r.prepared_at or _utcnow(),
                        )
                    )
            except Exception:
                pass

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"[v3 migrate skip: {e}]")
        finally:
            session.close()

    @staticmethod
    def _loads(raw) -> list:
        # للتوافق مع أي كود قديم يستدعي TeacherMemoryStore._loads
        return loads_list(raw)
