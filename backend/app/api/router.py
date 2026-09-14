"""نقطة تجميع راوترات الإصدار الأول — Modular Monolith.

المصدر المعتمد: modules/* (شرائح عمودية).
app.api.v1/* طبقات توافقية تُعاد التصدير من هنا وستُحذف لاحقاً.
"""
from app.api.v1 import reindex, stats, threads
from app.modules import cards, chat, memory

routers = [chat.router, threads.router, stats.router, reindex.router, cards.router, memory.router]

__all__ = ["routers", "chat", "threads", "stats", "reindex", "cards", "memory"]
