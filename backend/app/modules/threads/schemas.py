"""عقد المحادثات — ملك الفيتشر."""
from typing import Optional

from pydantic import BaseModel, Field


class ThreadRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=120)
