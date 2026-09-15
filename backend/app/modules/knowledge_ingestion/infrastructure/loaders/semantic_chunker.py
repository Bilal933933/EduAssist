import re

# أهداف chunking التقريبية بالكلمات/التوكنات.
# نستخدم whitespace tokens كـ proxy ثابت وخفيف بدل إضافة tokenizer جديد للمشروع.
TARGET_TOKENS = 400
MIN_TARGET_TOKENS = 300
MAX_TOKENS = 500
OVERLAP_TOKENS = 60

_SENTENCE_SPLIT = re.compile(r'(?<=[۔.!؟!?])\s+')
_PARAGRAPH_SPLIT = re.compile(r'\n\s*\n')


def _tokens(text: str) -> list[str]:
    return text.split()


def _word_count(text: str) -> int:
    return len(_tokens(text))


def _join_units(units: list[str], separator: str = "\n\n") -> str:
    return separator.join(u.strip() for u in units if u and u.strip()).strip()


def _hard_split_tokens(text: str, max_tokens: int = MAX_TOKENS, overlap_tokens: int = OVERLAP_TOKENS) -> list[str]:
    words = _tokens(text)
    if not words:
        return []
    chunks = []
    step = max(1, max_tokens - overlap_tokens)
    start = 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start += step
    return chunks


def _sentence_units(text: str) -> list[str]:
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]
    return sentences or [text.strip()]


def split_semantic(
    text: str,
    target_tokens: int = TARGET_TOKENS,
    min_tokens: int = MIN_TARGET_TOKENS,
    max_tokens: int = MAX_TOKENS,
    overlap_tokens: int = OVERLAP_TOKENS,
) -> list[str]:
    """يقسم النص إلى chunks دلالية bounded.

    - يحاول تجميع الفقرات/الجمل قرب 400 token.
    - لا يسمح لأي chunk عادي بتجاوز 500 token.
    - الجملة/الفقرة الأطول من الحد تُقسم hard split.
    - يضيف overlap محدودًا (~60 token) بين chunks المتجاورة.
    - لا يخلط sections مختلفة، حفاظًا على hierarchy والـmetadata.
    """
    text = (text or "").strip()
    if not text:
        return []
    if _word_count(text) <= max_tokens:
        return [text]

    paragraphs = [p.strip() for p in _PARAGRAPH_SPLIT.split(text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    units: list[str] = []
    for paragraph in paragraphs:
        if _word_count(paragraph) <= max_tokens:
            units.append(paragraph)
            continue
        # الفقرة الطويلة: حافظ على حدود الجمل أولًا، ثم hard split عند الحاجة.
        for sentence in _sentence_units(paragraph):
            if _word_count(sentence) <= max_tokens:
                units.append(sentence)
            else:
                units.extend(_hard_split_tokens(sentence, max_tokens=max_tokens, overlap_tokens=0))

    chunks: list[str] = []
    current_units: list[str] = []
    current_tokens = 0

    def flush() -> None:
        nonlocal current_units, current_tokens
        if current_units:
            chunks.append(_join_units(current_units))
            current_units = []
            current_tokens = 0

    for unit in units:
        unit_tokens = _word_count(unit)
        if unit_tokens > max_tokens:
            flush()
            chunks.extend(_hard_split_tokens(unit, max_tokens=max_tokens, overlap_tokens=0))
            continue

        if not current_units:
            current_units = [unit]
            current_tokens = unit_tokens
            continue

        if current_tokens + unit_tokens <= target_tokens:
            current_units.append(unit)
            current_tokens += unit_tokens
            continue

        # إذا كانت القطعة الحالية أقصر من الحد الأدنى، حاول إضافة الوحدة حتى لا
        # ننتج chunks صغيرة بلا داعٍ.
        if current_tokens < min_tokens and current_tokens + unit_tokens <= max_tokens:
            current_units.append(unit)
            current_tokens += unit_tokens
            continue

        flush()
        current_units = [unit]
        current_tokens = unit_tokens

    flush()

    # دمج remainder صغير مع السابق إذا أمكن، بدل ترك ذيل قصير جدًا.
    if len(chunks) >= 2 and _word_count(chunks[-1]) < min_tokens:
        merged = f"{chunks[-2]}\n\n{chunks[-1]}"
        if _word_count(merged) <= max_tokens:
            chunks[-2:] = [merged]

    # إضافة overlap بعد اكتمال الحدود، مع عدم تجاوز MAX_TOKENS.
    overlapped: list[str] = []
    for i, chunk in enumerate(chunks):
        if i == 0 or overlap_tokens <= 0:
            overlapped.append(chunk)
            continue
        previous_words = _tokens(chunks[i - 1])
        overlap = " ".join(previous_words[-overlap_tokens:])
        candidate = f"{overlap}\n\n{chunk}" if overlap else chunk
        if _word_count(candidate) <= max_tokens:
            overlapped.append(candidate)
        else:
            # إذا كان overlap سيكسر الحد، نحتفظ بالchunk دون overlap.
            overlapped.append(chunk)

    return overlapped


def chunk_sections_semantic(
    sections,
    target_tokens: int = TARGET_TOKENS,
    min_tokens: int = MIN_TARGET_TOKENS,
    max_tokens: int = MAX_TOKENS,
    overlap_tokens: int = OVERLAP_TOKENS,
):
    """يحول الأقسام إلى chunks مع الحفاظ على كل metadata الخاصة بالقسم."""
    chunks = []
    for section in sections:
        for index, text in enumerate(
            split_semantic(
                section.get("text", ""),
                target_tokens=target_tokens,
                min_tokens=min_tokens,
                max_tokens=max_tokens,
                overlap_tokens=overlap_tokens,
            )
        ):
            chunk = dict(section)
            chunk["text"] = text
            chunk["chunk_index"] = index
            chunk["chunk_token_count"] = _word_count(text)
            chunks.append(chunk)
    return chunks
