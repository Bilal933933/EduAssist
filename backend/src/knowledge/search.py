import re
import numpy as np
from sqlalchemy import select, and_
from src.knowledge.models import KnowledgeChunk

_ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
_TATWEEL = re.compile(r"\u0640")
_PUNCTUATION = re.compile(r"[^\w\s]")

_ARABIC_STOPWORDS = {
    "في", "من", "عن", "على", "إلى", "مع", "حتى", "خلال", "بين", "ما", "ماذا",
    "منذ", "كيف", "هل", "أين", "متى", "لماذا", "هو", "هي", "هما", "هم", "هن",
    "هذا", "هذه", "هذان", "هتان", "هؤلاء", "ذلك", "تلك", "الذي", "التي", "الذين",
    "اللائي", "اللاتي", "اللذان", "اللتان", "أن", "إن", "أنها", "إنه", "ثم", "أو", "أم",
    "قد", "لقد", "كل", "بعض", "غير", "معظم", "أي", "جدا"
}


try:
    from pyarabic.araby import (
        strip_tashkeel as _strip_tashkeel,
        strip_tatweel as _strip_tatweel,
        normalize_hamza as _normalize_hamza,
    )
    _PYARABIC = True
except Exception:
    _PYARABIC = False


def _normalize_arabic(text: str) -> str:
    text = text or ""
    if _PYARABIC:
        try:
            text = _normalize_hamza(_strip_tashkeel(_strip_tatweel(text)))
        except Exception:
            text = _ARABIC_DIACRITICS.sub("", text)
            text = _TATWEEL.sub("", text)
    else:
        text = _ARABIC_DIACRITICS.sub("", text)
        text = _TATWEEL.sub("", text)
    for old, new in {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ؤ": "ء", "ئ": "ء"}.items():
        text = text.replace(old, new)
    text = _PUNCTUATION.sub(" ", text)
    return text.strip()


def _strip_al(word: str) -> str:
    if word.startswith("ال") and len(word) > 3:
        return word[2:]
    return word


def _extract_tokens(text: str, filter_stopwords: bool = True) -> list[str]:
    raw_words = _normalize_arabic(text).split()
    tokens = []
    for w in raw_words:
        if len(w) < 2:
            continue
        if filter_stopwords and w in _ARABIC_STOPWORDS:
            continue
        tokens.append(w)
    return tokens


def _where_clause(scope: dict | None):
    from sqlalchemy import or_
    conditions = []
    for key in ("grade", "stage", "subject", "branch", "source_type", "book_id"):
        value = (scope or {}).get(key)
        if value:
            column = getattr(KnowledgeChunk, key)
            if key in ("grade", "stage") and value:
                conditions.append(or_(column == value, column.is_(None), column == "", column == "general"))
            else:
                conditions.append(column == value)
    return and_(*conditions) if conditions else None


class VectorSearch:
    def __init__(self, session_factory):
        self.Session = session_factory

    def search(self, query_embedding: list, top_k: int = 10, query_text: str = "", scope: dict | None = None):
        """Semantic retrieval بعد pre-filter metadata؛ لا يوجد metadata boost."""
        session = self.Session()
        try:
            where = _where_clause(scope)
            stmt = select(
                KnowledgeChunk.doc_key, KnowledgeChunk.title, KnowledgeChunk.text,
                KnowledgeChunk.source, KnowledgeChunk.page, KnowledgeChunk.embedding,
                KnowledgeChunk.doc_path, KnowledgeChunk.doc_type,
                KnowledgeChunk.grade, KnowledgeChunk.stage, KnowledgeChunk.subject,
                KnowledgeChunk.branch, KnowledgeChunk.source_type, KnowledgeChunk.book_id,
                KnowledgeChunk.unit, KnowledgeChunk.lesson, KnowledgeChunk.concepts,
            )
            if where is not None:
                stmt = stmt.where(where)
            chunks = session.execute(stmt).all()
            if not chunks:
                return []
            query_vec = np.array(query_embedding, dtype=np.float32)
            valid = [(i, c) for i, c in enumerate(chunks) if c.embedding]
            if not valid:
                return []
            embeddings = np.array([c.embedding for _, c in valid], dtype=np.float32)
            norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_vec)
            sims = np.dot(embeddings, query_vec) / (norms + 1e-12)
            order = np.argsort(-sims)[:top_k]
            result = []
            for rank in order:
                original_i, c = valid[int(rank)]
                result.append(self._serialize(c, similarity=float(sims[int(rank)])))
            return result
        finally:
            session.close()

    def lexical_search(self, query: str, top_k: int = 10, scope: dict | None = None):
        q_tokens = _extract_tokens(query, filter_stopwords=True) or _extract_tokens(query, filter_stopwords=False)
        if not q_tokens:
            return []

        session = self.Session()
        try:
            where = _where_clause(scope)
            stmt = select(
                KnowledgeChunk.doc_key, KnowledgeChunk.title, KnowledgeChunk.text,
                KnowledgeChunk.source, KnowledgeChunk.page, KnowledgeChunk.doc_path,
                KnowledgeChunk.doc_type, KnowledgeChunk.grade, KnowledgeChunk.stage,
                KnowledgeChunk.subject, KnowledgeChunk.branch, KnowledgeChunk.source_type,
                KnowledgeChunk.book_id, KnowledgeChunk.unit, KnowledgeChunk.lesson,
                KnowledgeChunk.concepts,
            )
            if where is not None:
                stmt = stmt.where(where)
            chunks = session.execute(stmt).all()
            scored = []
            for c in chunks:
                title_tokens = _extract_tokens(c.title or "", filter_stopwords=False)
                text_tokens = _extract_tokens(c.text or "", filter_stopwords=False)
                source_tokens = _extract_tokens(c.source or "", filter_stopwords=False)
                concepts_raw = c.concepts or []
                concepts_tokens = []
                for conc in concepts_raw:
                    concepts_tokens.extend(_extract_tokens(conc, filter_stopwords=False))
                concepts_set = set(concepts_tokens)
                concepts_set_no_al = {_strip_al(t) for t in concepts_set}
                lesson_tokens = _extract_tokens(c.lesson or "", filter_stopwords=False)
                lesson_set = set(lesson_tokens)
                lesson_set_no_al = {_strip_al(t) for t in lesson_set}
                title_set = set(title_tokens)
                title_set_no_al = {_strip_al(t) for t in title_set}
                text_counts = {}
                for t in text_tokens:
                    text_counts[t] = text_counts.get(t, 0) + 1
                    text_counts[_strip_al(t)] = text_counts.get(_strip_al(t), 0) + 1
                source_set = set(source_tokens)

                matched_score = 0.0
                total_weight = len(q_tokens)
                for qt in q_tokens:
                    qt_no_al = _strip_al(qt)
                    token_matched = False
                    if qt in title_set or qt_no_al in title_set_no_al:
                        matched_score += 2.5
                        token_matched = True
                    # concepts و lesson بأوزان عالية (كما اقترحت P0 review)
                    if qt in concepts_set or qt_no_al in concepts_set_no_al:
                        matched_score += 4.0
                        token_matched = True
                    if qt in lesson_set or qt_no_al in lesson_set_no_al:
                        matched_score += 4.0
                        token_matched = True
                    freq = text_counts.get(qt, 0) or text_counts.get(qt_no_al, 0)
                    if freq > 0:
                        matched_score += 1.0 + min(freq - 1, 3) * 0.2
                        token_matched = True
                    if not token_matched and (qt in source_set or qt_no_al in source_set):
                        matched_score += 1.0

                if matched_score > 0:
                    scored.append((matched_score / total_weight, c))

            scored.sort(key=lambda item: -item[0])
            return [self._serialize(c, lexical_score=float(score)) for score, c in scored[:top_k]]
        finally:
            session.close()

    @staticmethod
    def _serialize(c, similarity=None, lexical_score=None):
        item = {
            "doc_key": c.doc_key,
            "title": c.title,
            "text": c.text,
            "source": c.source,
            "page": c.page,
            "doc_path": c.doc_path,
            "doc_type": c.doc_type,
            "grade": c.grade,
            "stage": c.stage,
            "subject": c.subject,
            "branch": c.branch,
            "source_type": c.source_type,
            "book_id": c.book_id,
            "unit": c.unit,
            "lesson": c.lesson,
            "concepts": c.concepts or [],
        }
        if similarity is not None:
            item["similarity"] = similarity
        if lexical_score is not None:
            item["lexical_score"] = lexical_score
        return item
