import json
import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from google import genai
from pydantic import BaseModel

from app.dependencies import get_gemini_client, get_kb, get_store
from app.modules.chat.service import ChatService

router = APIRouter(prefix="/api", tags=["chat"])
_service = ChatService()


class ChatRequest(BaseModel):
    question: str
    thread_id: Optional[int] = None
    teacher_id: Optional[str] = "default"


@router.post("/chat")
async def chat_endpoint(
    req: ChatRequest,
    client: genai.Client = Depends(get_gemini_client),
    kb=Depends(get_kb),
    store=Depends(get_store),
):
    try:
        return await _service.handle(req.question, req.thread_id, client, kb, store, teacher_id=req.teacher_id or "default")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream_endpoint(
    req: ChatRequest,
    client: genai.Client = Depends(get_gemini_client),
    kb=Depends(get_kb),
    store=Depends(get_store),
):
    try:
        gen_or_stream, thread_id, already_stored = await _service.stream(req.question, req.thread_id, client, kb, store, teacher_id=req.teacher_id or "default")
        # حالة استيضاح بدون thread
        if thread_id is None:
            return StreamingResponse(gen_or_stream, media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
        # gen_or_stream هو run_agentic_rag_stream
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
                # المسارات الجاهزة (مباشر/تصحيح/محادثة) تحفظ رسالتها بنفسها.
                # البث الوكيلي فقط يُحفظ هنا، وبختم الانقطاع عند عدم اكتماله.
                if full_answer and not already_stored:
                    suffix = "" if completed else " [انقطع - حاول مرة أخرى]"
                    store.add_message(thread_id, "assistant", full_answer + suffix, sources=hits)
                yield f"data: {json.dumps({'type': 'thread', 'thread_id': thread_id}, ensure_ascii=False)}\n\n"
            except Exception as e:
                if full_answer and not already_stored:
                    store.add_message(thread_id, "assistant", full_answer + " [خطأ - Retry]", sources=hits)
                yield f"data: {json.dumps({'type': 'error', 'error': str(e), 'partial': full_answer[:200]}, ensure_ascii=False)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
