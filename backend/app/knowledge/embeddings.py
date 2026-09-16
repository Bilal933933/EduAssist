import time

import httpx
from google.genai import errors

from app.core.config import settings

MODEL_NAME = settings.EMBEDDING_MODEL
FALLBACK_EMBEDDING_MODELS = ["gemini-embedding-2-preview", "gemini-embedding-001"]
DIMENSIONS = settings.EMBEDDING_DIMENSIONS
BATCH_SIZE = 1
BATCH_DELAY = 2.0
MAX_RETRIES = 5


def _is_retryable(error):
    """هل الخطأ عابر (حصة/انقطاع شبكة) فيستحق إعادة المحاولة؟"""
    if isinstance(error, errors.ClientError):
        return error.code in (429, 500, 502, 503, 504)
    if isinstance(error, httpx.TransportError):
        return True
    return False


def _is_daily_quota(error):
    """هل استُنفدت حصة اليوم فعلاً (فلا جدوى من المحاولة على نفس النموذج)؟"""
    try:
        error_obj = getattr(error, "details", {}) or {}
        if not isinstance(error_obj, dict):
            return False
        error_obj = error_obj.get("error", error_obj)
        for detail in error_obj.get("details", []):
            if "QuotaFailure" in str(detail.get("@type", "")) and "RequestsPerDay" in str(detail):
                return True
    except (AttributeError, TypeError):
        pass
    return False


def _retry_delay(error):
    """يقرأ مدة الانتظار التي توصي بها Google نفسها من تفاصيل الخطأ."""
    try:
        error_obj = getattr(error, "details", {}) or {}
        if not isinstance(error_obj, dict):
            return None
        error_obj = error_obj.get("error", error_obj)
        for detail in error_obj.get("details", []):
            if str(detail.get("@type", "")).endswith("RetryInfo"):
                delay = str(detail.get("retryDelay", ""))
                if delay.endswith("s"):
                    return float(delay[:-1])
    except (AttributeError, TypeError):
        pass
    return None


def embed_batch(client, texts, model=MODEL_NAME):
    """يضمّن دفعة واحدة؛ على استنفاد يومي يرفع فوراً ليتولى embed_batches التبديل."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.embed_content(
                model=model,
                contents=texts,
                config={"outputDimensionality": DIMENSIONS},
            )
            embeddings = [e.values for e in response.embeddings]
            if len(embeddings) != len(texts):
                raise ValueError(
                    f"استجاب النموذج بمتجهات {len(embeddings)} لـ {len(texts)} نصوص — تحقق من النموذج"
                )
            return embeddings
        except Exception as error:
            last_error = error
            if isinstance(error, errors.ClientError) and _is_daily_quota(error):
                raise
            if not _is_retryable(error) or attempt == MAX_RETRIES - 1:
                raise
            wait = _retry_delay(error) or (5 * (attempt + 1))
            print(f"\n(التضمين بـ {model}: {type(error).__name__} — إعادة المحاولة خلال {wait:.0f} ثانية...)")
            time.sleep(wait)
    raise last_error


def embed_batches(client, texts, batch_size=BATCH_SIZE):
    """مولّد: يعيد متجهات كل دفعة تباعاً، مع تحول لنموذج احتياطي عند استنفاد الحصة."""
    models = [MODEL_NAME] + [m for m in FALLBACK_EMBEDDING_MODELS if m != MODEL_NAME]
    model_index = 0
    i = 0
    while i < len(texts):
        batch = texts[i:i + batch_size]
        try:
            yield embed_batch(client, batch, models[model_index])
            i += len(batch)
            if i < len(texts):
                time.sleep(BATCH_DELAY)
        except Exception as error:
            is_quota = isinstance(error, errors.ClientError) and _is_daily_quota(error)
            if is_quota and model_index < len(models) - 1:
                model_index += 1
                print(f"\n(استُنفدت حصة {models[model_index - 1]} — نكمل بالتضمين بـ {models[model_index]})")
                continue
            raise


def embed_texts(client, texts, batch_size=BATCH_SIZE):
    """يحول النصوص إلى متجهات كاملة (مريحة للاستخدام المفرد)."""
    vectors = []
    for batch_vectors in embed_batches(client, texts, batch_size):
        vectors.extend(batch_vectors)
    return vectors