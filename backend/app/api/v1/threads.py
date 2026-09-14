from fastapi import APIRouter, Depends

from app.core.errors import AppError
from app.core.response import ok
from app.core.validation import ensure_thread_exists, validate_thread_id, validate_title
from app.dependencies import get_store
from app.schemas.threads import ThreadRequest

router = APIRouter(prefix="/api", tags=["threads"])


@router.post("/threads")
async def create_thread_endpoint(req: ThreadRequest, store=Depends(get_store)):
    try:
        title = validate_title(req.title)
        return ok(store.create_thread(title=title))
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.get("/threads")
async def list_threads_endpoint(store=Depends(get_store)):
    try:
        return ok({"threads": store.list_threads()})
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.get("/threads/{thread_id}/messages")
async def thread_messages_endpoint(thread_id: int, store=Depends(get_store)):
    validate_thread_id(thread_id)
    ensure_thread_exists(store, thread_id)
    try:
        return ok({"thread_id": thread_id, "messages": store.get_messages(thread_id)})
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")


@router.delete("/threads/{thread_id}")
async def delete_thread_endpoint(thread_id: int, store=Depends(get_store)):
    validate_thread_id(thread_id)
    try:
        deleted = store.delete_thread(thread_id)
        if not deleted:
            raise AppError("THREAD_NOT_FOUND")
        return ok({"ok": True})
    except AppError:
        raise
    except Exception:
        raise AppError("INTERNAL_ERROR")
