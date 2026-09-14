"""توافقية: المصدر انتقل إلى app.modules.memory."""
from app.modules.memory.router import (
    add_mistake,
    get_memory,
    get_memory_default,
    grades_catalog,
    list_lessons,
    list_mistakes,
    reset_memory,
    router,
    update_from_interaction,
    update_memory_manual,
)
from app.modules.memory.schemas import InteractionUpdate, ManualUpdate, MistakeBody
from app.modules.memory.service import MemoryService
from app.modules.memory.validation import validate_grade

__all__ = [
    "router", "MemoryService", "ManualUpdate", "InteractionUpdate", "MistakeBody",
    "validate_grade", "grades_catalog", "get_memory_default", "get_memory",
    "update_memory_manual", "update_from_interaction", "add_mistake",
    "list_mistakes", "list_lessons", "reset_memory",
]
