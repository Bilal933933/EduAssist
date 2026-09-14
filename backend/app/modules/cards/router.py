"""راوتر البطاقات — HTTP فقط."""
from fastapi import APIRouter, Depends
from google import genai

from app.core.errors import AppError
from app.core.response import ok
from app.dependencies import get_gemini_client, get_kb
from app.modules.cards.schemas import CardsRequest
from app.modules.cards.service import CardsService

router = APIRouter(prefix="/api", tags=["cards"])
_service = CardsService()


@router.post("/flashcards")
async def flashcards(req: CardsRequest, client: genai.Client = Depends(get_gemini_client), kb=Depends(get_kb)):
    try:
        return ok(_service.generate_flashcards(req.topic, req.question, client, kb))
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.post("/quiz")
async def quiz(req: CardsRequest, client: genai.Client = Depends(get_gemini_client), kb=Depends(get_kb)):
    try:
        return ok(_service.generate_quiz(req.topic, req.question, client, kb))
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")
