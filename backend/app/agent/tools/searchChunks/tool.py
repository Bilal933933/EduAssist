import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def execute(args: dict, kb, client, inherited_scope=None):
    query = args.get("query", "")
    top_k = int(args.get("top_k", 5))
    from app.agent.chat import embed_question
    try:
        hits = kb.hybrid_search(query, None, top_k=top_k, scope=inherited_scope, candidate_k=40, fused_k=20, embed_fn=lambda: embed_question(client, query))
        return hits
    except Exception as e:
        return [{"error": str(e), "title": "خطأ", "text": ""}]

def format_search_observation(hits: list, max_hits: int = 8, max_chars: int = 600) -> str:
    if not hits:
        return "لا توجد نتائج بحث."
    blocks = []
    for i, hit in enumerate(hits[:max_hits], start=1):
        meta = " | ".join(x for x in [
            f"المصدر={hit.get('source') or 'غير محدد'}",
            f"الصف={hit.get('grade') or 'عام'}",
            f"المادة={hit.get('subject') or 'غير محددة'}",
            f"الفرع={hit.get('branch') or '-'}",
            f"الوحدة={hit.get('unit') or '-'}",
            f"الدرس={hit.get('lesson') or hit.get('title') or '-'}",
            f"الصفحة={hit.get('page') or '-'}",
        ] if x)
        evidence = (hit.get("text") or "").strip()
        if len(evidence) > max_chars:
            evidence = evidence[:max_chars].rstrip() + "…"
        blocks.append(f"[{i}] {meta}\n{evidence}")
    remaining = max(0, len(hits) - max_hits)
    suffix = f"\n(+ {remaining} مرشحًا إضافيًا في candidate pool)" if remaining else ""
    return "\n\n---\n\n".join(blocks) + suffix
