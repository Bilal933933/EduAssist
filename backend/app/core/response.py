"""المغلف الموحد للاستجابات — المصدر الوحيد لشكل الرد."""
import uuid
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


def ok(data: Any = None, request_id: str | None = None) -> dict:
    return {"ok": True, "data": data, "meta": {"requestId": request_id}}


def fail(code: str, message: str, request_id: str | None = None, status: int = 500) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "ok": False,
            "error": {"code": code, "message": message},
            "meta": {"requestId": request_id},
        },
    )


def get_request_id(request: Request | None) -> str | None:
    if request is None:
        return None
    return getattr(request.state, "request_id", request.headers.get("X-Request-Id"))


async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:12]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response
