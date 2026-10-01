"""محولات الهجين — عقد واحد للمقارنة العادلة."""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def rule_classify(question: str, context: dict | None = None) -> dict:
    """القواعد فقط — بلا شبكة."""
    from app.query_analyzer.analyzer import analyze, is_ambiguous

    analysis = analyze(question, context or {})
    return {
        "intent": analysis.intent,
        "confidence": 1.0,
        "source": "rule",
        "ambiguous": is_ambiguous(analysis, question),
    }


def hybrid_classify(question: str, context: dict | None = None, client=None) -> dict:
    """الهجين: قواعد أولاً + نموذج مقيد عند الغموض فقط."""
    from app.query_analyzer.analyzer import analyze, is_ambiguous, _detect_source_policy

    ctx = context or {}
    analysis = analyze(question, ctx)
    ambiguous = is_ambiguous(analysis, question)
    if not ambiguous or client is None:
        return {
            "intent": analysis.intent,
            "confidence": 1.0,
            "source": "rule",
            "ambiguous": ambiguous,
        }
    try:
        from app.query_analyzer.llm_classifier import classify_intent_llm

        llm_intent, conf = classify_intent_llm(client, question, ctx)
        if llm_intent and conf >= 0.6:
            return {"intent": llm_intent, "confidence": conf, "source": "llm", "ambiguous": ambiguous}
    except Exception:
        pass
    return {"intent": analysis.intent, "confidence": 1.0, "source": "rule-fallback", "ambiguous": ambiguous}


def llm_only_classify(question: str, context: dict | None = None, client=None) -> dict:
    """النموذج وحده — للقياس المقارن فقط."""
    if client is None:
        return {"intent": None, "confidence": 0.0, "source": "llm-skipped", "ambiguous": True}
    try:
        from app.query_analyzer.llm_classifier import classify_intent_llm

        intent, conf = classify_intent_llm(client, question, context or {})
        if intent:
            return {"intent": intent, "confidence": conf, "source": "llm", "ambiguous": True}
    except Exception:
        pass
    return {"intent": None, "confidence": 0.0, "source": "llm-failed", "ambiguous": True}
