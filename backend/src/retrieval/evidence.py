from dataclasses import dataclass, field

@dataclass
class Evidence:
    doc_key: str
    text: str
    title: str | None = None
    source: str | None = None
    page: int | None = None
    doc_path: str | None = None
    doc_type: str | None = None
    grade: str | None = None
    stage: str | None = None
    subject: str | None = None
    branch: str | None = None
    source_type: str | None = None
    book_id: str | None = None
    unit: str | None = None
    lesson: str | None = None
    concepts: list = field(default_factory=list)
    similarity: float | None = None
    lexical_score: float | None = None
    rrf_score: float | None = None

    @classmethod
    def from_dict(cls, d: dict) -> "Evidence":
        return cls(
            doc_key=d.get("doc_key",""),
            text=d.get("text",""),
            title=d.get("title"),
            source=d.get("source"),
            page=d.get("page"),
            doc_path=d.get("doc_path"),
            doc_type=d.get("doc_type"),
            grade=d.get("grade"),
            stage=d.get("stage"),
            subject=d.get("subject"),
            branch=d.get("branch"),
            source_type=d.get("source_type"),
            book_id=d.get("book_id"),
            unit=d.get("unit"),
            lesson=d.get("lesson"),
            concepts=d.get("concepts") or [],
            similarity=d.get("similarity"),
            lexical_score=d.get("lexical_score"),
            rrf_score=d.get("rrf_score"),
        )

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}
