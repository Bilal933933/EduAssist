from enum import Enum


class ModuleIntent(str, Enum):
    """نيات الوحدات الثلاث — مستوى التوجيه بين الوحدات (لا يخلط مع نيات analyzer الـ18)."""

    GRAMMAR_CORRECTION = "grammar_correction"
    CONVERSATION_PRACTICE = "conversation_practice"
    LESSON_KNOWLEDGE = "lesson_knowledge"
