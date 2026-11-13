import io
from PIL import Image, ImageDraw, ImageFont
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.parser import QuestionParser
from backend.app.services.ocr import ocr_engine

client = TestClient(app)

def test_ocr_engine_synthetic_image():
    # Create a clean synthetic image with an MCQ
    img = Image.new("RGB", (800, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    text = (
        "1. What does CPU stand for?\n"
        "A) Central Processing Unit\n"
        "B) Computer Personal Unit\n"
        "C) Central Processor Utility\n"
        "D) Control Power Unit"
    )
    draw.text((20, 20), text, fill=(0, 0, 0))
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    res = ocr_engine.extract_from_bytes(buf.getvalue())
    assert res["error"] is None
    assert len(res["lines"]) >= 3
    assert "Central Processing Unit" in res["text"] or "CPU" in res["text"]

def test_question_parser_variations():
    parser = QuestionParser()

    # Variation 1: Standard numbered question
    text1 = (
        "1. What is the primary function of an operating system?\n"
        "A) Managing hardware resources\n"
        "B) Compiling source code\n"
        "C) Designing web pages\n"
        "D) Sending emails"
    )
    res1 = parser.parse_from_text(text1)
    assert res1["question"] == "What is the primary function of an operating system?"
    assert len(res1["options"]) == 4
    assert res1["options"]["A"] == "Managing hardware resources"

    # Variation 2: Fill in the blank
    text2 = (
        "During the ______ phase, data teams determine what data is required and who is responsible.\n"
        "A) capture\n"
        "B) planning\n"
        "C) analyze\n"
        "D) manage"
    )
    res2 = parser.parse_from_text(text2)
    assert "During the" in res2["question"]
    assert len(res2["options"]) == 4

def test_ocr_api_endpoint():
    img = Image.new("RGB", (600, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "What is RAM?\nA) Random Access Memory\nB) Read Access Memory", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    response = client.post(
        "/api/ocr/image",
        files={"file": ("test_mcq.png", buf.getvalue(), "image/png")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "raw_text" in data
    assert "parsed_question" in data
    assert "options" in data

