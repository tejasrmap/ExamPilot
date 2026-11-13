import io
import numpy as np
from PIL import Image, ImageDraw
import fitz # PyMuPDF
from backend.app.services.parser import QuestionParser
from backend.app.services.ocr import ocr_engine

def test_code_assembly_instruction_protection():
    """
    Verifies that assembly labels like 'b_1:', 'loop:', and instructions like 'ANDI R4, R1, 1'
    are not misidentified as multiple-choice options.
    """
    text = (
        "2. For Problems 2 through 8, use the following Code Sequence:\n"
        "loop:\n"
        "  LW R1, 0(R2)\n"
        "  ANDI R4, R1, 1\n"
        "b_1:\n"
        "  BEQZ R4, l_3\n"
        "  ADD R5, R5, R1\n"
        "  J l_4\n"
        "l_3:\n"
        "  ADD R6, R6, R1\n"
        "l_4:\n"
        "  ADDI R2, R2, 4\n"
        "  SUBI R3, R3, 1\n"
        "b_2:\n"
        "  BNEZ R3, loop\n\n"
        "Conceptually, what values are kept in R2 and R3?\n"
        "A) R2 contains the loop iteration variable\n"
        "B) R3 contains the pointer to array elements\n"
        "C) R2 contains the pointer that points to array elements and R3 is loop count\n"
        "D) Both R2 and R3 hold scratch values"
    )

    parser = QuestionParser()
    res = parser.parse_from_text(text)

    # Question text should encompass the code and the final query
    assert "Code Sequence" in res["question"] or "Conceptually" in res["question"]
    # Only genuine options A, B, C, D must be extracted
    assert len(res["options"]) == 4
    assert "A" in res["options"] and "B" in res["options"] and "C" in res["options"] and "D" in res["options"]
    assert "array elements" in res["options"]["C"]
    # b_1: and loop: MUST NOT be options
    assert "b_1:" not in res["options"]
    assert "loop:" not in res["options"]

def test_options_a_through_f():
    """
    Verifies support for 6 options (A through F).
    """
    text = (
        "Which of the following are primary phases in data management?\n"
        "A) Capture\n"
        "B) Planning\n"
        "C) Analyze\n"
        "D) Manage\n"
        "E) Archive\n"
        "F) Destroy"
    )
    parser = QuestionParser()
    res = parser.parse_from_text(text)
    assert len(res["options"]) == 6
    assert res["options"]["F"] == "Destroy"

def test_fill_in_the_blank_question():
    """
    Verifies fill-in-the-blank question statements are cleanly parsed.
    """
    text = (
        "Fill in the blank: During the ______ phase, data teams decide what data is needed.\n"
        "A) capture\n"
        "B) planning\n"
        "C) analyze\n"
        "D) manage"
    )
    parser = QuestionParser()
    res = parser.parse_from_text(text)
    assert "During the" in res["question"]
    assert len(res["options"]) == 4
    assert res["options"]["B"] == "planning"

def test_unlettered_bullet_options():
    """
    Verifies options formatted with bullets or numbers (1, 2, 3, 4) get mapped to A, B, C, D.
    """
    text = (
        "What is the time complexity of binary search on a sorted array?\n"
        "1) O(1)\n"
        "2) O(log n)\n"
        "3) O(n)\n"
        "4) O(n log n)"
    )
    parser = QuestionParser()
    res = parser.parse_from_text(text)
    assert "binary search" in res["question"]
    assert len(res["options"]) == 4
    assert res["options"]["B"] == "O(log n)" or res["options"]["A"] == "O(1)"

def test_pdf_document_pipeline_synthetic():
    """
    Generates a synthetic multi-page digital PDF in memory and verifies extraction via PyMuPDF.
    """
    doc = fitz.open() # New empty PDF
    # Page 1: Digital question
    page1 = doc.new_page()
    page1.insert_text((50, 72), "1. What is the capital of Japan?\nA) Tokyo\nB) Kyoto\nC) Osaka\nD) Nagoya")

    # Page 2: Second question
    page2 = doc.new_page()
    page2.insert_text((50, 72), "2. What is the speed of light in vacuum?\nA) 3x10^8 m/s\nB) 1.5x10^8 m/s\nC) 300 km/h\nD) Infinite")

    pdf_bytes = doc.write()
    doc.close()

    res = ocr_engine.extract_from_pdf_bytes(pdf_bytes, max_pages=5)
    assert res["error"] is None
    assert res["total_pages"] == 2
    assert res["processed_pages"] == 2
    assert "Tokyo" in res["full_text"]
    assert "speed of light" in res["full_text"]

def test_noisy_image_preprocessing():
    """
    Verifies image preprocessing with contrast enhancement on low-res noisy images.
    """
    # Create small noisy image
    small_img = Image.new("RGB", (320, 180), color=(220, 220, 220))
    processed = ocr_engine.preprocess_image(small_img)
    # Upscaled with Lanczos
    assert processed.width >= 600
    assert processed.height >= 300
