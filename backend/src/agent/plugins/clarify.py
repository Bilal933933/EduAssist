def run(client, kb, question, analysis=None):
    # الاستيضاح فقط من المحلل الجديد (prepare_lesson بلا صف).
    # حُذف الـ fallback المعجمي الذي كان يسأل عن الصف/المصدر لأي سؤال عام حتى التحيات.
    if analysis is not None:
        if getattr(analysis, "needs_clarification", False):
            return {"needs": True, "question": analysis.clarification_question}
        return {"needs": False}
    from src.agent.clarifier import needs_clarification
    hits = kb.vector_service.lexical_search(question, top_k=5)
    clar = needs_clarification(question, hits)
    if clar:
        return {"needs": True, "question": clar["question"], "options": clar.get("options", [])}
    return {"needs": False}
