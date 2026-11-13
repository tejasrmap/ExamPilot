"""
ExamPilot Answer Generation & Analysis Engine
GT InnoX LLP
"""

from typing import Dict, Any, Tuple, Optional, List
from desktop.ai.domain_detector import detect_domain, detect_domain_with_details
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
        model: Optional[str] = None,
        structured_options: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Coordinates full MCQ question analysis pipeline with stable option identity and curriculum grounding.
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

        # Step 1b: Auto-detect domain with curriculum evidence
        domain_details = detect_domain_with_details(clean_q, clean_opts)
        if not subj or subj in ["General", "Auto-Detect", "⚡ Auto-Detect Domain"] or subj.startswith("⚡"):
            subj = domain_details["subject"]

        # Step 2: Query Ollama
        success, ai_data, ai_err = self.client.generate_answer(
            clean_q, clean_opts, subject=subj, model=model
        )
        if not success or not ai_data:
            return False, None, ai_err

        ai_data["detected_subject"] = subj
        ai_data["subject_confidence"] = domain_details.get("subject_confidence", 0.80)
        ai_data["curriculum_confidence"] = domain_details.get("curriculum_confidence", 0.0)
        if not ai_data.get("evidence"):
            ai_data["evidence"] = domain_details.get("evidence")

        # Map option identity
        suggested = ai_data.get("suggested_answer", "")
        if structured_options:
            ai_data["structured_options"] = structured_options
            matching_opt = next((o for o in structured_options if o.get("internal_label") == suggested), None)
            if matching_opt:
                ai_data["original_label"] = matching_opt.get("original_label")
                ai_data["source_position"] = matching_opt.get("source_order")
        else:
            ai_data["original_label"] = None
            ai_data["source_position"] = (ord(suggested.upper()) - ord('A') + 1) if len(suggested) == 1 and suggested.isalpha() else None

        # Step 3: Calibrate confidence
        raw_conf = ai_data.get("confidence", 0.85)
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

