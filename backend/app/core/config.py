import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    INTERNAL_API_KEY: str = os.getenv("INTERNAL_API_KEY", "")
    VECTOR_DATABASE_URL: str = os.getenv("VECTOR_DATABASE_URL", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", os.getenv("VECTOR_DATABASE_URL", ""))

    # نماذج Gemini — كانت متناثرة في chat.py و fc_client.py
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    # التضمين — v1: المحلي e5-small (384) هو المصدر الوحيد. ثوابت Gemini أدناه
    # legacy_v2 مجمّدة (انظر app/knowledge/embeddings.py) — لا تغيّر الأبعاد هنا.
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
    EMBEDDING_DIMENSIONS: int = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))
    # v1 الفعلي (يُقرأ من embeddings.py): e5-small / 384, query:/passage:
    LOCAL_EMBEDDING_PATH: str = os.getenv("LOCAL_EMBEDDING_PATH", r"D:\Offline-600GB\07-RAG\models\e5-small")
    LOCAL_EMBEDDING_DIM: int = int(os.getenv("LOCAL_EMBEDDING_DIM", "384"))

    # السجلات — كانت في core/logging.py
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
PUBLIC_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}
