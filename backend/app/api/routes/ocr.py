import base64
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from backend.app.core.deps import get_optional_current_user
from backend.app.services.ocr import ocr_engine
from backend.app.services.parser import QuestionParser
from backend.app.services.domain_detector import detect_domain

router = APIRouter(prefix="/ocr", tags=["OCR & Document Extraction"])
parser = QuestionParser()

class Base64ScanRequest(BaseModel):
    image_base64: str

@router.get("/status")
def get_ocr_status():
    return {
        "engine": "RapidOCR (PaddleOCR ONNX)",
        "ready": ocr_engine.is_ready(),
        "error": ocr_engine.get_error()
    }

@router.post("/image")
async def scan_image(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None)
):
    """
    Performs preprocessing, RapidOCR extraction, spatial sorting,
    and automatic QuestionParser identification.
    """
    image_bytes = None
    if file:
        image_bytes = await file.read()
    elif image_base64:
        clean_b64 = image_base64
        if "base64," in clean_b64:
            clean_b64 = clean_b64.split("base64,")[1]
        try:
            image_bytes = base64.b64decode(clean_b64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 encoding: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Either file upload or image_base64 form field is required.")

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image received.")

    # 1. Run OCR
    ocr_result = ocr_engine.extract_from_bytes(image_bytes)
    if ocr_result.get("error"):
        raise HTTPException(status_code=500, detail=ocr_result["error"])

    raw_text = ocr_result["text"]
    
    # 2. Parse MCQ structure
    parsed_mcq = parser.parse_from_text(raw_text)

    # 3. Detect academic domain
    q_text = parsed_mcq.get("question") or raw_text
    detected_domain = detect_domain(q_text)

    return {
        "raw_text": raw_text,
        "ocr_confidence": ocr_result["confidence"],
        "lines": ocr_result["lines"],
        "parsed_question": parsed_mcq.get("question") or "",
        "options": parsed_mcq.get("options") or {},
        "structured_options": parsed_mcq.get("structured_options") or [],
        "has_original_labels": parsed_mcq.get("has_original_labels", False),
        "detected_domain": detected_domain,
        "validation_issues": parsed_mcq.get("validation_issues") or [],
        "is_ambiguous": parsed_mcq.get("is_ambiguous", False),
        "ambiguity_details": parsed_mcq.get("ambiguity_details") or [],
        "needs_correction": parsed_mcq.get("needs_correction", False)
    }

@router.post("/pdf")
async def scan_pdf(
    file: UploadFile = File(...),
    max_pages: int = Form(15)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF document.")
    
    pdf_bytes = await file.read()
    res = ocr_engine.extract_from_pdf_bytes(pdf_bytes, max_pages=max_pages)
    if res.get("error"):
        raise HTTPException(status_code=500, detail=res["error"])

    # Process each page to find MCQ questions
    extracted_questions = []
    for page in res["pages"]:
        parsed = parser.parse_from_text(page["text"])
        if parsed.get("question") and len(parsed.get("options", {})) >= 2:
            domain = detect_domain(parsed["question"])
            extracted_questions.append({
                "page_number": page["page_number"],
                "question": parsed["question"],
                "options": parsed["options"],
                "subject": domain,
                "confidence": page["confidence"]
            })

    return {
        "filename": file.filename,
        "total_pages": res["total_pages"],
        "processed_pages": res["processed_pages"],
        "questions_found": len(extracted_questions),
        "questions": extracted_questions,
        "pages": res["pages"]
    }

