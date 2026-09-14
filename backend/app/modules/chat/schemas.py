"""عقد المحادثة — ملك الفيتشر (Modular Monolith)."""
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    thread_id: Optional[int] = Field(default=None, gt=0)
    teacher_id: Optional[str] = Field(default="default", max_length=64)
