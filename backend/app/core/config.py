import os
import re
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

    PROJECT_NAME: str = "ExamPilot 2.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server-side AES-256 encryption key for API keys (must be 32 bytes or 64 hex chars or random fallback)
    API_KEY_ENCRYPTION_SECRET: str = os.getenv(
        "API_KEY_ENCRYPTION_SECRET", 
        "exampilot_super_secret_encryption_key_32_bytes_len!!"
    )
    # Secondary encryption keys for graceful key rotation without downtime
    API_KEY_ENCRYPTION_ROTATION_SECRETS: List[str] = [
        s.strip() for s in os.getenv("API_KEY_ENCRYPTION_ROTATION_SECRETS", "").split(",") if s.strip()
    ]
    
    # Database URL: defaults to local PostgreSQL or SQLite fallback for portable dev/testing
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./exampilot_saas.db")
    
    # Supabase Auth / JWT Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://demo.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "demo-anon-key")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY", None)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "exampilot_jwt_secret_token_dev_environment_GT_InnoX")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    RESET_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes for password reset
    
    # Frontend URL (for password reset links and emails)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Email Service Configuration
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "console") # console, smtp, resend
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST", None)
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER", None)
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD", None)
    SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@exampilot.gtinnox.com")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
    RESEND_API_KEY: Optional[str] = os.getenv("RESEND_API_KEY", None)

    # Storage Service Configuration
    STORAGE_PROVIDER: str = os.getenv("STORAGE_PROVIDER", "local") # local, supabase, s3
    STORAGE_LOCAL_DIR: str = os.getenv("STORAGE_LOCAL_DIR", "backend/storage/documents")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "exampilot-documents")
    
    # Rate Limiting
    RATE_LIMIT_OCR_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_OCR_PER_MINUTE", "20"))
    RATE_LIMIT_AUTH_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_AUTH_PER_MINUTE", "10"))

    # OCR / File Upload limits
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "25"))
    ALLOWED_IMAGE_TYPES: list = ["image/png", "image/jpeg", "image/webp"]
    ALLOWED_PDF_TYPES: list = ["application/pdf"]
    
    # CORS (Never use wildcard "*" in production with credentials)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    # Chrome extension regex pattern: matches exact 32 lowercase alpha extension IDs
    CHROME_EXTENSION_REGEX: str = r"^chrome-extension://[a-z]{32}$"

def validate_production_config(cfg: Settings) -> None:
    """
    Validates that production environment variables are properly set and do not
    silently fall back to development defaults. Raises RuntimeError on failure.
    """
    env = cfg.ENVIRONMENT.lower()
    if env not in ("production", "prod"):
        return

    errors = []

    # 1. JWT Secret check
    if "dev_environment" in cfg.JWT_SECRET or len(cfg.JWT_SECRET) < 32:
        errors.append("JWT_SECRET must be set to a secure, random string (minimum 32 characters) in production.")

    # 2. Key Encryption Secret check
    if "super_secret_encryption" in cfg.API_KEY_ENCRYPTION_SECRET or len(cfg.API_KEY_ENCRYPTION_SECRET) < 32:
        errors.append("API_KEY_ENCRYPTION_SECRET must be set to a secure 32+ byte string in production.")

    # 3. Database URL check
    if cfg.DATABASE_URL.startswith("sqlite"):
        errors.append("DATABASE_URL cannot use SQLite in production. A production PostgreSQL URL is required.")

    # 4. CORS Origins check
    if "*" in cfg.BACKEND_CORS_ORIGINS:
        errors.append("BACKEND_CORS_ORIGINS cannot contain wildcard '*' in production when credentials are enabled.")
    if not cfg.BACKEND_CORS_ORIGINS:
        errors.append("BACKEND_CORS_ORIGINS must contain at least one explicit production frontend domain.")

    # 5. Email Service check
    if cfg.EMAIL_PROVIDER == "console":
        errors.append("EMAIL_PROVIDER cannot be 'console' in production. Configure 'smtp' or 'resend'.")
    elif cfg.EMAIL_PROVIDER == "smtp" and (not cfg.SMTP_HOST or not cfg.SMTP_USER):
        errors.append("SMTP_HOST and SMTP_USER are required when EMAIL_PROVIDER is 'smtp'.")

    if errors:
        msg = "PRODUCTION CONFIGURATION VALIDATION FAILED:\n - " + "\n - ".join(errors)
        raise RuntimeError(msg)

settings = Settings()
