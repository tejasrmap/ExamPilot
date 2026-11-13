from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings, validate_production_config
from backend.app.api.api_router import api_router
from backend.app.db.init_db import init_db

# Validate production configuration if running in production
validate_production_config(settings)

# Initialize database tables in development/test
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ExamPilot 2.0 Backend API — SaaS AI learning & MCQ analysis engine by GT InnoX LLP",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# Configure hardened CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=settings.CHROME_EXTENSION_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "User-Agent"],
)

# Register main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "product": "ExamPilot 2.0",
        "company": "GT InnoX LLP",
        "tagline": "Understand Questions. Learn the Answers."
    }
