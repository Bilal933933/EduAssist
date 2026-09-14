"""نقطة تجميع راوترات الإصدار الأول."""
from app.api.v1 import cards, chat, memory, reindex, stats, threads

routers = [chat.router, threads.router, stats.router, reindex.router, cards.router, memory.router]

__all__ = ["routers", "chat", "threads", "stats", "reindex", "cards", "memory"]
