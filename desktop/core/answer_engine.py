"""
ExamPilot Answer Generation & Analysis Engine
GT InnoX LLP
"""

from typing import Dict, Any, Tuple, Optional
from desktop.ai.domain_detector import detect_domain
from desktop.ai.ollama_client import ollama_client, OllamaClient
from desktop.core.confidence_engine import confidence_engine
from desktop.core.explanation_engine import explanation_engine
from desktop.security.validation import validate_question_payload
from desktop.utils.logger import logger

class AnswerEngine:
    """Core orchestration engine for question analysis and answer resolution."""

    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or ollama_client

    def analyze(
        self,
        question_text: str,
        options: Dict[str, str],
        subject: str = "General",
        model: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Coordinates full MCQ question analysis pipeline.
        Returns:
            (success, structured_analysis, error_message)
        """
        # Step 1: Validate payload
        payload = {"question": question_text, "options": options, "subject_name": subject}
        valid, val_err, clean_payload = validate_question_payload(payload)
        if not valid or not clean_payload:
            return False, None, f"Question validation failed: {val_err}"

        clean_q = clean_payload["question"]
        clean_opts = clean_payload["options"]
        subj = clean_payload["subject_name"]

        # Step 1b: Auto-detect domain if requested or generic
        if not subj or subj in ["General", "Auto-Detect", "⚡ Auto-Detect Domain"] or subj.startswith("⚡"):
            detected = detect_domain(clean_q, clean_opts)
            if detected:
                subj = detected

        # Step 2: Query Ollama
        success, ai_data, ai_err = self.client.generate_answer(
            clean_q, clean_opts, subject=subj, model=model
        )
        if not success or not ai_data:
            return False, None, ai_err

        ai_data["detected_subject"] = subj

        # Step 3: Calibrate confidence
        raw_conf = ai_data.get("confidence", 0.85)
        suggested = ai_data.get("suggested_answer", "")
        explanation = ai_data.get("explanation", "")
        opt_analysis = ai_data.get("option_analysis", {})

        calibrated_conf = confidence_engine.calibrate(
            raw_conf, explanation, opt_analysis, suggested, len(clean_opts)
        )
        ai_data["confidence"] = calibrated_conf

        # Step 4: Pedagogical breakdown
        breakdown = explanation_engine.build_pedagogical_breakdown(ai_data)
        ai_data["breakdown"] = breakdown

        logger.info(f"Answer generated for '{clean_q[:40]}...' -> Suggested: {suggested} (conf: {calibrated_conf})")
        return True, ai_data, ""

answer_engine = AnswerEngine()

