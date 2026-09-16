import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agent.loop.helpers import LIGHT_SYSTEM, select_light_system


def enrich_light_query(question: str, history=None, analysis=None) -> str:
    """يوسّع سؤال المتابعة الضميرية بمادة الحوار (موضوع/مثال المساعد).

    «كيف اشرح لهم الاجابة» وحده استعلام فارغ يسترجع بلاغة عشوائية؛
    نلحق به آخر مثال اقترحه المساعد + موضوع التحليل.
    """
    q = (question or "").strip()
    anchors: list[str] = []
    try:
        topics = list(getattr(analysis, "topics", None) or [])
        scope_topic = getattr(getattr(analysis, "scope", None), "topic", None)
        if scope_topic and scope_topic not in topics:
            topics.append(scope_topic)
        for t in topics:
            t = str(t or "").strip()
            if t and t not in anchors and len(anchors) < 2:
                anchors.append(t)
    except Exception:
        pass
    if not anchors and history:
        import re as _re

        for role, text in reversed(history):
            if role != "assistant" or not text:
                continue
            m = _re.search(r'[«"]([^»"]{4,80})[»"]', text)
            if m:
                anchors.append(m.group(1).strip())
                break
            if "لا " in f" {text} " and len(text) < 300:
                anchors.append(text[:120].strip())
                break
            break
    if not anchors:
        return q
    return f"{q} {' '.join(anchors)}"


def _build_light_prompt(question, hits, history=None, analysis=None):
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
    system = select_light_system(analysis, question)
    user = (
        f"{hist}الأدلة من المصادر:\n{evidence}\n\n"
        f"سؤال المدرس: {question}\n"
        "المطلوب: أجب مباشرة (إعراب/شرح مختصر). استشهد بالأدلة إن اعتمدت عليها، "
        "وإلا أجب من معرفتك مع التنبيه المذكور."
    )
    if system is not LIGHT_SYSTEM:
        user = (
            f"{hist}الأدلة من المصادر:\n{evidence}\n\n"
            f"سؤال المدرس: {question}\n"
            "المطلوب: اشرح للزميل كيف يوصل الإجابة لطلابه في 3-4 خطوات قصيرة "
            "مرتبطة بالجملة محل السؤال نفسها (القاعدة + العلامة + مثال مضاد + سؤال اختبار). "
            "استشهد بالأدلة إن اعتمدت عليها، وإلا أجب من معرفتك مع التنبيه المذكور."
        )
    return system, user


def _light_search(kb, client, question, question_scope, history=None, analysis=None):
    from app.agent.tools import execute_tool
    try:
        query = enrich_light_query(question, history, analysis)
        hits = execute_tool("searchChunks", {"query": query, "top_k": 8}, kb, client, inherited_scope=question_scope)
        if not isinstance(hits, list):
            return []
        return [h for h in hits if isinstance(h, dict) and not h.get("error")]
    except Exception as e:
        print(f"[Light search skip: {e}]")
        return []
