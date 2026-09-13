import hmac
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import chat, stats, threads, reindex, cards, memory

load_dotenv()

app = FastAPI(title="Arabic Grammar Tutor API")

# تفعيل CORS للتواصل الآمن مع واجهة Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2.2 Global Exception Filter موحد
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback, logging
    logging.error(f"Unhandled: {request.url.path} - {exc}\n{traceback.format_exc()}")
    # لا تكشف التفاصيل الداخلية للعميل
    return JSONResponse(status_code=500, content={"detail": "حدث خطأ داخلي. حاول مرة أخرى.", "code": "INTERNAL_ERROR"})

# مسارات عامة لا تتطلب المفتاح الداخلي (الفحص الحيوي + التوثيق فقط)
PUBLIC_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}


@app.get("/health", tags=["health"])
async def health():
    """فحص الحيوية: تستخدمه خدمة Realtime لمراقبة هذه الخدمة."""
    kb_ready = False
    try:
        from app.dependencies import get_kb

        get_kb()
        kb_ready = True
    # BaseException لالتقاط SystemExit الذي يرفعه KnowledgeBase عند غياب الفهرسة
    except BaseException:
        kb_ready = False
    return {"status": "ok", "service": "ai-chat", "kb_ready": kb_ready}


@app.middleware("http")
async def internal_key_guard(request: Request, call_next):
    """حارس المفتاح الداخلي: يرفض أي طلب لا يأتي من بوابة Realtime الموثوقة."""
    if request.method == "OPTIONS" or request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    expected = os.getenv("INTERNAL_API_KEY", "")
    provided = request.headers.get("X-Internal-Key", "")
    # فشل مغلق: إن لم يُعرَّف المفتاح نهائياً تُرفض كل الطلبات
    if not expected or not hmac.compare_digest(expected, provided):
        return JSONResponse(
            status_code=401,
            content={"detail": "مفتاح داخلي مفقود أو غير صحيح."},
        )
    return await call_next(request)


app.include_router(chat.router)
app.include_router(threads.router)
app.include_router(stats.router)
app.include_router(reindex.router)
app.include_router(cards.router)
app.include_router(memory.router)
