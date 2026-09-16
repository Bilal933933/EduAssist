import time

from google import genai
from google.genai import errors

from app.core.config import settings

MODEL_NAME = settings.GEMINI_MODEL
FALLBACK_MODELS = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite"]
MAX_RETRIES = 3


def _is_retryable(error):
    """هل الخطأ عابر (استنفاد حصة مؤقت/انقطاع) فيستحق إعادة المحاولة؟"""
    if isinstance(error, errors.ClientError):
        return error.code in (429, 500, 502, 503, 504)
    return False


def _retry_delay(error):
    """يقرأ مدة الانتظار التي توصي بها Google نفسها من تفاصيل الخطأ (مثال: '19s')."""
    try:
        for detail in error.details:
            if str(detail.get("@type", "")).endswith("RetryInfo"):
                delay = str(detail.get("retryDelay", ""))
                if delay.endswith("s"):
                    return float(delay[:-1])
    except (AttributeError, TypeError):
        pass
    return None


def build_prompt(question, hits, history=None):
    """يبني تعليمات النظام مع سجل المحادثة والمحتوى المسترجع وسؤال الطالب."""
    context = "\n\n".join(
        f"[{h['title']}]\n{h['text']}" for h in hits
    )
    system = (
        "أنت معلم النحو العربي. أجب عن أسئلة الطالب باللغة العربية الفصحى "
        "البسيطة، بالاعتماد على المحتوى المقدم أولاً. "
        "لا تخترع قواعد غير موجودة في المحتوى. "
        "اعتمد أيضاً على سياق المحادثة السابقة لفهم الأسئلة التابعة والضمائر. "
        "إن لم تجد الجواب في المحتوى فقل ذلك بوضوح. "
        "ابدأ إجابتك بمثال قصير عندما يساعد ذلك."
    )
    parts = []
    if history:
        transcript = "\n".join(
            f"{'الطالب' if role == 'user' else 'المساعد'}: {text}"
            for role, text in history
        )
        parts.append(f"المحادثة السابقة:\n{transcript}")
    parts.append(f"المحتوى المتاح:\n{context}")
    parts.append(f"سؤال الطالب: {question}")
    user = "\n\n".join(parts)
    return system, user


def _try_model(client, model, user, system):
    """يستدعي نموذجاً واحداً مع إعادة محاولة بالمدة التي توصي بها Google."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=model,
                contents=user,
                config={"systemInstruction": system},
            )
            return response.text
        except Exception as error:
            last_error = error
            if not _is_retryable(error) or attempt == MAX_RETRIES - 1:
                raise
            wait = _retry_delay(error) or (2 ** attempt)
            code = getattr(error, "code", "خطأ")
            print(f"\n(الحصة مؤقتاً {code} — إعادة المحاولة خلال {wait:.0f} ثانية...)")
            time.sleep(wait)
    raise last_error


def ask(client, question, hits, history=None):
    """يجرب النموذج الأساسي ثم الاحتياطيين؛ ينتقل للنموذج التالي عند 404 أو استنفاد الحصة."""
    system, user = build_prompt(question, hits, history)
    models = [MODEL_NAME] + [m for m in FALLBACK_MODELS if m != MODEL_NAME]
    last_error = None
    for i, model in enumerate(models):
        try:
            return _try_model(client, model, user, system)
        except Exception as error:
            last_error = error
            is_client = isinstance(error, errors.ClientError)
            code = getattr(error, "code", None)
            if not is_client or code not in (404, 429):
                raise
            if i < len(models) - 1:
                print(f"\n(نموذج {model} فشل — نجرب {models[i + 1]}...)")
    raise last_error


def embed_question(client, question):
    """يحول سؤال الطالب إلى متجه عبر سلسلة نماذج التضمين الاحتياطية."""
    try:
        from app.knowledge.embeddings import embed_texts
    except ImportError:
        from app.knowledge.embeddings import embed_texts
    return embed_texts(client, [question])[0]