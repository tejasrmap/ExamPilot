"""
ExamPilot Ollama Local AI Client
Connects strictly to Ollama local API (localhost:11434).
GT InnoX LLP
"""

import json
import requests
import subprocess
import shutil
from typing import Dict, Any, List, Optional, Tuple, Callable
from desktop.ai.model_config import model_config
from desktop.ai.prompts import SYSTEM_PROMPT, build_mcq_prompt
from desktop.ai.response_parser import response_parser
from desktop.security.privacy import PrivacyGuard
from desktop.utils.logger import logger

class OllamaClient:
    """Robust client for local Ollama inference runtime."""

    def __init__(self, host: Optional[str] = None):
        self.host = (host or model_config.host).rstrip("/")
        if not PrivacyGuard.verify_url_is_local(self.host):
            raise ValueError(f"ExamPilot security policy prohibits external endpoints: {self.host}")

    def is_service_running(self) -> bool:
        """Check if local Ollama daemon is active and responsive."""
        try:
            res = requests.get(f"{self.host}/api/tags", timeout=1.0)
            return res.status_code == 200
        except Exception:
            return False

    def is_ollama_installed(self) -> bool:
        """Check if ollama CLI binary exists on the system PATH or standard folders."""
        if shutil.which("ollama"):
            return True
        import os
        from pathlib import Path
        localapp = Path(os.environ.get("LOCALAPPDATA", ""))
        default_ollama = localapp / "Programs" / "Ollama" / "ollama.exe"
        return default_ollama.exists()

    def ensure_service_running(self) -> bool:
        """Check if Ollama service is active. If not, auto-start in background."""
        if self.is_service_running():
            return True

        ollama_bin = shutil.which("ollama")
        if not ollama_bin:
            import os
            from pathlib import Path
            localapp = Path(os.environ.get("LOCALAPPDATA", ""))
            candidate = localapp / "Programs" / "Ollama" / "ollama.exe"
            if candidate.exists():
                ollama_bin = str(candidate)

        if not ollama_bin:
            return False

        try:
            logger.info(f"Auto-starting local Ollama service: {ollama_bin} serve...")
            import os, subprocess, time
            creation_flags = 0
            if os.name == 'nt':
                creation_flags = subprocess.CREATE_NO_WINDOW | getattr(subprocess, 'DETACHED_PROCESS', 0)

            subprocess.Popen(
                [ollama_bin, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=creation_flags
            )

            for _ in range(12):
                time.sleep(0.5)
                if self.is_service_running():
                    logger.info("Ollama service is now active and responsive.")
                    return True
        except Exception as e:
            logger.error(f"Failed to auto-start Ollama service: {e}", exc_info=True)

        return self.is_service_running()

    def list_installed_models(self) -> List[Dict[str, Any]]:
        """List all models currently installed locally in Ollama."""
        if not self.is_service_running():
            return []
        try:
            res = requests.get(f"{self.host}/api/tags", timeout=2.0)
            if res.status_code == 200:
                data = res.json()
                models = data.get("models", [])
                result = []
                for m in models:
                    name = m.get("name", "")
                    size_gb = round(m.get("size", 0) / (1024 ** 3), 2)
                    modified_at = m.get("modified_at", "")
                    result.append({
                        "name": name,
                        "size_gb": size_gb,
                        "modified_at": modified_at
                    })
                return result
        except Exception as e:
            logger.warning(f"Failed to query installed Ollama models: {e}")
        return []

    def check_model_exists(self, model_name: str) -> bool:
        """Check if a specific model is pulled and ready locally."""
        installed = self.list_installed_models()
        req_norm = model_name.lower().strip()
        req_base = req_norm.split(":")[0]
        req_tag = req_norm.split(":")[1] if ":" in req_norm else "latest"

        for m in installed:
            m_norm = m["name"].lower().strip()
            m_base = m_norm.split(":")[0]
            m_tag = m_norm.split(":")[1] if ":" in m_norm else "latest"
            
            # Exact match (e.g. qwen2.5:1.5b == qwen2.5:1.5b)
            if m_norm == req_norm:
                return True
            # Base and tag match (handling implicit :latest)
            if m_base == req_base and m_tag == req_tag:
                return True
        return False

    def pull_model(self, model_name: str, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Tuple[bool, str]:
        """
        Stream pull a model into local Ollama storage.
        `progress_callback` receives progress updates: {"status": str, "completed": int, "total": int, "percent": float}
        """
        try:
            url = f"{self.host}/api/pull"
            payload = {"name": model_name, "stream": True}
            logger.info(f"Initiating Ollama model pull for '{model_name}'...")
            
            with requests.post(url, json=payload, stream=True, timeout=1200) as response:
                if response.status_code != 200:
                    return False, f"Server responded with error status {response.status_code}: {response.text}"
                
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        status = chunk.get("status", "")
                        total = chunk.get("total", 0)
                        completed = chunk.get("completed", 0)
                        percent = round((completed / total * 100), 1) if total > 0 else 0.0

                        if progress_callback:
                            progress_callback({
                                "status": status,
                                "completed": completed,
                                "total": total,
                                "percent": percent
                            })

                        if "error" in chunk:
                            return False, chunk["error"]

            logger.info(f"Model '{model_name}' downloaded successfully.")
            return True, "Download completed successfully."

        except Exception as e:
            logger.error(f"Error pulling model '{model_name}': {e}", exc_info=True)
            return False, str(e)

    def generate_answer(
        self,
        question_text: str,
        options: Dict[str, str],
        subject: str = "General",
        model: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Generates structured MCQ analysis with automatic retries on malformed JSON.
        Returns:
            (success, parsed_data, error_message)
        """
        if not self.ensure_service_running():
            return False, None, "Ollama service is not running on 127.0.0.1:11434. Please start Ollama."

        target_model = model or model_config.active_model
        
        # Verify model exists; if not, check fallback
        if not self.check_model_exists(target_model):
            if model_config.fallback_model and self.check_model_exists(model_config.fallback_model):
                logger.warning(f"Target model '{target_model}' not found, falling back to installed '{model_config.fallback_model}'")
                target_model = model_config.fallback_model
            else:
                installed_list = [m['name'] for m in self.list_installed_models()]
                if installed_list:
                    target_model = installed_list[0]
                    logger.info(f"Using installed local model '{target_model}'")
                else:
                    return False, None, f"Model '{target_model}' is not installed locally. Please download it via the AI Model Manager."

        prompt_text = build_mcq_prompt(question_text, options, subject)
        url = f"{self.host}/api/generate"
        payload = {
            "model": target_model,
            "system": SYSTEM_PROMPT,
            "prompt": prompt_text,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.0,  # Zero temperature for deterministic factual accuracy
                "top_p": 0.9,
                "num_predict": 1024
            }
        }

        # Attempt with retry
        max_attempts = model_config.max_retries + 1
        last_error = ""

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Sending prompt to Ollama '{target_model}' (attempt {attempt}/{max_attempts})...")
                res = requests.post(url, json=payload, timeout=model_config.timeout_seconds)
                
                if res.status_code != 200:
                    last_error = f"Ollama HTTP error {res.status_code}: {res.text}"
                    continue

                raw_json = res.json()
                raw_response = raw_json.get("response", "")

                is_valid, parsed_data, parse_err = response_parser.parse(raw_response, options)
                if is_valid and parsed_data:
                    parsed_data["model_used"] = target_model
                    return True, parsed_data, ""

                last_error = f"Validation error: {parse_err}"
                logger.warning(f"Attempt {attempt} returned invalid JSON: {parse_err}. Raw: {raw_response[:300]}")

            except requests.Timeout:
                last_error = f"Ollama inference timed out after {model_config.timeout_seconds}s."
                logger.warning(last_error)
            except Exception as e:
                last_error = f"Connection error to Ollama: {e}"
                logger.warning(last_error)

        return False, None, f"Failed to obtain valid AI answer. Details: {last_error}"

ollama_client = OllamaClient()
