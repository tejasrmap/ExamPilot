"""
ExamPilot Confidence Calibration Engine
Computes calibrated heuristic certainty based on linguistic certainty,
option distinctiveness, and model response indicators.
GT InnoX LLP
"""

import re
from typing import Dict, Any

class ConfidenceEngine:
    """Calibrates confidence scores avoiding raw uncalibrated probabilities."""

    # Words indicating uncertainty or ambiguity
    HEDGE_WORDS = [
        "maybe", "perhaps", "possibly", "unclear", "ambiguous",
        "might be", "could be", "arguable", "debatable", "depending on"
    ]

    # Words indicating decisive proof
    STRONG_AFFIRMATIONS = [
        "by definition", "strictly", "universally", "fundamental",
        "axiom", "standardized", "guaranteed", "always"
    ]

    def calibrate(self, ai_confidence: float, explanation: str, option_analysis: Dict[str, str], suggested_answer: str, total_options: int) -> float:
        """
        Calibrate model self-reported confidence with linguistic features.
        Returns a float between 0.10 and 0.99.
        """
        score = float(ai_confidence)
        lower_exp = explanation.lower()

        # Deduct if hedge words exist in explanation
        for hedge in self.HEDGE_WORDS:
            if hedge in lower_exp:
                score -= 0.12
                break

        # Bonus for rigorous option analysis
        if len(option_analysis) >= total_options:
            score += 0.05

        # Check if selected option explanation is strong
        if suggested_answer in option_analysis:
            ans_exp = option_analysis[suggested_answer].lower()
            for strong in self.STRONG_AFFIRMATIONS:
                if strong in ans_exp:
                    score += 0.04
                    break

        # Clamp between 0.20 and 0.99
        calibrated = max(0.20, min(0.99, round(score, 2)))
        return calibrated

confidence_engine = ConfidenceEngine()

