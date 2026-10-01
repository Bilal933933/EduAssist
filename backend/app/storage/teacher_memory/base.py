"""تهيئة ذاكرة المدرس — engine/session/seed/indexes فقط."""
from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.storage.teacher_memory.constants import MEMORY_DB_URL, SEED_GRADES
from app.storage.teacher_memory.models import Base, Grade


class TeacherMemoryBase:
    """يوفر engine وSession والتهيئة الأولية فقط."""

    def _init_engine(self, db_url: str | None = None):
        from app.db.session import get_engine

        self.db_url = db_url or MEMORY_DB_URL
        # رابط مخصص للاختبارات فقط؛ وإلا المحرك المشترك
        self.engine = create_engine(self.db_url) if db_url else get_engine()
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

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
