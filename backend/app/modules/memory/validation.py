"""تحقق نطاق الذاكرة — ملك الفيتشر.

validate_grade مفهوم نطاق (مرتبط بكتالوج الصفوف M1/M2)،
لذا يعيش هنا لا في core.
"""
from app.core.errors import AppError


def validate_grade(grade: str | None, catalog: list[str] | None = None) -> str | None:
    """إن توفر الكتالوج تحقق صارم، وإلا فحص شكلي فقط (لا يكسر بدون DB)."""
    g = (grade or "").strip()
    if not g:
        return None
    if catalog is not None and g not in catalog:
        raise AppError("GRADE_UNKNOWN")
    return g
