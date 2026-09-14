"""توافقية رجعية: التنفيذ انتقل إلى app.api.v1.cards."""
from app.api.v1.cards import CardsRequest, flashcards, quiz, router

__all__ = ["router", "CardsRequest", "flashcards", "quiz"]
