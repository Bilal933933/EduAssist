from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_store

router = APIRouter(prefix="/api", tags=["threads"])


class ThreadRequest(BaseModel):
    title: Optional[str] = None


@router.post("/threads")
async def create_thread_endpoint(req: ThreadRequest, store=Depends(get_store)):
    try:
        return store.create_thread(title=req.title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads")
async def list_threads_endpoint(store=Depends(get_store)):
    try:
        return {"threads": store.list_threads()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads/{thread_id}/messages")
async def thread_messages_endpoint(thread_id: int, store=Depends(get_store)):
    try:
        if not store.thread_exists(thread_id):
            raise HTTPException(status_code=404, detail="المحادثة غير موجودة.")
        return {"thread_id": thread_id, "messages": store.get_messages(thread_id)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/threads/{thread_id}")
async def delete_thread_endpoint(thread_id: int, store=Depends(get_store)):
    try:
        deleted = store.delete_thread(thread_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="المحادثة غير موجودة.")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
