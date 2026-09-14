import hmac

from app.core.config import PUBLIC_PATHS, settings
from app.core.errors import AppError
from app.core.response import fail, get_request_id


async def internal_key_guard(request, call_next):
    """حارس المفتاح الداخلي: فشل مغلق — يرفض أي طلب بلا X-Internal-Key صحيح."""
    if request.method == "OPTIONS" or request.url.path in PUBLIC_PATHS:
        return await call_next(request)
    expected = settings.INTERNAL_API_KEY
    provided = request.headers.get("X-Internal-Key", "")
    if not expected or not hmac.compare_digest(expected, provided):
        return fail(
            "INTERNAL_KEY_INVALID",
            "مفتاح داخلي مفقود أو غير صحيح.",
            request_id=get_request_id(request),
            status=401,
        )
    return await call_next(request)
