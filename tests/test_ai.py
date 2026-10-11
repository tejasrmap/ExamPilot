"""
Unit Tests for ExamPilot AI Engines
GT InnoX LLP
"""

import json
from desktop.ai.response_parser import response_parser
from desktop.core.confidence_engine import confidence_engine
from desktop.core.explanation_engine import explanation_engine
from desktop.ai.ollama_client import OllamaClient

def test_response_parser_clean_json():
    raw = json.dumps({
        "question": "Which data structure follows FIFO?",
        "suggested_answer": "B",
        "answer_text": "Queue",
        "explanation": "A queue follows First In First Out.",
        "option_analysis": {
            "A": "Stack follows LIFO.",
            "B": "Queue follows FIFO.",
            "C": "Tree is hierarchical.",
            "D": "Graph has cycles."
        },
        "confidence": 0.98,
        "needs_review": False
    })
    is_valid, data, err = response_parser.parse(raw)
    assert is_valid is True
    assert data["suggested_answer"] == "B"
    assert data["confidence"] == 0.98
    assert data["needs_review"] is False

def test_response_parser_markdown_fence():
    raw = """
    Here is the response:
    ```json
    {
      "suggested_answer": "Option C",
      "explanation": "Third normal form eliminates transitive dependencies.",
      "option_analysis": {
        "A": "1NF eliminates repeating groups.",
        "B": "2NF eliminates partial dependencies.",
        "C": "3NF eliminates transitive dependencies."
      },
      "confidence": 92
    }
    ```
    """
    is_valid, data, err = response_parser.parse(raw)
    assert is_valid is True
    assert data["suggested_answer"] == "C"
    assert data["confidence"] == 0.92

def test_response_parser_missing_required_keys():
    raw = json.dumps({"incomplete": "data"})
    is_valid, data, err = response_parser.parse(raw)
    assert is_valid is False
    assert "Missing required field" in err

def test_confidence_calibration():
    # Explanation with hedge words should decrease score
    calibrated_hedge = confidence_engine.calibrate(
        ai_confidence=0.90,
        explanation="This is perhaps true, but possibly ambiguous in some contexts.",
        option_analysis={"A": "opt A", "B": "opt B"},
        suggested_answer="A",
        total_options=4
    )
    assert calibrated_hedge < 0.90

    # Explanation with strong affirmations and complete option analysis
    calibrated_strong = confidence_engine.calibrate(
        ai_confidence=0.90,
        explanation="By definition, a queue strictly follows First In First Out.",
        option_analysis={"A": "LIFO", "B": "By definition, FIFO", "C": "Tree", "D": "Graph"},
        suggested_answer="B",
        total_options=4
    )
    assert calibrated_strong >= 0.95

def test_explanation_pedagogical_breakdown():
    raw = {
        "suggested_answer": "B",
        "answer_text": "Queue",
        "explanation": "Follows FIFO.",
        "option_analysis": {
            "A": "Stack follows LIFO",
            "B": "Queue follows FIFO"
        }
    }
    breakdown = explanation_engine.build_pedagogical_breakdown(raw)
    assert breakdown["suggested_answer"] == "B"
    assert len(breakdown["option_breakdowns"]) == 2
    correct_breakdown = [b for b in breakdown["option_breakdowns"] if b["is_suggested"]][0]
    assert correct_breakdown["option"] == "B"

