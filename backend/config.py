import logging
import os

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    SUPABASE_URL: str = os.getenv(
        "SUPABASE_URL", "https://zxzcnpkfabiiecagczao.supabase.co"
    )
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "anon_key")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "service_key")
    RAILWAY_PORT: int = int(os.getenv("RAILWAY_PORT", "8000"))
    STUDENT_JWT_SECRET: str = os.getenv(
        "STUDENT_JWT_SECRET", "student-jwt-secret-change-in-production"
    )
    MCP_DEBUG_SECRET: str = os.getenv("MCP_DEBUG_SECRET", "")
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


settings = Settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
