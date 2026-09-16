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

    # التضمين — كانت في knowledge/embeddings.py (الخلط هنا يكسر البحث)
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
    EMBEDDING_DIMENSIONS: int = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))

    # السجلات — كانت في core/logging.py
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
PUBLIC_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}
