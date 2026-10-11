"""
ExamPilot AI Response Parser & Validator Module
GT InnoX LLP
"""

import json
import re
from typing import Dict, Any, Tuple, Optional
from desktop.utils.logger import logger

class ResponseParser:
    """Extracts, cleans, and validates structured JSON from AI outputs."""

    # Regex to extract JSON block even if model includes markdown ```json ... ```
    JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)

    # Patterns for hallucinated URLs or citations
    URL_PATTERN = re.compile(r"https?:\/\/[^\s\)\"\'>]+", re.IGNORECASE)
    CITATION_PATTERN = re.compile(r"\[(?:(?:cite|ref|source|journal)\s*[:=]?\s*|doi:)[^\]]+\]", re.IGNORECASE)

    REQUIRED_KEYS = ["suggested_answer", "explanation", "option_analysis"]

    def _attempt_repair_truncated_json(self, text: str) -> Optional[dict]:
        """Attempt to close truncated JSON strings, objects, or arrays."""
        candidate = text.strip()
        # Count open braces and quotes
        open_braces = candidate.count("{") - candidate.count("}")
        quote_count = candidate.count('"') - candidate.count('\\"')

        repaired = candidate
        if quote_count % 2 != 0:
            repaired += '"'
        if open_braces > 0:
            repaired += "}" * open_braces

        try:
            return json.loads(repaired)
        except Exception:
            return None

    def parse(self, raw_output: str, original_options: Optional[Dict[str, str]] = None) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Parses raw AI text output into validated structured dictionary.
        Returns:
            (is_valid, parsed_dict, error_message)
        """
        if not raw_output or not raw_output.strip():
            return False, None, "AI returned an empty response."

        cleaned = raw_output.strip()

        # Check for markdown code fences
        match = self.JSON_BLOCK_RE.search(cleaned)
        if match:
            candidate = match.group(1).strip()
        else:
            # Look for the first '{' and last '}'
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = cleaned[start:end + 1]
            else:
                candidate = cleaned

        # Attempt JSON decoding
        data = None
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError as e:
            # Try to fix common trailing commas
            candidate_fixed = re.sub(r",\s*([\}\]])", r"\1", candidate)
            try:
                data = json.loads(candidate_fixed)
            except Exception:
                # Try repairing truncated braces
                data = self._attempt_repair_truncated_json(candidate)
                if not data:
                    logger.warning(f"Failed to parse JSON response: {e}. Content: {cleaned[:180]}")
                    return False, None, f"Malformed JSON output from model: {e}"

        if not isinstance(data, dict):
            return False, None, "AI response was not a JSON object."

        # Intelligent recovery for truncated keys
        if "suggested_answer" not in data and original_options:
            reasoning_str = (str(data.get("reasoning", "")) + " " + str(data.get("explanation", ""))).lower()
            for opt_letter, opt_val in sorted(original_options.items(), key=lambda x: -len(x[1])):
                if opt_val.strip() and opt_val.strip().lower() in reasoning_str:
                    data["suggested_answer"] = opt_letter
                    break

        if "explanation" not in data and "reasoning" in data:
            data["explanation"] = data["reasoning"]

        if "option_analysis" not in data and original_options:
            data["option_analysis"] = {k: f"Option {k}: {v}" for k, v in original_options.items()}

        # Verify required keys
        for key in self.REQUIRED_KEYS:
            if key not in data:
                return False, None, f"Missing required field in AI output: '{key}'"

        # Sanitize explanation from hallucinated URLs or invented citations
        explanation = str(data.get("explanation", "")).strip()
        explanation = self.URL_PATTERN.sub("[Reference removed]", explanation)
        explanation = self.CITATION_PATTERN.sub("", explanation)
        data["explanation"] = explanation

        # Validate suggested_answer
        suggested = str(data.get("suggested_answer", "")).strip().upper()
        
        # Clean potential prefixes like "OPTION B", "(B)", "B)", "B: QUEUE"
        opt_match = re.search(r"\b([A-G])\b", suggested)
        if opt_match:
            suggested = opt_match.group(1)
        elif original_options:
            # Model may have output the answer text instead of letter (e.g. "Queue")
            clean_sug = suggested.lower()
            for opt_letter, opt_val in original_options.items():
                if opt_val.strip().lower() == clean_sug or clean_sug in opt_val.strip().lower():
                    suggested = opt_letter
                    break

        data["suggested_answer"] = suggested

        # Semantic option verification:
        # Cross-verify whether the model's textual reasoning conclusion specifies an exact option value
        if original_options and len(original_options) >= 2:
            reasoning_text = str(data.get("reasoning", "")).strip().lower()
            if reasoning_text:
                matches = []
                for opt_let, opt_val in original_options.items():
                    words = re.findall(r"\b[a-zA-Z0-9]+\b", opt_val.lower())
                    if not words:
                        continue
                    pattern = r"\b" + r"[\s,]+".join(words) + r"\b"
                    if re.search(pattern, reasoning_text):
                        matches.append((opt_let, len(words), len(opt_val)))

                if matches:
                    matches.sort(key=lambda x: (x[1], x[2]), reverse=True)
                    best_match_letter = matches[0][0]
                    # If current suggested letter does not match the best verified text in reasoning
                    current_val = original_options.get(suggested, "").lower()
                    current_words = re.findall(r"\b[a-zA-Z0-9]+\b", current_val)
                    current_pattern = r"\b" + r"[\s,]+".join(current_words) + r"\b" if current_words else ""
                    
                    if not current_pattern or not re.search(current_pattern, reasoning_text):
                        logger.info(f"Semantically verified suggested_answer from {suggested} to {best_match_letter} ('{original_options[best_match_letter]}') based on explicit reasoning deduction.")
                        suggested = best_match_letter
                        data["suggested_answer"] = best_match_letter

        # Match answer_text from original options
        if original_options:
            if suggested in original_options:
                data["answer_text"] = original_options[suggested]
            elif "answer_text" not in data:
                data["answer_text"] = ""

        # Validate confidence score (ensure float 0.0 - 1.0)
        try:
            conf = float(data.get("confidence", 0.85))
            if conf > 1.0:
                conf = conf / 100.0 if conf <= 100.0 else 0.95
            data["confidence"] = max(0.0, min(1.0, round(conf, 3)))
        except (ValueError, TypeError):
            data["confidence"] = 0.85

        # Validate needs_review
        data["needs_review"] = bool(data.get("needs_review", False))

        # Validate option_analysis is a dict
        if not isinstance(data.get("option_analysis"), dict):
            data["option_analysis"] = {}

        return True, data, ""

response_parser = ResponseParser()
