"""اللوجر المركزي — المصدر الوحيد للإعداد (stdlib فقط).

3 ملفات JSONL تحت backend/logs/ + كونسول UTF-8:
- app.jsonl (طلبات/أحداث)، retrieval.jsonl (سطر لكل سؤال)، errors.jsonl (أخطاء).
السطر في الملفات JSON جاهز أصلاً من المتصل، فالمُنسق "%(message)s" فقط.
"""
import logging
import re
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.request_context import get_request_id_ctx

_configured = False

_REDACT_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z\-_]{10,}"),
    re.compile(r"(?i)(gemini_api_key|internal_api_key)\s*[:=]\s*['\"]?[^'\"\s,}]+"),
]


class _ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id") or not getattr(record, "request_id"):
            record.request_id = get_request_id_ctx() or "-"
        return True


class _RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        from app.core.config import settings

        msg = record.getMessage()
        for pat in _REDACT_PATTERNS:
            msg = pat.sub("[REDACTED]", msg)
        for secret in (settings.GEMINI_API_KEY, settings.INTERNAL_API_KEY):
            if secret and len(secret) >= 8 and secret in msg:
                msg = msg.replace(secret, "[REDACTED]")
        record.msg = msg
        record.args = ()
        return True


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def setup_logging(log_dir: str | None = None, level: str | None = None) -> Path:
    """يهيئ المجلد والمعالجات مرة واحدة. يعيد مسار مجلد السجلات."""
    from app.core.config import settings

    global _configured
    root = _backend_root()
    target = Path(log_dir or settings.LOG_DIR)
    if not target.is_absolute():
        target = root / target
    target.mkdir(parents=True, exist_ok=True)
    lvl = (level or settings.LOG_LEVEL).upper()
    numeric = getattr(logging, lvl, logging.INFO)

    specs = (("app", "app.jsonl"), ("retrieval", "retrieval.jsonl"), ("errors", "errors.jsonl"))
    for name, filename in specs:
        logger = logging.getLogger(f"eduassist.{name}")
        logger.setLevel(numeric)
        logger.propagate = False
        if _configured:
            continue
        fh = RotatingFileHandler(target / filename, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        fh.setLevel(numeric)
        fh.setFormatter(logging.Formatter("%(message)s"))
        fh.addFilter(_RedactingFilter())
        logger.addHandler(fh)

    if not _configured:
        console = logging.StreamHandler()
        console.setLevel(numeric)
        console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] rid=%(request_id)s %(message)s"))
        console.addFilter(_ContextFilter())
        console.addFilter(_RedactingFilter())
        for name, _ in specs:
            logging.getLogger(f"eduassist.{name}").addHandler(console)
        # الجذر يلتقط تحذيرات uvicorn/fastapi دون ازدواج
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric)
        _configured = True
    return target


def get_logger(name: str) -> logging.Logger:
    """يرجع لوجر eduassist.<name> مع حقن requestId تلقائياً."""
    logger = logging.getLogger(f"eduassist.{name}")
    if not any(isinstance(f, _ContextFilter) for f in logger.filters):
        logger.addFilter(_ContextFilter())
    if not any(isinstance(f, _RedactingFilter) for f in logger.filters):
        logger.addFilter(_RedactingFilter())
    return logger


class Timer:
    """مؤقت قياس مراحل خط الأنابيب (نُقل من src/core/logger)."""

    def __init__(self, name: str):
        self.name = name
        self.start = time.time()
        self.log = get_logger(name)

    def end(self, extra=""):
        elapsed = time.time() - self.start
        self.log.info(f"{self.name} - {elapsed:.2f}s {extra}")
        return elapsed
