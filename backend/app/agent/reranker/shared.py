"""مشتركات طبقات الترتيب: حارس المجموعة الصغيرة + بناء نص المقطع."""


# تهدئة إعادة محاولة تحميل النماذج (التنزيل بطيء لمرة واحدة)
RETRY_COOLDOWN = 900


def small_pool(hits: list, top_k: int) -> list | None:
    """المجموعات الصغيرة (≤3) لا تحتاج ترتيباً — يعيدها مباشرة أو None للمتابعة."""
    return hits[:top_k] if len(hits) <= 3 else None


def passage_text(h: dict, max_chars: int = 700) -> str:
    """نص المقطع مع metadata — نفس غنى مسار LLM (درس/مفاهيم + 700 حرف)."""
    concepts = h.get("concepts")
    meta = " | ".join(
        x for x in [
            h.get("title") or "",
            h.get("lesson") or "",
            ", ".join(concepts) if isinstance(concepts, list) else (concepts or ""),
            h.get("grade") or "",
            h.get("subject") or "",
        ]
        if x
    )
    text = (h.get("text") or "")[:max_chars]
    return f"{meta} | {text}" if meta else text
