"""محلل الأسئلة — النية والنطاق وسياسة المصادر."""
from app.query_analyzer.analyzer import QueryAnalysis, analyze
from app.query_analyzer.scope import Scope

__all__ = ["QueryAnalysis", "analyze", "Scope"]
