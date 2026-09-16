import json
import traceback

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import AppError, message_for
from app.core.logging import get_logger
from app.core.request_context import set_request_id
from app.core.response import fail, get_request_id


async def app_error_handler(request: Request, exc: AppError):
    status, message = message_for(exc.code)
    rid = get_request_id(request)
    set_request_id(rid)
    get_logger("errors").warning(json.dumps({"type": "app_error", "code": exc.code, "path": request.url.path}, ensure_ascii=False))
    return fail(exc.code, message, request_id=rid, status=status)


async def http_error_handler(request: Request, exc: StarletteHTTPException):
    # لا نسرب detail الداخلي: نعيد رسالة عربية عامة حسب الحالة
    code = "NOT_FOUND" if exc.status_code == 404 else "INTERNAL_ERROR"
    if exc.status_code == 401:
        code = "UNAUTHORIZED"
    elif exc.status_code == 422:
        code = "VALIDATION_ERROR"
    status, message = message_for(code)
    return fail(code, message, request_id=get_request_id(request), status=exc.status_code)


async def validation_error_handler(request: Request, exc: RequestValidationError):
    status, message = message_for("VALIDATION_ERROR")
    return fail("VALIDATION_ERROR", message, request_id=get_request_id(request), status=status)


async def global_exception_handler(request: Request, exc: Exception):
    rid = get_request_id(request)
    set_request_id(rid)
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    get_logger("errors").error(json.dumps({"type": "unhandled", "path": request.url.path, "error": str(exc)[:200], "trace": tb[-1500:]}, ensure_ascii=False))
    status, message = message_for("INTERNAL_ERROR")
    return fail("INTERNAL_ERROR", message, request_id=rid, status=status)


def register_exception_handlers(app):
    from fastapi.exceptions import RequestValidationError as _RVE

    app.exception_handler(AppError)(app_error_handler)
    app.exception_handler(StarletteHTTPException)(http_error_handler)
    app.exception_handler(_RVE)(validation_error_handler)
    app.exception_handler(Exception)(global_exception_handler)
    return app
