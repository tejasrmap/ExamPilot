from typing import Dict, List, Optional
from backend.app.providers.base import BaseAIProvider, ModelInfo
from backend.app.providers.openai_provider import OpenAIProvider
from backend.app.providers.gemini_provider import GeminiProvider
from backend.app.providers.anthropic_provider import AnthropicProvider
from backend.app.providers.openrouter_provider import OpenRouterProvider
from backend.app.providers.models_catalog import CATALOG

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseAIProvider] = {
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
            "anthropic": AnthropicProvider(),
            "openrouter": OpenRouterProvider()
        }

    def get_provider(self, name: str) -> BaseAIProvider:
        clean_name = name.lower().strip()
        provider = self._providers.get(clean_name)
        if not provider:
            raise ValueError(f"Unsupported AI provider '{name}'. Supported providers: {list(self._providers.keys())}")
        return provider

    def list_supported_providers(self) -> List[str]:
        return list(self._providers.keys())

    async def get_all_models(self) -> Dict[str, List[ModelInfo]]:
        return CATALOG

# Global singleton registry
provider_registry = ProviderRegistry()

