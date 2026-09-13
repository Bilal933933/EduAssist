import os
from functools import lru_cache

from fastapi import HTTPException
from google import genai

from src.storage.chat_store import ChatStore
from src.knowledge_base import KnowledgeBase


@lru_cache(maxsize=1)
def get_kb() -> KnowledgeBase:
    """قاعدة المعرفة المتجهية — تُهيأ مرة واحدة بشكل كسول (Lazy) لتجنب فشل التشغيل إن لم تكن مفهرسة."""
    try:
        return KnowledgeBase()
    except SystemExit:
        raise HTTPException(
            status_code=500,
            detail="قاعدة البيانات المتجهية غير مفهرسة. يرجى تشغيل indexer.py أولاً.",
        )


@lru_cache(maxsize=1)
def get_store() -> ChatStore:
    """مخزن المحادثات — يُهيأ مرة واحدة بشكل كسول."""
    return ChatStore()


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    """عميل Gemini مشترك — يُنشأ مرة واحدة بدل إنشائه داخل كل طلب."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY غير مجهزة في .env")
    return genai.Client(api_key=api_key)
