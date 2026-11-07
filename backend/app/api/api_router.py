from fastapi import APIRouter
from backend.app.api.routes import (
    auth, providers, questions, ocr, assistant, practice, documents, analytics, settings
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(providers.router)
api_router.include_router(questions.router)
api_router.include_router(ocr.router)
api_router.include_router(assistant.router)
api_router.include_router(practice.router)
api_router.include_router(documents.router)
api_router.include_router(analytics.router)
api_router.include_router(settings.router)

