"""بناء كتلة البرومبت والملخص — للاستخدام الداخلي للـ Agent فقط."""
from __future__ import annotations

from app.storage.teacher_memory.helpers import _valid_grade_label
from app.storage.teacher_memory.models import (
    Grade,
    Teacher,
    TeacherGradeAssignment,
    TeacherPreference,
    TeacherTopicStat,
)


class PromptMixin:
    def get_prompt_block(
        self,
        teacher_key: str = "default",
        current_grade: str | None = None,
        current_topic: str | None = None,
    ) -> str:
        session = self.Session()
        try:
            teacher = self._get_or_create_teacher(session, teacher_key)
            grade_id = self.resolve_grade_id(session, current_grade)
            prefs = session.query(TeacherPreference).filter_by(teacher_id=teacher.id).first()
            grades = (
                session.query(Grade)
                .join(TeacherGradeAssignment, TeacherGradeAssignment.grade_id == Grade.id)
                .filter(TeacherGradeAssignment.teacher_id == teacher.id)
                .order_by(Grade.level_order)
                .all()
            )
            mistakes = self._query_mistakes(session, teacher.id, grade_id=grade_id, topic=current_topic)
            recent = self._query_events(session, teacher.id, grade_id=grade_id)
            topics = (
                session.query(TeacherTopicStat)
                .filter_by(teacher_id=teacher.id)
                .order_by(TeacherTopicStat.ask_count.desc())
                .limit(5)
                .all()
            )

            if (
                (teacher.interaction_count or 0) == 0
                and not mistakes
                and not recent
                and not teacher.summary
            ):
                return ""

            lines = [
                "[سياق المدرس — للاستخدام الداخلي فقط]",
                "خاطب المستخدم كمدرس محترف زميل. كن مباشراً وعملياً. لا تبسيط طفولي ولا وعظ.",
            ]
            if teacher.display_name and teacher.display_name != "المدرس":
                lines.append(f"- المدرس: {teacher.display_name}")

            if current_grade and grade_id:
                g = session.query(Grade).get(grade_id)
                label = _valid_grade_label(g.label_ar if g else None) or current_grade
                lines.append(f"- الصف المستهدف لهذه الإجابة: {label}")
            elif grades:
                labels = [l for l in (_valid_grade_label(g.label_ar) for g in grades[:6]) if l]
                if labels:
                    lines.append("- صفوفه: " + ", ".join(labels))

            if current_topic:
                lines.append(f"- الموضوع الحالي: {current_topic}")

            if topics:
                names = list(dict.fromkeys(t.topic for t in topics if t.topic))
                if names:
                    lines.append("- مواضيع متكررة: " + ", ".join(names))

            if recent:
                bits = []
                for e in recent:
                    g = session.query(Grade).get(e.grade_id) if e.grade_id else None
                    label = _valid_grade_label(g.label_ar if g else None)
                    bits.append(e.topic + (f" ({label})" if label else ""))
                lines.append(f"- آخر ما حُضّر/نوقش: {', '.join(bits)}")
                lines.append(
                    "  → تجنّب تكرار نفس الأمثلة أو نفس هيكل الخطة إن تطابق الموضوع والصف."
                )

            if mistakes:
                scope = f"لصف {current_grade}" if current_grade else "لدى طلابه"
                m_txt = []
                for m in mistakes:
                    label = m.mistake
                    if m.topic:
                        label = f"{label} [{m.topic}]"
                    m_txt.append(label)
                lines.append(f"- أخطاء شائعة {scope}: {'; '.join(m_txt)}")
                lines.append("  → عالجها في الشرح والتدريبات عند ملاءمة الموضوع.")

            if prefs:
                bits = [
                    f"التفصيل: {prefs.detail_level}",
                    f"الأمثلة: {prefs.example_style}",
                    f"النبرة: {prefs.tone or 'احترافي'}",
                ]
                if prefs.prefers_lesson_plans:
                    bits.append("خطط حصص")
                if prefs.prefers_exercises:
                    bits.append("تدريبات")
                lines.append("- تفضيلات العمل: " + " | ".join(bits))

            if teacher.class_context:
                lines.append(f"- ملاحظة عامة: {teacher.class_context[:180]}")
            if teacher.summary:
                lines.append(f"- ملخص: {teacher.summary}")

            lines.append(
                "نفّذ التكييف دون الإفصاح عن وجود «ذاكرة» أو «ملف» في نص الإجابة."
            )
            return "\n".join(lines)
        finally:
            session.close()

    def _build_summary(self, session, teacher: Teacher) -> str:
        grades = (
            session.query(Grade)
            .join(TeacherGradeAssignment, TeacherGradeAssignment.grade_id == Grade.id)
            .filter(TeacherGradeAssignment.teacher_id == teacher.id)
            .order_by(Grade.level_order)
            .limit(4)
            .all()
        )
        topics = (
            session.query(TeacherTopicStat)
            .filter_by(teacher_id=teacher.id)
            .order_by(TeacherTopicStat.ask_count.desc())
            .limit(3)
            .all()
        )
        mistakes = self._query_mistakes(session, teacher.id, limit=1)
        events = self._query_events(session, teacher.id, limit=1)
        prefs = session.query(TeacherPreference).filter_by(teacher_id=teacher.id).first()
        parts = []
        if grades:
            labels = [l for l in (_valid_grade_label(g.label_ar) for g in grades) if l]
            if labels:
                parts.append("صفوف: " + ", ".join(labels))
        if topics:
            names = list(dict.fromkeys(t.topic for t in topics if t.topic))
            if names:
                parts.append("مواضيع: " + ", ".join(names))
        if events:
            parts.append(f"آخر درس: {events[0].topic}")
        if mistakes:
            parts.append(f"خطأ متكرر: {mistakes[0].mistake[:40]}")
        if prefs:
            parts.append(f"{prefs.detail_level} / {prefs.tone or 'احترافي'}")
        return " — ".join(parts) if parts else "مدرس لغة عربية."
