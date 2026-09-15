import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agent.loop.helpers import LIGHT_SYSTEM


def _build_light_prompt(question, hits, history=None):
    parts = []
    for h in (hits or [])[:8]:
        if not isinstance(h, dict) or h.get("error") or not (h.get("text") or "").strip():
            continue
        src = h.get("source", "مصدر")
        page = f" ص{h.get('page')}" if h.get("page") else ""
        parts.append(f"[{h.get('title', src)} - {src}{page}]\n{h.get('text', '')[:800]}")
    evidence = "\n\n---\n\n".join(parts) if parts else "لا توجد أدلة مسترجعة."
    hist = ""
    if history:
        hist = "\n".join(f"{'المدرس' if r == 'user' else 'المساعد'}: {t[:300]}" for r, t in history[-4:])
        hist = f"سياق المحادثة:\n{hist}\n\n"
    user = (
        f"{hist}الأدلة من المصادر:\n{evidence}\n\n"
        f"سؤال المدرس: {question}\n"
        "المطلوب: أجب مباشرة (إعراب/شرح مختصر). استشهد بالأدلة إن اعتمدت عليها، "
        "وإلا أجب من معرفتك مع التنبيه المذكور."
    )
    return LIGHT_SYSTEM, user


def _light_search(kb, client, question, question_scope):
    from app.agent.tools import execute_tool
    try:
        hits = execute_tool("searchChunks", {"query": question, "top_k": 8}, kb, client, inherited_scope=question_scope)
        if not isinstance(hits, list):
            return []
        return [h for h in hits if isinstance(h, dict) and not h.get("error")]
    except Exception as e:
        print(f"[Light search skip: {e}]")
        return []
