"""وحدة المحادثة — شريحة عمودية (router + service + schemas + validation)."""
from app.modules.chat.router import chat_endpoint, chat_stream_endpoint, router
from app.modules.chat.schemas import ChatRequest
from app.modules.chat.service import ChatService
from app.modules.chat.validation import validate_question

__all__ = ["router", "ChatRequest", "ChatService", "chat_endpoint", "chat_stream_endpoint", "validate_question"]
