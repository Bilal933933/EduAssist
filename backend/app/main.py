import json
import time

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import routers
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.request_context import set_request_id
from app.core.response import get_request_id, ok, request_id_middleware
from app.core.security import internal_key_guard

load_dotenv()
setup_logging()

app = FastAPI(title="Arabic Grammar Tutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.middleware("http")(internal_key_guard)
app.middleware("http")(request_id_middleware)


@app.middleware("http")
async def access_log_middleware(request: Request, call_next):
    """سطر app.jsonl واحد لكل طلب: طريقة/مسار/حالة/مدة. ثانوي لا يكسر."""
    start = time.perf_counter()
    try:
        response = await call_next(request)
        status = response.status_code
    except Exception:
        status = 500
        raise
    finally:
        try:
            rid = get_request_id(request)
            set_request_id(rid)
            payload = {
                "type": "access",
                "method": request.method,
                "path": request.url.path,
                "status": status,
                "duration_ms": round((time.perf_counter() - start) * 1000, 1),
            }
            get_logger("app").info(json.dumps(payload, ensure_ascii=False))
        except Exception:
            pass
    return response


@app.get("/health", tags=["health"])
async def health(request: Request):
    """فحص الحيوية: تستخدمه خدمة Realtime لمراقبة هذه الخدمة."""
    kb_ready = False
    try:
        from app.dependencies import get_kb

        get_kb()
        kb_ready = True
    except BaseException:
        kb_ready = False
    return ok({"status": "ok", "service": "ai-chat", "kb_ready": kb_ready}, request_id=get_request_id(request))


for r in routers:
    app.include_router(r)
