import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.modules.tutor_orchestrator.application.intent_map import map_intent
from app.modules.tutor_orchestrator.domain.intent import ModuleIntent


def resolve_module(analysis) -> ModuleIntent:
    """يقرأ analysis.intent الجاهزة من analyze() ويعيد وحدة التوجيه.

    لا يعيد تصنيفاً ولا يستدعي LLM — التوجيه فقط (المرحلة 1).
    """
    intent = getattr(analysis, "intent", None)
    return map_intent(intent)
