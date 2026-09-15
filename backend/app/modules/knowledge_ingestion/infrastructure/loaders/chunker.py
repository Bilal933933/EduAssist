from app.modules.knowledge_ingestion.infrastructure.loaders.semantic_chunker import (
    chunk_sections_semantic,
    split_semantic,
    TARGET_TOKENS,
    OVERLAP_TOKENS,
)


def split_long_text(text, target_words=TARGET_TOKENS, overlap=OVERLAP_TOKENS):
    """واجهة توافقية: التقسيم المقيد بالتوكنات."""
    return split_semantic(text, target_tokens=target_words, overlap_tokens=overlap)


def chunk_sections(sections):
    """يقسم sections إلى chunks bounded 300–500 token تقريبًا."""
    return chunk_sections_semantic(
        sections,
        target_tokens=TARGET_TOKENS,
        overlap_tokens=OVERLAP_TOKENS,
    )
