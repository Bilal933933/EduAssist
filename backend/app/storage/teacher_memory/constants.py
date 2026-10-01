"""ثوابت ذاكرة المدرس — إعدادات وحدود وبذور الصفوف."""
from __future__ import annotations

from app.core.config import settings

# المصدر الوحيد للرابط — كان os.getenv متناثراً
MEMORY_DB_URL = settings.DATABASE_URL or settings.VECTOR_DATABASE_URL

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
