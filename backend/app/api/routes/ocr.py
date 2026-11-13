import base64
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.core.deps import get_current_user
from backend.app.core.rate_limit import rate_limiter
from backend.app.db.models import Profile
from backend.app.services.ocr import ocr_engine
from backend.app.services.parser import QuestionParser
from backend.app.services.domain_detector import detect_domain

logger = logging.getLogger("exampilot.ocr")
router = APIRouter(prefix="/ocr", tags=["OCR & Document Extraction"])
parser = QuestionParser()

MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

def validate_image_magic_bytes(data: bytes) -> str:
    """Verifies that byte payload begins with a valid image signature."""
    if len(data) < 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is too small to be a valid image."
        )
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid image format. Supported formats are PNG, JPEG, and WebP."
    )

def validate_pdf_magic_bytes(data: bytes) -> None:
    """Verifies that byte payload begins with the %PDF- signature."""
    if len(data) < 5 or not data.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document format. The file signature does not match a valid PDF."
        )

async def read_bounded_bytes(file: UploadFile, max_bytes: int) -> bytes:
    """Reads UploadFile in chunks, aborting with 413 if max_bytes is exceeded."""
    chunks = []
    total_size = 0
    chunk_size = 65536  # 64KB chunks

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Uploaded file exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )
        chunks.append(chunk)

    return b"".join(chunks)

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
    image_base64: Optional[str] = Form(None),
    current_user: Profile = Depends(get_current_user)
):
    """
    Authenticated, rate-limited, bounded OCR scan endpoint.
    Performs preprocessing, RapidOCR extraction, spatial sorting,
    and automatic QuestionParser identification.
    """
    rate_limiter.enforce(f"ocr_{current_user.id}", settings.RATE_LIMIT_OCR_PER_MINUTE, window_seconds=60, action_name="OCR scan")

    image_bytes = None
    if file:
        image_bytes = await read_bounded_bytes(file, MAX_BYTES)
    elif image_base64:
        clean_b64 = image_base64.strip()
        if "base64," in clean_b64:
            clean_b64 = clean_b64.split("base64,")[1].strip()
        # Pre-check base64 decoded size limit
        approx_size = (len(clean_b64) * 3) // 4
        if approx_size > MAX_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Base64 image payload exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )
        try:
            image_bytes = base64.b64decode(clean_b64)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid base64 encoding: {str(e)}")
        if len(image_bytes) > MAX_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either file upload or image_base64 form field is required.")

    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty image received.")

    # Validate image magic signature
    validate_image_magic_bytes(image_bytes)

    # 1. Run OCR safely
    try:
        ocr_result = ocr_engine.extract_from_bytes(image_bytes)
    except Exception as e:
        logger.error(f"RapidOCR extraction failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OCR processing error occurred.")

    if ocr_result.get("error"):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ocr_result["error"])

    raw_text = ocr_result.get("text", "")
    
    # 2. Parse MCQ structure
    parsed_mcq = parser.parse_from_text(raw_text, lines_metadata=ocr_result.get("lines"))

    # 3. Detect academic domain
    q_text = parsed_mcq.get("question") or raw_text
    detected_domain = detect_domain(q_text)

    return {
        "raw_text": raw_text,
        "ocr_confidence": ocr_result.get("confidence", 0.0),
        "lines": ocr_result.get("lines", []),
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
    max_pages: int = Form(15),
    current_user: Profile = Depends(get_current_user)
):
    """
    Authenticated, bounded PDF document scan endpoint.
    Extracts MCQ questions across pages up to safety limits.
    """
    rate_limiter.enforce(f"ocr_pdf_{current_user.id}", 10, window_seconds=60, action_name="PDF scan")

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be a PDF document.")
    
    pdf_bytes = await read_bounded_bytes(file, MAX_BYTES)
    validate_pdf_magic_bytes(pdf_bytes)

    # Bound maximum pages to 20 for server safety
    bounded_pages = max(1, min(max_pages, 20))

    try:
        res = ocr_engine.extract_from_pdf_bytes(pdf_bytes, max_pages=bounded_pages)
    except Exception as e:
        logger.error(f"PDF OCR extraction failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="PDF processing error occurred.")

    if res.get("error"):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=res["error"])

    extracted_questions = []
    for page in res.get("pages", []):
        parsed = parser.parse_from_text(page.get("text", ""))
        if parsed.get("question") and len(parsed.get("options", {})) >= 2:
            domain = detect_domain(parsed["question"])
            extracted_questions.append({
                "page_number": page.get("page_number", 1),
                "question": parsed["question"],
                "options": parsed["options"],
                "subject": domain,
                "confidence": page.get("confidence", 0.0)
            })

    return {
        "filename": file.filename,
        "total_pages": res.get("total_pages", 0),
        "processed_pages": res.get("processed_pages", 0),
        "questions_found": len(extracted_questions),
        "questions": extracted_questions,
        "pages": res.get("pages", [])
    }
