"""قدرة المعرفة (RAG) — الاسترجاع والنطاق والدمج RRF وإعادة الترتيب.

المسار الوحيد: KnowledgeBase.hybrid_search (بوابة معجمية + RRF هجين).
"""
from app.knowledge.base import KnowledgeBase
from app.knowledge.retrieval_log import log_retrieval, summarize_hits

__all__ = ["KnowledgeBase", "log_retrieval", "summarize_hits"]
