"""قدرة المعرفة (RAG) — حدّ القدرة، لا التنفيذ.

قرار معماري (Modular Monolith + تعديل المراجعة):
- app/knowledge = قدرة تطبيقية/معرفية (استرجاع، نطاق، دمج RRF، إعادة ترتيب).
- app/infra (لاحقاً) = تفاصيل تقنية (VectorService، المخازن، عملاء Gemini).
- لا نرمي retrieval في infra/ تلقائياً حتى لا تتحول إلى سلة مهملات.
- src/ لا يُلمس في هذه النقلة عمداً (بنية تعمل + 57 اختباراً) — يُهاجر لاحقاً.

حالياً: إعادة تصدير حدودية فقط، التنفيذ في src/ كما هو.
"""
from src.knowledge_base import KnowledgeBase
from src.retrieval.retrieval_service import RetrievalService
from app.knowledge.retrieval_log import log_retrieval, summarize_hits

__all__ = ["KnowledgeBase", "RetrievalService", "log_retrieval", "summarize_hits"]
