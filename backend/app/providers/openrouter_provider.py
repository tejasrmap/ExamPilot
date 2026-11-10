import json
import httpx
from typing import Dict, List, Optional, Any
from backend.app.providers.base import BaseAIProvider, ModelInfo, QuestionAnalysisResult, ConfidenceModel
from backend.app.providers.models_catalog import CATALOG, calculate_cost
from backend.app.providers.prompt_builder import ANALYSIS_SYSTEM_PROMPT, build_analysis_user_prompt

class OpenRouterProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "openrouter"

    async def validate_key(self, api_key: str) -> bool:
        """Validates OpenRouter API key by checking auth key endpoint."""
        if not api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://openrouter.ai/api/v1/auth/key",
                    headers={"Authorization": f"Bearer {api_key.strip()}"}
                )
                return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self, api_key: Optional[str] = None) -> List[ModelInfo]:
        return CATALOG.get("openrouter", [])

    async def generate_analysis(
        self,
        api_key: str,
        model: str,
        question_text: str,
        options: Dict[str, str],
        subject: Optional[str] = None,
        context_material: Optional[str] = None
    ) -> QuestionAnalysisResult:
        user_prompt = build_analysis_user_prompt(question_text, options, subject, context_material)
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "HTTP-Referer": "https://exampilot.gtinnox.com",
            "X-Title": "ExamPilot 2.0",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"OpenRouter API error ({resp.status_code}): {resp.text}")
            
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            in_tokens = usage.get("prompt_tokens", 0)
            out_tokens = usage.get("completion_tokens", 0)
            cost = calculate_cost("openrouter", model, in_tokens, out_tokens)

            parsed = json.loads(raw_content)
            conf = parsed.get("confidence", {})
            if isinstance(conf, str):
                conf = {"level": "high", "reason": conf}

            return QuestionAnalysisResult(
                question=parsed.get("question", question_text),
                suggested_answer=parsed.get("suggested_answer", "A").upper(),
                answer_text=parsed.get("answer_text", options.get(parsed.get("suggested_answer", "A"), "")),
                explanation=parsed.get("explanation", ""),
                option_analysis=parsed.get("option_analysis", {}),
                confidence=ConfidenceModel(
                    level=conf.get("level", "high"),
                    reason=conf.get("reason", "OpenRouter multi-model consensus verification")
                ),
                subject=parsed.get("subject", subject or "General"),
                needs_review=parsed.get("needs_review", False),
                input_tokens=in_tokens,
                output_tokens=out_tokens,
                estimated_cost=cost
            )

    async def chat(
        self,
        api_key: str,
        model: str,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "HTTP-Referer": "https://exampilot.gtinnox.com",
            "X-Title": "ExamPilot 2.0",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": 0.4
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"OpenRouter API error ({resp.status_code}): {resp.text}")
            data = resp.json()
            usage = data.get("usage", {})
            in_tokens = usage.get("prompt_tokens", 0)
            out_tokens = usage.get("completion_tokens", 0)
            cost = calculate_cost("openrouter", model, in_tokens, out_tokens)

            return {
                "content": data["choices"][0]["message"]["content"],
                "input_tokens": in_tokens,
                "output_tokens": out_tokens,
                "estimated_cost": cost
            }

