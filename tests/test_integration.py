"""
End-to-End Integration Tests for ExamPilot
GT InnoX LLP
"""

import tempfile
import pytest
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from desktop.core.ocr_engine import ocr_engine
from desktop.core.question_parser import question_parser
from desktop.core.confidence_engine import confidence_engine
from desktop.database.database import DatabaseManager
from desktop.database.repository import Repository
from desktop.database.models import QuestionModel

def render_mcq_image(question: str, options: dict) -> Image.Image:
    """Render high-clarity synthetic MCQ image for deterministic OCR testing."""
    img = Image.new("RGB", (750, 320), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Try loading high-clarity font
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()

    y = 25
    draw.text((30, y), question, fill=(0, 0, 0), font=font)
    y += 50

    for opt, val in sorted(options.items()):
        draw.text((40, y), f"{opt}) {val}", fill=(10, 10, 10), font=font)
        y += 45

    return img

def test_end_to_end_pipeline():
    if not ocr_engine.is_available():
        pytest.skip("OCR Engine not available in current test environment.")

    # 1. Generate practice question image
    test_q = "What is the capital city of Australia?"
    test_opts = {
        "A": "Sydney",
        "B": "Melbourne",
        "C": "Canberra",
        "D": "Brisbane"
    }
    img = render_mcq_image(test_q, test_opts)

    # 2. Perform OCR extraction
    ocr_res = ocr_engine.extract_text(img)
    assert ocr_res["success"] is True, f"OCR extraction failed: {ocr_res.get('error')}"
    assert len(ocr_res["lines"]) >= 3, "OCR extracted fewer than 3 lines"

    # 3. Parse extracted lines
    parsed = question_parser.parse_from_lines(ocr_res["lines"])
    assert "australia" in parsed["question"].lower() or "capital" in parsed["question"].lower()
    assert len(parsed["options"]) >= 2

    # 4. Simulate structured AI answer resolution
    suggested_answer = "C"
    explanation = "Canberra is the purpose-built federal capital city of Australia."
    opt_analysis = {
        "A": "Sydney is the most populous city but not the capital.",
        "B": "Melbourne was the temporary seat until 1927.",
        "C": "Canberra was founded as the official capital in 1913.",
        "D": "Brisbane is the state capital of Queensland."
    }

    calibrated_conf = confidence_engine.calibrate(
        ai_confidence=0.96,
        explanation=explanation,
        option_analysis=opt_analysis,
        suggested_answer=suggested_answer,
        total_options=len(parsed["options"])
    )
    assert calibrated_conf > 0.85

    # 5. Persist to SQLite Database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    try:
        manager = DatabaseManager(db_path=db_path)
        repo = Repository(manager=manager)

        q_model = QuestionModel(
            question_text=parsed["question"],
            options=parsed["options"],
            suggested_answer=suggested_answer,
            answer_text="Canberra",
            explanation=explanation,
            option_analysis=opt_analysis,
            confidence=calibrated_conf,
            subject_name="General Knowledge"
        )
        saved_id = repo.save_question(q_model)
        assert saved_id > 0

        # 6. Verify retrieval and analytics
        retrieved = repo.get_question_by_id(saved_id)
        assert retrieved is not None
        assert retrieved.suggested_answer == "C"

        analytics = repo.get_dashboard_analytics()
        assert analytics["total_questions"] == 1
        assert analytics["accuracy"] == 100.0
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except Exception:
            pass
