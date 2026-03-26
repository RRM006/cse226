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
    SUPABASE_SERVICE_KEY: str = os.getenv(
        "SUPABASE_SERVICE_KEY", "service_key"
    )
    RAILWAY_PORT: int = int(os.getenv("RAILWAY_PORT", "8000"))
    STUDENT_JWT_SECRET: str = os.getenv("STUDENT_JWT_SECRET", "student-jwt-secret-change-in-production")

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


settings = Settings()
