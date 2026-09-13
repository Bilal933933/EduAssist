import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, BigInteger, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# نفس قاعدة البيانات المتجهية — جداول مستقلة للمحادثات
CHAT_DB_URL = os.getenv(
    "VECTOR_DATABASE_URL",
    "postgresql://postgres:12345678@localhost:5432/ai_grammar_tutor",
)

# حدود سياق المحادثة المرسل للنموذج
MAX_CONTEXT_MESSAGES = 8
MAX_CONTEXT_CHARS = 3000

Base = declarative_base()


class ChatThread(Base):
    """نموذج المحادثة: جلسة حوار بين الطالب والمساعد."""
    __tablename__ = "chat_threads"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255), default="محادثة جديدة")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ChatMessage(Base):
    """نموذج رسالة داخل محادثة (من الطالب أو المساعد)."""
    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    thread_id = Column(
        BigInteger,
        ForeignKey("chat_threads.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role = Column(String(16), nullable=False)  # 'user' أو 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(Text)  # JSON لمصادر RAG المستخدمة في الإجابة
    created_at = Column(DateTime, server_default=func.now())


class ChatStore:
    """خدمة تخزين المحادثات ورسائلها وسياقها في قاعدة البيانات."""

    def __init__(self, db_url: str = None):
        self.db_url = db_url or CHAT_DB_URL
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_thread(self, title: str = None) -> dict:
        """ينشئ محادثة جديدة ويعيدها كقاموس."""
        clean_title = (title or "").strip()[:200] or "محادثة جديدة"
        session = self.Session()
        try:
            thread = ChatThread(title=clean_title)
            session.add(thread)
            session.commit()
            return {"id": thread.id, "title": thread.title}
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list_threads(self) -> list:
        """يعيد قائمة المحادثات مرتبة بالأحدث مع عدد رسائل كل واحدة."""
        session = self.Session()
        try:
            threads = (
                session.query(ChatThread)
                .order_by(ChatThread.updated_at.desc())
                .all()
            )
            counts = dict(
                session.query(ChatMessage.thread_id, func.count(ChatMessage.id))
                .group_by(ChatMessage.thread_id)
                .all()
            )
            return [
                {
                    "id": t.id,
                    "title": t.title,
                    "message_count": int(counts.get(t.id, 0)),
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                }
                for t in threads
            ]
        finally:
            session.close()

    def thread_exists(self, thread_id: int) -> bool:
        """يتحقق من وجود محادثة بالمعرف المعطى."""
        session = self.Session()
        try:
            return (
                session.query(ChatThread.id).filter_by(id=thread_id).first()
                is not None
            )
        finally:
            session.close()

    def get_messages(self, thread_id: int) -> list:
        """يعيد رسائل محادثة مرتبة زمنياً مع مصادرها."""
        session = self.Session()
        try:
            messages = (
                session.query(ChatMessage)
                .filter_by(thread_id=thread_id)
                .order_by(ChatMessage.id.asc())
                .all()
            )
            return [self._to_dict(m) for m in messages]
        finally:
            session.close()

    def add_message(self, thread_id: int, role: str, content: str, sources=None) -> dict:
        """يحفظ رسالة في محادثة ويحدّث وقت آخر نشاط لها."""
        session = self.Session()
        try:
            message = ChatMessage(
                thread_id=thread_id,
                role=role,
                content=content,
                sources=json.dumps(sources, ensure_ascii=False) if sources else None,
            )
            session.add(message)
            session.query(ChatThread).filter_by(id=thread_id).update(
                {"updated_at": func.now()}
            )
            session.commit()
            return self._to_dict(message)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def recent_history(self, thread_id: int) -> list:
        """يعيد آخر رسائل المحادثة ضمن حدود السياق بترتيب زمني [(role, content)]."""
        session = self.Session()
        try:
            rows = (
                session.query(ChatMessage)
                .filter_by(thread_id=thread_id)
                .order_by(ChatMessage.id.desc())
                .limit(MAX_CONTEXT_MESSAGES)
                .all()
            )
            history = []
            budget = MAX_CONTEXT_CHARS
            for msg in reversed(rows):
                cost = len(msg.content or "")
                if history and budget - cost < 0:
                    break
                budget -= cost
                history.append((msg.role, msg.content))
            return history
        finally:
            session.close()

    def delete_thread(self, thread_id: int):
        """يحذف محادثة مع كل رسائلها."""
        session = self.Session()
        try:
            session.query(ChatMessage).filter_by(thread_id=thread_id).delete()
            deleted = (
                session.query(ChatThread).filter_by(id=thread_id).delete()
            )
            session.commit()
            return deleted > 0
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def _to_dict(message: ChatMessage) -> dict:
        """يحول رسالة إلى قاموس جاهز لـ JSON."""
        sources = None
        if message.sources:
            try:
                sources = json.loads(message.sources)
            except json.JSONDecodeError:
                sources = None
        return {
            "id": message.id,
            "thread_id": message.thread_id,
            "role": message.role,
            "content": message.content,
            "sources": sources,
            "created_at": message.created_at.isoformat() if message.created_at else None,
        }
