"""مستودع ملخصات المحادثة — جدول واحد إضافي بحت (بلا ترحيل بيانات).

يُستخدم فقط عندما يتجاوز سجل الـ thread نافذة السياق المباشر.
"""

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Text,
    create_engine,
    func,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.storage.chat_store import CHAT_DB_URL

Base = declarative_base()


class ConversationSummary(Base):
    """ملخص تراكمي لما تجاوز نافذة السياق في thread واحد."""

    __tablename__ = "conversation_summaries"

    thread_id = Column(
        BigInteger, ForeignKey("chat_threads.id", ondelete="CASCADE"), primary_key=True
    )
    summary = Column(Text, nullable=False, default="")
    summarized_upto_msg_id = Column(BigInteger, nullable=False, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SummaryRepository:
    """قراءة/كتابة ملخص thread واحد — بلا أي منطق تلخيص."""

    def __init__(self, db_url: str | None = None):
        self.engine = create_engine(db_url or CHAT_DB_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get(self, thread_id: int) -> dict:
        session = self.Session()
        try:
            row = session.query(ConversationSummary).filter_by(thread_id=thread_id).first()
            if row is None:
                return {"summary": "", "summarized_upto_msg_id": 0}
            return {"summary": row.summary or "", "summarized_upto_msg_id": row.summarized_upto_msg_id or 0}
        finally:
            session.close()

    def save(self, thread_id: int, summary: str, upto_msg_id: int) -> None:
        session = self.Session()
        try:
            row = session.query(ConversationSummary).filter_by(thread_id=thread_id).first()
            if row is None:
                row = ConversationSummary(thread_id=thread_id)
                session.add(row)
            row.summary = summary
            row.summarized_upto_msg_id = upto_msg_id
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
