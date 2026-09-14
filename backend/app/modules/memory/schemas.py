"""عقد الذاكرة — ملك الفيتشر."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ManualUpdate(BaseModel):
    teacher_id: str = "default"
    display_name: Optional[str] = None
    preferred_grades: Optional[List[str]] = None
    style_notes: Optional[List[str]] = None
    summary: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    class_context: Optional[str] = None
    common_mistakes: Optional[List[Any]] = None
    recent_lessons: Optional[List[Any]] = None


class InteractionUpdate(BaseModel):
    teacher_id: str = "default"
    grade: Optional[str] = None
    topic: Optional[str] = None
    style_hint: Optional[str] = None
    question: Optional[str] = None
    is_lesson_prep: bool = False
    mistake_text: Optional[str] = None
    thread_id: Optional[int] = None


class MistakeBody(BaseModel):
    teacher_id: str = "default"
    mistake: str
    topic: Optional[str] = None
    grade: Optional[str] = None
