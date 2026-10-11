"""
ExamPilot Explanation Formatting & Enrichment Engine
GT InnoX LLP
"""

from typing import Dict, Any

class ExplanationEngine:
    """Structures explanations into pedagogical sections for enhanced understanding."""

    def format_explanation_summary(self, suggested_answer: str, answer_text: str, explanation: str) -> str:
        """Create a clean, focused summary of the correct answer."""
        return f"**Option {suggested_answer}** ({answer_text}): {explanation}"

    def build_pedagogical_breakdown(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Organizes AI analysis into key takeaways, options review, and core concept."""
        suggested = raw_data.get("suggested_answer", "")
        options_analysis = raw_data.get("option_analysis", {})
        explanation = raw_data.get("explanation", "")

        return {
            "suggested_answer": suggested,
            "answer_text": raw_data.get("answer_text", ""),
            "core_reason": explanation,
            "option_breakdowns": [
                {
                    "option": opt,
                    "is_suggested": (opt == suggested),
                    "analysis": text
                }
                for opt, text in sorted(options_analysis.items())
            ],
            "needs_review": raw_data.get("needs_review", False)
        }

explanation_engine = ExplanationEngine()

