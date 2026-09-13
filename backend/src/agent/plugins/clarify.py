def run(client, kb, question, analysis=None):
    if analysis and getattr(analysis, "needs_clarification", False):
        return {"needs": True, "question": analysis.clarification_question}
    from src.agent.clarifier import needs_clarification
    hits = kb.vector_service.lexical_search(question, top_k=5)
    clar = needs_clarification(question, hits)
    if clar:
        return {"needs": True, "question": clar["question"], "options": clar.get("options", [])}
    return {"needs": False}
