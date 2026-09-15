import os
from functools import lru_cache

from app.core.errors import AppError
from google import genai

from app.storage.chat_store import ChatStore
from app.knowledge.base import KnowledgeBase
from app.modules.knowledge_ingestion.application.indexer_service import IndexerService
from app.modules.conversation.infrastructure.summary_repository import (
    SummaryRepository,
)


@lru_cache(maxsize=1)
def get_kb() -> KnowledgeBase:
    """قاعدة المعرفة المتجهية — تُهيأ مرة واحدة بشكل كسول (Lazy) لتجنب فشل التشغيل إن لم تكن مفهرسة."""
    try:
        return KnowledgeBase()
    except AppError:
        raise
    except SystemExit:
        raise AppError("KB_NOT_INDEXED")


@lru_cache(maxsize=1)
def get_store() -> ChatStore:
    """مخزن المحادثات — يُهيأ مرة واحدة بشكل كسول."""
    return ChatStore()


@lru_cache(maxsize=1)
def get_summary_repo() -> SummaryRepository:
    """مستودع ملخصات المحادثة — مفرد (singleton) كبقية المخازن، لا Engine لكل طلب."""
    return SummaryRepository()


@lru_cache(maxsize=1)
def get_indexer() -> IndexerService:
    """خدمة الفهرسة الموحدة — مفرد كبقية المخازن."""
    return IndexerService()


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    """عميل Gemini مشترك — يُنشأ مرة واحدة بدل إنشائه داخل كل طلب."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AppError("GEMINI_KEY_MISSING")
    return genai.Client(api_key=api_key)
