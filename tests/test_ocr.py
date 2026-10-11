"""
Unit Tests for ExamPilot OCR Engine
GT InnoX LLP
"""

from PIL import Image, ImageDraw, ImageFont
from desktop.core.ocr_engine import ocr_engine
from desktop.core.question_parser import question_parser

def create_synthetic_mcq_image(question: str, options: dict) -> Image.Image:
    """Render a synthetic clear MCQ image for testing OCR."""
    img = Image.new("RGB", (750, 320), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()

    y = 25
    draw.text((30, y), question, fill=(0, 0, 0), font=font)
    y += 50

    for opt, text in sorted(options.items()):
        draw.text((40, y), f"{opt}) {text}", fill=(10, 10, 10), font=font)
        y += 45

    return img

def test_ocr_extraction_on_synthetic_image():
    if not ocr_engine.is_available():
        return  # Skip if environment lacks onnx

    test_q = "Which scheduling algorithm is non-preemptive?"
    test_opts = {
        "A": "Round Robin",
        "B": "First-Come First-Served",
        "C": "Shortest Remaining Time",
        "D": "Priority Preemptive"
    }
    img = create_synthetic_mcq_image(test_q, test_opts)

    result = ocr_engine.extract_text(img)
    assert result["success"] is True
    assert len(result["lines"]) > 0
    assert result["avg_confidence"] > 0.5

    # Check parser works on OCR output
    parsed = question_parser.parse_from_lines(result["lines"])
    q_norm = parsed["question"].lower().replace(" ", "")
    assert "scheduling" in q_norm or "preemptive" in q_norm
    assert len(parsed["options"]) >= 2

