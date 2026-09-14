"""توافقية: العقود انتقلت للشرائح — المصدر modules/*/schemas.py."""
from app.modules.cards.schemas import CardsRequest
from app.modules.chat.schemas import ChatRequest
from app.modules.memory.schemas import InteractionUpdate, ManualUpdate, MistakeBody
from app.modules.threads.schemas import ThreadRequest

__all__ = ["ChatRequest", "ThreadRequest", "CardsRequest", "ManualUpdate", "InteractionUpdate", "MistakeBody"]
