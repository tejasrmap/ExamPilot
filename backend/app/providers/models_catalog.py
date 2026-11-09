from typing import Dict, List
from backend.app.providers.base import ModelInfo

CATALOG: Dict[str, List[ModelInfo]] = {
    "openai": [
        ModelInfo(
            id="gpt-4o",
            name="GPT-4o (Omni)",
            provider="openai",
            supports_vision=True,
            context_window=128000,
            input_cost_per_million=2.50,
            output_cost_per_million=10.00
        ),
        ModelInfo(
            id="gpt-4o-mini",
            name="GPT-4o Mini (Fast & Cheap)",
            provider="openai",
            supports_vision=True,
            context_window=128000,
            input_cost_per_million=0.15,
            output_cost_per_million=0.60
        ),
        ModelInfo(
            id="o3-mini",
            name="o3-mini (High Reasoning)",
            provider="openai",
            supports_vision=False,
            context_window=200000,
            input_cost_per_million=1.10,
            output_cost_per_million=4.40
        )
    ],
    "gemini": [
        ModelInfo(
            id="gemini-2.0-flash",
            name="Gemini 2.0 Flash (Next-Gen Speed)",
            provider="gemini",
            supports_vision=True,
            context_window=1000000,
            input_cost_per_million=0.10,
            output_cost_per_million=0.40
        ),
        ModelInfo(
            id="gemini-1.5-flash",
            name="Gemini 1.5 Flash",
            provider="gemini",
            supports_vision=True,
            context_window=1000000,
            input_cost_per_million=0.075,
            output_cost_per_million=0.30
        ),
        ModelInfo(
            id="gemini-1.5-pro",
            name="Gemini 1.5 Pro (Deep Context)",
            provider="gemini",
            supports_vision=True,
            context_window=2000000,
            input_cost_per_million=1.25,
            output_cost_per_million=5.00
        )
    ],
    "anthropic": [
        ModelInfo(
            id="claude-3-5-sonnet-20241022",
            name="Claude 3.5 Sonnet (State-of-the-art Reasoning)",
            provider="anthropic",
            supports_vision=True,
            context_window=200000,
            input_cost_per_million=3.00,
            output_cost_per_million=15.00
        ),
        ModelInfo(
            id="claude-3-5-haiku-20241022",
            name="Claude 3.5 Haiku (Lightning Speed)",
            provider="anthropic",
            supports_vision=False,
            context_window=200000,
            input_cost_per_million=0.80,
            output_cost_per_million=4.00
        )
    ],
    "openrouter": [
        ModelInfo(
            id="deepseek/deepseek-chat",
            name="DeepSeek V3 (OpenRouter)",
            provider="openrouter",
            supports_vision=False,
            context_window=64000,
            input_cost_per_million=0.14,
            output_cost_per_million=0.28
        ),
        ModelInfo(
            id="meta-llama/llama-3.3-70b-instruct",
            name="Llama 3.3 70B Instruct (OpenRouter)",
            provider="openrouter",
            supports_vision=False,
            context_window=131072,
            input_cost_per_million=0.18,
            output_cost_per_million=0.18
        ),
        ModelInfo(
            id="google/gemini-2.0-flash-001",
            name="Gemini 2.0 Flash via OpenRouter",
            provider="openrouter",
            supports_vision=True,
            context_window=1000000,
            input_cost_per_million=0.10,
            output_cost_per_million=0.40
        )
    ]
}

def calculate_cost(provider: str, model_id: str, input_tokens: int, output_tokens: int) -> float:
    models = CATALOG.get(provider, [])
    for m in models:
        if m.id == model_id:
            in_cost = (input_tokens / 1_000_000.0) * m.input_cost_per_million
            out_cost = (output_tokens / 1_000_000.0) * m.output_cost_per_million
            return round(in_cost + out_cost, 6)
    # Default fallback rate: $0.50 / M in, $1.50 / M out
    return round((input_tokens * 0.50 + output_tokens * 1.50) / 1_000_000.0, 6)

