"""توافقية رجعية: التنفيذ انتقل إلى app.api.v1.chat."""
from app.api.v1.chat import ChatRequest, chat_endpoint, chat_stream_endpoint, router

__all__ = ["router", "ChatRequest", "chat_endpoint", "chat_stream_endpoint"]
