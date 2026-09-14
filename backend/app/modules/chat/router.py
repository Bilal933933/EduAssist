"""راوتر المحادثة — HTTP فقط (Modular Monolith).

القاعدة: Router = تأطير HTTP/SSE فقط.
كل التنسيق في ChatService. event_generator هنا محوّل SSE وليس منطق عمل.
"""
import asyncio
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from google import genai

from app.core.errors import AppError
from app.core.response import ok
from app.core.validation import validate_teacher_id, validate_thread_id
from app.dependencies import get_gemini_client, get_kb, get_store
from app.modules.chat.schemas import ChatRequest
from app.modules.chat.service import ChatService
from app.modules.chat.validation import validate_question

router = APIRouter(prefix="/api", tags=["chat"])
_service = ChatService()


@router.post("/chat")
async def chat_endpoint(
    req: ChatRequest,
    client: genai.Client = Depends(get_gemini_client),
    kb=Depends(get_kb),
    store=Depends(get_store),
):
    try:
        question = validate_question(req.question)
        teacher_id = validate_teacher_id(req.teacher_id)
        thread_id = validate_thread_id(req.thread_id)
        result = await _service.handle(question, thread_id, client, kb, store, teacher_id=teacher_id)
        return ok(result)
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.post("/chat/stream")
async def chat_stream_endpoint(
    req: ChatRequest,
    client: genai.Client = Depends(get_gemini_client),
    kb=Depends(get_kb),
    store=Depends(get_store),
):
    try:
        question = validate_question(req.question)
        teacher_id = validate_teacher_id(req.teacher_id)
        thread_id = validate_thread_id(req.thread_id)
        gen_or_stream, thread_id, already_stored = await _service.stream(question, thread_id, client, kb, store, teacher_id=teacher_id)
        if thread_id is None:
            return StreamingResponse(gen_or_stream, media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
        stream_gen = gen_or_stream

        async def event_generator():
            full_answer = ""
            hits = []
            completed = False
            try:
                async for event in stream_gen:
                    if event["type"] == "answer_chunk":
                        full_answer += event["text"]
                    elif event["type"] == "done":
                        hits = event.get("hits", [])
                        completed = True
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0)
                if full_answer and not already_stored:
                    suffix = "" if completed else " [انقطع - حاول مرة أخرى]"
                    store.add_message(thread_id, "assistant", full_answer + suffix, sources=hits)
                yield f"data: {json.dumps({'type': 'thread', 'thread_id': thread_id}, ensure_ascii=False)}\n\n"
            except Exception:
                if full_answer and not already_stored:
                    store.add_message(thread_id, "assistant", full_answer + " [خطأ - Retry]", sources=hits)
                yield f"data: {json.dumps({'type': 'error', 'error': {'code': 'INTERNAL_ERROR', 'message': 'حدث خطأ داخلي. حاول مرة أخرى.'}, 'partial': full_answer[:200]}, ensure_ascii=False)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")
