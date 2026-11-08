import os
import secrets
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "ExamPilot 2.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server-side AES-256 encryption key for API keys (must be 32 bytes or 64 hex chars or random fallback)
    API_KEY_ENCRYPTION_SECRET: str = os.getenv(
        "API_KEY_ENCRYPTION_SECRET", 
        "exampilot_super_secret_encryption_key_32_bytes_len!!"
    )
    
    # Database URL: defaults to local PostgreSQL or SQLite fallback for portable dev/testing
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./exampilot_saas.db")
    
    # Supabase Auth / JWT Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://demo.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "demo-anon-key")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY", None)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "exampilot_jwt_secret_token_dev_environment_GT_InnoX")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # OCR / File Upload limits
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_IMAGE_TYPES: list = ["image/png", "image/jpeg", "image/webp"]
    ALLOWED_PDF_TYPES: list = ["application/pdf"]
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "chrome-extension://*",
        "*"
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

