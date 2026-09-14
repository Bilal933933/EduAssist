"""توافقية: الخدمات انتقلت للشرائح (Modular Monolith) — ستُحذف لاحقاً."""
from app.modules.cards.service import CardsService
from app.modules.chat.service import ChatService
from app.modules.memory.service import MemoryService

__all__ = ["ChatService", "CardsService", "MemoryService"]
