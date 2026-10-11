"""
ExamPilot Model Configuration Module
GT InnoX LLP
"""

from typing import Dict, Any, List
from desktop.config import DEFAULT_OLLAMA_HOST, DEFAULT_PRIMARY_MODEL, DEFAULT_FALLBACK_MODEL, RECOMMENDED_MODELS

class ModelConfig:
    def __init__(self, host: str = DEFAULT_OLLAMA_HOST, active_model: str = DEFAULT_FALLBACK_MODEL):
        self.host = host.rstrip("/")
        self.active_model = active_model
        self.fallback_model = DEFAULT_FALLBACK_MODEL
        self.timeout_seconds = 90
        self.max_retries = 2

    def get_recommended_models(self) -> List[Dict[str, Any]]:
        return RECOMMENDED_MODELS

model_config = ModelConfig()

