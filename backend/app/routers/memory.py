"""توافقية رجعية: التنفيذ انتقل إلى app.api.v1.memory."""
from app.api.v1.memory import (
    InteractionUpdate,
    ManualUpdate,
    MistakeBody,
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

__all__ = ["router", "ManualUpdate", "InteractionUpdate", "MistakeBody", "grades_catalog", "get_memory_default", "get_memory", "update_memory_manual", "update_from_interaction", "add_mistake", "list_mistakes", "list_lessons", "reset_memory"]
