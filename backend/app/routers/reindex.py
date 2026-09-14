"""توافقية رجعية: التنفيذ انتقل إلى app.api.v1.reindex."""
from app.api.v1.reindex import reindex_endpoint, router

__all__ = ["router", "reindex_endpoint"]
