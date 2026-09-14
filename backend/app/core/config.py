import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    INTERNAL_API_KEY: str = os.getenv("INTERNAL_API_KEY", "")
    VECTOR_DATABASE_URL: str = os.getenv("VECTOR_DATABASE_URL", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", os.getenv("VECTOR_DATABASE_URL", ""))


settings = Settings()
PUBLIC_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}
