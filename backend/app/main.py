from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import routers
from app.core.exceptions import register_exception_handlers
from app.core.response import get_request_id, ok, request_id_middleware
from app.core.security import internal_key_guard

load_dotenv()

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
