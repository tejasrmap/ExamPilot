import json
import httpx
from typing import Dict, List, Optional, Any
from backend.app.providers.base import BaseAIProvider, ModelInfo, QuestionAnalysisResult, ConfidenceModel
from backend.app.providers.models_catalog import CATALOG, calculate_cost
from backend.app.providers.prompt_builder import ANALYSIS_SYSTEM_PROMPT, build_analysis_user_prompt
from backend.app.providers.http_utils import execute_provider_request_with_retry

class GeminiProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "gemini"

    async def validate_key(self, api_key: str) -> bool:
        """Validates Google Gemini API key by calling list models endpoint."""
        if not api_key:
            return False
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key.strip()}"
            resp = await execute_provider_request_with_retry("GET", url, timeout=10.0, max_retries=1)
            return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self, api_key: Optional[str] = None) -> List[ModelInfo]:
        return CATALOG.get("gemini", [])

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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key.strip()}"
        
        payload = {
            "system_instruction": {
                "parts": [{"text": ANALYSIS_SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }

        resp = await execute_provider_request_with_retry(
            "POST", url, json_data=payload, timeout=45.0, max_retries=2
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")
        
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("No candidate response returned from Gemini")
        
        raw_text = candidates[0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})
        in_tokens = usage.get("promptTokenCount", 0)
        out_tokens = usage.get("candidatesTokenCount", 0)
        cost = calculate_cost("gemini", model, in_tokens, out_tokens)

        parsed = json.loads(raw_text)
        conf = parsed.get("confidence", {})
        if isinstance(conf, str):
            conf = {"level": "medium", "reason": conf}

        return QuestionAnalysisResult(
            question=parsed.get("question", question_text),
            suggested_answer=parsed.get("suggested_answer", "A").upper(),
            answer_text=parsed.get("answer_text", options.get(parsed.get("suggested_answer", "A"), "")),
            explanation=parsed.get("explanation", ""),
            option_analysis=parsed.get("option_analysis", {}),
            confidence=ConfidenceModel(
                level=conf.get("level", "high"),
                reason=conf.get("reason", "Direct deductive and empirical verification")
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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key.strip()}"
        
        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": m["content"]}]
            })
            
        payload = {
            "contents": contents,
            "generationConfig": {"temperature": 0.4}
        }
        if system_prompt:
            payload["system_instruction"] = {"parts": [{"text": system_prompt}]}

        resp = await execute_provider_request_with_retry(
            "POST", url, json_data=payload, timeout=45.0, max_retries=2
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")
        data = resp.json()
        candidates = data.get("candidates", [])
        text = candidates[0]["content"]["parts"][0]["text"] if candidates else ""
        usage = data.get("usageMetadata", {})
        in_tokens = usage.get("promptTokenCount", 0)
        out_tokens = usage.get("candidatesTokenCount", 0)
        cost = calculate_cost("gemini", model, in_tokens, out_tokens)

        return {
            "content": text,
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "estimated_cost": cost
        }
