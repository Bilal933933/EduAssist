"""توافقية رجعية: التنفيذ انتقل إلى app.api.v1.stats."""
from app.api.v1.stats import router, stats_endpoint

__all__ = ["router", "stats_endpoint"]
