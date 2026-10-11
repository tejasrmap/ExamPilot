"""
ExamPilot Security & Validation Module
GT InnoX LLP
"""

import re
from typing import Dict, Any, Tuple, Optional

def sanitize_text(text: str) -> str:
    """Strip dangerous characters or excessive whitespace while preserving math symbols."""
    if not text:
        return ""
    # Normalize unicode spaces, strip null bytes
    clean = text.replace("\x00", "").strip()
    return clean

def validate_question_payload(data: Any) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Validate that question data complies with ExamPilot structured format.
    Requires at least a non-empty question and at least 2 options.
    """
    if not isinstance(data, dict):
        return False, "Payload must be a JSON object", None

    question_text = sanitize_text(data.get("question", ""))
    if not question_text or len(question_text) < 3:
        return False, "Question text must be at least 3 characters", None

    options = data.get("options")
    if not isinstance(options, dict) or len(options) < 2:
        return False, "MCQ must contain at least 2 distinct options", None

    clean_options = {}
    for key, val in options.items():
        key_str = str(key).strip().upper()
        val_str = sanitize_text(str(val))
        if not val_str:
            return False, f"Option '{key_str}' has empty content", None
        clean_options[key_str] = val_str

    sanitized = {
        "question": question_text,
        "options": clean_options,
        "subject_name": sanitize_text(data.get("subject_name", "General"))
    }
    return True, "", sanitized

def validate_native_message(raw_msg: Any) -> Tuple[bool, str]:
    """Validate incoming Chrome extension native message schema."""
    if not isinstance(raw_msg, dict):
        return False, "Native message must be a JSON object"
    
    action = raw_msg.get("action")
    if not action or not isinstance(action, str):
        return False, "Missing or invalid 'action' field"

    allowed_actions = ["ping", "analyze_question", "get_status", "open_desktop"]
    if action not in allowed_actions:
        return False, f"Action '{action}' is not permitted"

    return True, ""

