"""
ذاكرة المدرس — طبقة بيانات M1/M2

الجداول:
  grades
  teachers
  teacher_grade_assignments
  teacher_preferences
  teacher_topic_stats
  teacher_mistakes
  teacher_lesson_events

التوافق:
  external_key='default' يعمل كما كان teacher_id النصي.
  ترحيل تلقائي من جداول v3 (teacher_profiles / teacher_mistakes / teacher_recent_lessons).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

MEMORY_DB_URL = os.getenv(
    "VECTOR_DATABASE_URL",
    "postgresql://postgres:12345678@localhost:5432/ai_grammar_tutor",
)

Base = declarative_base()

MAX_TOPICS = 12
MAX_GRADES = 10
MAX_MISTAKES_PROMPT = 6
MAX_RECENT_PROMPT = 5

DEFAULT_PREFERENCES = {
    "detail_level": "متوسط",
    "example_style": "منهجية",
    "prefers_lesson_plans": True,
    "prefers_exercises": True,
    "tone": "احترافي",
}

# قاموس مطابقة نصوص الصف → code
GRADE_ALIASES: dict[str, str] = {
    "الأول الابتدائي": "primary_1",
    "اول ابتدائي": "primary_1",
    "1 ابتدائي": "primary_1",
    "الثاني الابتدائي": "primary_2",
    "ثاني ابتدائي": "primary_2",
    "الثالث الابتدائي": "primary_3",
    "ثالث ابتدائي": "primary_3",
    "الرابع الابتدائي": "primary_4",
    "رابع ابتدائي": "primary_4",
    "الخامس الابتدائي": "primary_5",
    "خامس ابتدائي": "primary_5",
    "الخامس": "primary_5",
    "السادس الابتدائي": "primary_6",
    "سادس ابتدائي": "primary_6",
    "السادس": "primary_6",
    "الأول الإعدادي": "prep_1",
    "الاول الاعدادي": "prep_1",
    "أول إعدادي": "prep_1",
    "اعدادي اول": "prep_1",
    "الإعدادي": "prep_1",
    "اعدادي": "prep_1",
    "الثاني الإعدادي": "prep_2",
    "ثاني إعدادي": "prep_2",
    "الثالث الإعدادي": "prep_3",
    "ثالث إعدادي": "prep_3",
    "الأول الثانوي": "sec_1",
    "الثاني الثانوي": "sec_2",
    "الثالث الثانوي": "sec_3",
    "ثانوي": "sec_1",
}

SEED_GRADES = [
    ("primary_1", "الأول الابتدائي", "primary", 1),
    ("primary_2", "الثاني الابتدائي", "primary", 2),
    ("primary_3", "الثالث الابتدائي", "primary", 3),
    ("primary_4", "الرابع الابتدائي", "primary", 4),
    ("primary_5", "الخامس الابتدائي", "primary", 5),
    ("primary_6", "السادس الابتدائي", "primary", 6),
    ("prep_1", "الأول الإعدادي", "prep", 7),
    ("prep_2", "الثاني الإعدادي", "prep", 8),
    ("prep_3", "الثالث الإعدادي", "prep", 9),
    ("sec_1", "الأول الثانوي", "secondary", 10),
    ("sec_2", "الثاني الثانوي", "secondary", 11),
    ("sec_3", "الثالث الثانوي", "secondary", 12),
]


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _norm_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _mistake_key(mistake: str, grade_id: int | None, topic: str | None) -> str:
    base = f"{_norm_text(mistake)}|{grade_id or ''}|{_norm_text(topic or '')}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:40]


# ═══════════════════════════════════════════════════════════
# الجداول
# ═══════════════════════════════════════════════════════════


class Grade(Base):
    __tablename__ = "grades"

    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    code = Column(String(32), unique=True, nullable=False)
    label_ar = Column(String(80), nullable=False)
    stage = Column(String(32), nullable=False)  # primary | prep | secondary
    level_order = Column(Integer, nullable=False, default=0)


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_key = Column(String(64), unique=True, nullable=True, index=True)
    display_name = Column(String(120), default="المدرس")
    school_id = Column(UUID(as_uuid=True), nullable=True)
    class_context = Column(Text, default="")
    summary = Column(Text, default="")
    interaction_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TeacherGradeAssignment(Base):
    __tablename__ = "teacher_grade_assignments"
    __table_args__ = (
        UniqueConstraint("teacher_id", "grade_id", name="uq_teacher_grade"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True)
    grade_id = Column(SmallInteger, ForeignKey("grades.id"), nullable=False, index=True)
    is_primary = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)


class TeacherPreference(Base):
    __tablename__ = "teacher_preferences"

    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="CASCADE"), primary_key=True)
    detail_level = Column(String(20), default="متوسط")
    example_style = Column(String(30), default="منهجية")
    tone = Column(String(20), default="احترافي")
    prefers_lesson_plans = Column(Boolean, default=True)
    prefers_exercises = Column(Boolean, default=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TeacherTopicStat(Base):
    __tablename__ = "teacher_topic_stats"
    __table_args__ = (
        UniqueConstraint("teacher_id", "topic", "grade_id", name="uq_teacher_topic_grade"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(120), nullable=False)
    grade_id = Column(SmallInteger, ForeignKey("grades.id"), nullable=True, index=True)
    ask_count = Column(Integer, default=1)
    last_asked_at = Column(DateTime, server_default=func.now())


class TeacherMistake(Base):
    __tablename__ = "teacher_mistakes_v2"
    __table_args__ = (
        UniqueConstraint("teacher_id", "normalized_key", name="uq_teacher_mistake_key"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True)
    grade_id = Column(SmallInteger, ForeignKey("grades.id"), nullable=True, index=True)
    topic = Column(String(120), nullable=True, index=True)
    mistake = Column(String(300), nullable=False)
    normalized_key = Column(String(40), nullable=False)
    count = Column(Integer, default=1)
    source = Column(String(20), default="auto")  # auto | manual
    is_active = Column(Boolean, default=True)
    last_seen_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())


class TeacherLessonEvent(Base):
    __tablename__ = "teacher_lesson_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True)
    grade_id = Column(SmallInteger, ForeignKey("grades.id"), nullable=True, index=True)
    topic = Column(String(120), nullable=False)
    event_type = Column(String(30), default="prep")  # prep | discuss | exam
    lesson_id = Column(String(64), nullable=True)  # UUID نصي للتوافق مع Nest
    thread_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)


# ── جداول v3 القديمة (للترحيل فقط؛ تُقرأ إن وُجدت) ───────────

class LegacyTeacherProfile(Base):
    __tablename__ = "teacher_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    teacher_id = Column(String(64))
    display_name = Column(String(120))
    preferred_grades = Column(Text)
    frequent_topics = Column(Text)
    style_notes = Column(Text)
    preferences = Column(Text)
    class_context = Column(Text)
    summary = Column(Text)
    interaction_count = Column(Integer)
    common_mistakes = Column(Text)
    recent_lessons = Column(Text)


class LegacyMistake(Base):
    __tablename__ = "teacher_mistakes"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    teacher_id = Column(String(64))
    mistake = Column(String(300))
    topic = Column(String(120))
    grade = Column(String(80))
    count = Column(Integer)


class LegacyRecentLesson(Base):
    __tablename__ = "teacher_recent_lessons"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    teacher_id = Column(String(64))
    topic = Column(String(120))
    grade = Column(String(80))
    prepared_at = Column(DateTime)


class TeacherMemoryStore:
    """خدمة ذاكرة المدرس — النموذج المعياري M1/M2."""

    def __init__(self, db_url: str | None = None):
        self.db_url = db_url or MEMORY_DB_URL
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self._seed_grades()
        self._ensure_indexes()
        self._migrate_from_v3()

    # ─── تهيئة ───────────────────────────────────────────────

    def _seed_grades(self):
        session = self.Session()
        try:
            if session.query(Grade).count() == 0:
                for code, label, stage, order in SEED_GRADES:
                    session.add(
                        Grade(code=code, label_ar=label, stage=stage, level_order=order)
                    )
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"[grades seed skip: {e}]")
        finally:
            session.close()

    def _ensure_indexes(self):
        stmts = [
            "CREATE INDEX IF NOT EXISTS idx_mistakes_v2_teacher_grade_count ON teacher_mistakes_v2 (teacher_id, grade_id, count DESC) WHERE is_active = TRUE",
            "CREATE INDEX IF NOT EXISTS idx_lesson_events_teacher_grade_time ON teacher_lesson_events (teacher_id, grade_id, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_topic_stats_teacher ON teacher_topic_stats (teacher_id, ask_count DESC)",
        ]
        try:
            with self.engine.begin() as conn:
                for s in stmts:
                    try:
                        conn.execute(text(s))
                    except Exception:
                        pass
        except Exception as e:
            print(f"[indexes skip: {e}]")

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
                for g in self._loads(lp.preferred_grades):
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
                for t in self._loads(lp.frequent_topics):
                    if isinstance(t, dict) and t.get("topic"):
                        self._bump_topic_stat(
                            session, teacher.id, t["topic"], None, int(t.get("count", 1))
                        )
                    elif isinstance(t, str) and t.strip():
                        self._bump_topic_stat(session, teacher.id, t.strip(), None, 1)

                # أخطاء من عمود JSON القديم
                for m in self._loads(getattr(lp, "common_mistakes", None) or "[]"):
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

    # ─── حل الهوية والصف ─────────────────────────────────────

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

    # ─── قراءة للـ API / Agent ───────────────────────────────

    def get_profile(self, teacher_key: str = "default") -> dict:
        session = self.Session()
        try:
            teacher = self._get_or_create_teacher(session, teacher_key)
            return self._profile_dict(session, teacher)
        finally:
            session.close()

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
                label = g.label_ar if g else current_grade
                lines.append(f"- الصف المستهدف لهذه الإجابة: {label}")
            elif grades:
                lines.append(
                    "- صفوفه: " + ", ".join(g.label_ar for g in grades[:6])
                )

            if current_topic:
                lines.append(f"- الموضوع الحالي: {current_topic}")

            if topics:
                lines.append(
                    "- مواضيع متكررة: "
                    + ", ".join(t.topic for t in topics)
                )

            if recent:
                bits = []
                for e in recent:
                    g = session.query(Grade).get(e.grade_id) if e.grade_id else None
                    bits.append(
                        e.topic + (f" ({g.label_ar})" if g else "")
                    )
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

    # ─── تحديث ───────────────────────────────────────────────

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
            elif question and self._looks_like_lesson_prep(question) and topic:
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
                extracted = self._extract_mistake_from_question(question)
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
                prefs = self._infer_preferences(question, prefs)
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
                        "grade": g.label_ar if g else None,
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

    # ─── مساعدات ─────────────────────────────────────────────

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
            "preferred_grades": [g.label_ar for g in grades],
            "grades": [
                {"id": g.id, "code": g.code, "label_ar": g.label_ar, "stage": g.stage}
                for g in grades
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
                        session.query(Grade).get(e.grade_id).label_ar
                        if e.grade_id and session.query(Grade).get(e.grade_id)
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
            "grade": g.label_ar if g else None,
            "grade_id": m.grade_id,
            "count": m.count,
            "source": m.source,
        }

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
            parts.append("صفوف: " + ", ".join(g.label_ar for g in grades))
        if topics:
            parts.append("مواضيع: " + ", ".join(t.topic for t in topics))
        if events:
            parts.append(f"آخر درس: {events[0].topic}")
        if mistakes:
            parts.append(f"خطأ متكرر: {mistakes[0].mistake[:40]}")
        if prefs:
            parts.append(f"{prefs.detail_level} / {prefs.tone or 'احترافي'}")
        return " — ".join(parts) if parts else "مدرس لغة عربية."

    @staticmethod
    def _loads(raw) -> list:
        if not raw:
            return []
        if isinstance(raw, list):
            return raw
        try:
            data = json.loads(raw)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    @staticmethod
    def _looks_like_lesson_prep(question: str) -> bool:
        q = question or ""
        return any(k in q for k in ["حضر", "تحضير", "خطة درس", "سير حصة", "حضّر", "درس عن"])

    @staticmethod
    def _extract_mistake_from_question(question: str) -> str | None:
        q = (question or "").strip()
        triggers = [
            "أخطاء شائعة", "خطأ شائع", "يخطئون", "يخلطون",
            "أخطاء الطلاب", "الخطأ الشائع", "أخطائي الطلاب",
        ]
        if not any(t in q for t in triggers):
            return None
        for t in triggers:
            if t in q:
                tail = q[q.find(t) + len(t) :].strip(" :：-،.")
                if len(tail) > 8:
                    return tail[:180]
                return q[:180]
        return None

    @staticmethod
    def _infer_preferences(question: str, prefs: dict) -> dict:
        prefs = dict(prefs)
        q = question or ""
        if any(k in q for k in ["مختصر", "باختصار", "سريع"]):
            prefs["detail_level"] = "مختصر"
        elif any(k in q for k in ["مفصل", "عميق", "شامل", "تفصيلي"]):
            prefs["detail_level"] = "مفصل"
        if any(k in q for k in ["من الحياة", "واقعي", "يومي"]):
            prefs["example_style"] = "من_الحياة"
        if any(k in q for k in ["مشوق", "ممتع", "لعبة"]):
            prefs["tone"] = "مشوّق"
        else:
            prefs.setdefault("tone", "احترافي")
        if any(k in q for k in ["خطة", "سير حصة", "تحضير", "حضر"]):
            prefs["prefers_lesson_plans"] = True
        if any(k in q for k in ["تدريب", "تمرين", "أسئلة", "اختبار"]):
            prefs["prefers_exercises"] = True
        return prefs
