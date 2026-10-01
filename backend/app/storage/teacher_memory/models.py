"""نماذج ذاكرة المدرس — جداول SQLAlchemy فقط."""
from __future__ import annotations

import uuid
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
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


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


class LegacyTeacherProfile(Base):
    """جدول v3 النصي القديم — للترحيل فقط (read-only)."""

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
    """جدول أخطاء v3 — للترحيل فقط (read-only)."""

    __tablename__ = "teacher_mistakes"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    teacher_id = Column(String(64))
    mistake = Column(String(300))
    topic = Column(String(120))
    grade = Column(String(80))
    count = Column(Integer)


class LegacyRecentLesson(Base):
    """جدول الدروس الحديثة v3 — للترحيل فقط (read-only)."""

    __tablename__ = "teacher_recent_lessons"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    teacher_id = Column(String(64))
    topic = Column(String(120))
    grade = Column(String(80))
    prepared_at = Column(DateTime)
