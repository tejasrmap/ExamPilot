import json
import httpx
from typing import Dict, List, Optional, Any
from backend.app.providers.base import BaseAIProvider, ModelInfo, QuestionAnalysisResult, ConfidenceModel
from backend.app.providers.models_catalog import CATALOG, calculate_cost
from backend.app.providers.prompt_builder import ANALYSIS_SYSTEM_PROMPT, build_analysis_user_prompt
from backend.app.providers.http_utils import execute_provider_request_with_retry

class AnthropicProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "anthropic"

    async def validate_key(self, api_key: str) -> bool:
        """Validates Anthropic API key by sending minimal request to messages endpoint."""
        if not api_key:
            return False
        try:
            headers = {
                "x-api-key": api_key.strip(),
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "ping"}]
            }
            resp = await execute_provider_request_with_retry(
                "POST", "https://api.anthropic.com/v1/messages", headers=headers, json_data=payload, timeout=10.0, max_retries=1
            )
            return resp.status_code in (200, 400) and resp.status_code != 401
        except Exception:
            return False

    async def list_models(self, api_key: Optional[str] = None) -> List[ModelInfo]:
        return CATALOG.get("anthropic", [])

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
        user_prompt += "\nRespond with valid JSON only. Do not enclose in markdown blocks."

        headers = {
            "x-api-key": api_key.strip(),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": model,
            "max_tokens": 2048,
            "system": ANALYSIS_SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_prompt}],
            "temperature": 0.1
        }

        resp = await execute_provider_request_with_retry(
            "POST", "https://api.anthropic.com/v1/messages", headers=headers, json_data=payload, timeout=45.0, max_retries=2
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Anthropic API error ({resp.status_code}): {resp.text}")
        
        data = resp.json()
        raw_text = data["content"][0]["text"].strip()
        
        # Clean possible markdown wrap
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        usage = data.get("usage", {})
        in_tokens = usage.get("input_tokens", 0)
        out_tokens = usage.get("output_tokens", 0)
        cost = calculate_cost("anthropic", model, in_tokens, out_tokens)

        parsed = json.loads(raw_text)
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
                reason=conf.get("reason", "Theoretical and conceptual consistency")
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
        headers = {
            "x-api-key": api_key.strip(),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": model,
            "max_tokens": 2048,
            "messages": messages,
            "temperature": 0.4
        }
        if system_prompt:
            payload["system"] = system_prompt

        resp = await execute_provider_request_with_retry(
            "POST", "https://api.anthropic.com/v1/messages", headers=headers, json_data=payload, timeout=45.0, max_retries=2
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Anthropic API error ({resp.status_code}): {resp.text}")
        data = resp.json()
        usage = data.get("usage", {})
        in_tokens = usage.get("input_tokens", 0)
        out_tokens = usage.get("output_tokens", 0)
        cost = calculate_cost("anthropic", model, in_tokens, out_tokens)

        return {
            "content": data["content"][0]["text"],
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "estimated_cost": cost
        }
