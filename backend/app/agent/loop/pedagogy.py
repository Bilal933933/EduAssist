import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_PEDAGOGY_KEYWORDS = ("أسلوب", "كيف أشرح", "كيف اشرح", "طريقة", "نشاط", "تمهيد", "استراتيجية", "مشوقة", "اقترح")


def _is_pedagogy_query(question: str, analysis=None) -> bool:
    """سؤال أسلوب/شرح يحتاج Tier2 تربوياً — نية أو كلمات مفتاحية."""
    try:
        if getattr(analysis, "intent", None) == "pedagogical_advice":
            return True
    except Exception:
        pass
    q = question or ""
    return any(k in q for k in _PEDAGOGY_KEYWORDS)


def _fetch_pedagogy_hits(kb, client, question: str, question_scope: dict | None, top_k: int = 5, analysis=None) -> list:
    """Tier2 منفصل وآمن: يعيد [] عند غياب الكتب أو أي خطأ — لا يكسر Tier1.

    يرفض الاستعلام التربوي الفارغ (سؤال ضميري بلا موضوع/مرساة) حتى لا يلوث
    الأدلة بنتائج عشوائية — Tier1 المخصب يكفي حينها.
    """
    q = (question or "").strip()
    has_anchor = False
    try:
        topics = list(getattr(analysis, "topics", None) or []) if analysis is not None else []
        scope_topic = getattr(getattr(analysis, "scope", None), "topic", None) if analysis is not None else None
        has_anchor = bool(topics or (scope_topic and str(scope_topic).strip()))
    except Exception:
        has_anchor = False
    if not has_anchor and len(q) < 30 and any(k in q for k in ("اشرح", "أشرح", "لهم", "الاجابة")):
        return []
    try:
        from app.agent.chat import embed_question
        scope = dict(question_scope or {})
        if hasattr(kb, "hybrid_search_pedagogy"):
            hits = kb.hybrid_search_pedagogy(
                question, None, top_k=top_k, scope=scope,
                embed_fn=lambda: embed_question(client, question),
            )
        else:
            ped_scope = dict(scope)
            ped_scope["source_type"] = "pedagogy"
            hits = kb.hybrid_search(
                question, None, top_k=top_k, scope=ped_scope,
                embed_fn=lambda: embed_question(client, question),
            )
        return [h for h in (hits or []) if isinstance(h, dict) and not h.get("error")]
    except Exception as e:
        print(f"[Pedagogy Tier2 skip: {e}]")
        return []


def _merge_pedagogy(tier1_hits: list, ped_hits: list, ped_first: bool = False, limit: int = 14) -> list:
    """دمج وسمي بلا خلط استعلامات: إزالة تكرار ثم قص — يعمل مع [] بأمان."""
    merged = []
    seen = set()
    ordered = ([*(ped_hits or []), *(tier1_hits or [])] if ped_first else ([*(tier1_hits or []), *(ped_hits or [])]))
    for h in ordered:
        if not isinstance(h, dict):
            continue
        k = h.get("doc_key") or (h.get("text", "")[:120])
        if k in seen:
            continue
        seen.add(k)
        merged.append(h)
        if len(merged) >= limit:
            break
    return merged
