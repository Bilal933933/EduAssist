"""نقطة تجميع الراوترات — Modular Monolith.

المصدر الوحيد: modules/* (شرائح عمودية + قدرات منصة).
لا يوجد api/v1 بعد نقلة الحسم.
"""
from app.modules import cards, chat, memory, threads
from app.modules.system import reindex, stats

routers = [chat.router, threads.router, stats.router, reindex.router, cards.router, memory.router]

__all__ = ["routers", "chat", "threads", "stats", "reindex", "cards", "memory"]
