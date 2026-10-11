"""
ExamPilot Model Manager Module
GT InnoX LLP
"""

from typing import List, Dict, Any, Tuple, Optional, Callable
from desktop.ai.ollama_client import ollama_client, OllamaClient
from desktop.ai.model_config import model_config
from desktop.utils.system_info import get_system_hardware_info, check_disk_space_for_model
from desktop.utils.logger import logger

class ModelManager:
    """Manages AI model lifecycles, hardware matching, and downloads."""

    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or ollama_client

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive status of Ollama, hardware, and models."""
        hw = get_system_hardware_info()
        installed_models = self.client.list_installed_models()
        service_running = self.client.is_service_running()
        cli_installed = self.client.is_ollama_installed()

        return {
            "service_running": service_running,
            "cli_installed": cli_installed,
            "active_model": model_config.active_model,
            "fallback_model": model_config.fallback_model,
            "installed_models": installed_models,
            "recommended_catalog": model_config.get_recommended_models(),
            "hardware": hw
        }

    def set_active_model(self, model_name: str) -> bool:
        """Switch current active model."""
        model_config.active_model = model_name
        logger.info(f"Active model set to '{model_name}'")
        return True

    def download_model(self, model_name: str, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Tuple[bool, str]:
        """Verify storage and download model via Ollama."""
        # Find expected size
        catalog = {m["name"]: m for m in model_config.get_recommended_models()}
        expected_gb = catalog.get(model_name, {}).get("disk_gb", 4.0)

        if not check_disk_space_for_model(expected_gb):
            return False, f"Insufficient disk space. Model requires at least {expected_gb} GB plus 2 GB safety margin."

        return self.client.pull_model(model_name, progress_callback)

model_manager = ModelManager()

