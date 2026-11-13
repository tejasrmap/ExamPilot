import os
import uuid
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.db.models import Profile, Document, DocumentChunk, Subject
from backend.app.core.deps import get_current_user
from backend.app.core.rate_limit import rate_limiter
from backend.app.services.ocr import ocr_engine
from backend.app.services.rag import chunk_document_text, search_relevant_chunks
from backend.app.services.storage import storage_service

logger = logging.getLogger("exampilot.documents")
router = APIRouter(prefix="/documents", tags=["Knowledge Library & Documents"])

MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

class SearchDocumentRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    subject_id: Optional[str] = None
    limit: int = 5

async def read_bounded_bytes(file: UploadFile, max_bytes: int) -> bytes:
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

def validate_pdf_signature(data: bytes) -> None:
    if len(data) < 5 or not data.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File signature validation failed. Uploaded document does not match a valid PDF."
        )

@router.get("", response_model=List[Dict[str, Any]])
def list_documents(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    docs = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(desc(Document.created_at)).all()

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_size_bytes": d.file_size_bytes,
            "subject_name": d.subject_name or "General",
            "page_count": d.page_count,
            "storage_provider": getattr(d, "storage_provider", "local"),
            "processing_status": d.processing_status,
            "created_at": d.created_at
        }
        for d in docs
    ]

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    subject_name: Optional[str] = Form("General"),
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Authenticated, bounded document upload handler.
    Streams input in bounded chunks, validates signatures, stores in durable storage abstraction,
    and indexes text chunks for RAG.
    """
    rate_limiter.enforce(f"doc_upload_{current_user.id}", 15, window_seconds=60, action_name="Document upload")

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must have a valid filename.")

    content_bytes = await read_bounded_bytes(file, MAX_BYTES)
    file_size = len(content_bytes)
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext == ".pdf":
        validate_pdf_signature(content_bytes)

    doc_id = str(uuid.uuid4())

    # 1. Store via durable storage abstraction
    saved_meta = storage_service.save_file(
        user_id=current_user.id,
        document_id=doc_id,
        filename=file.filename,
        content_bytes=content_bytes,
        content_type="application/pdf" if file_ext == ".pdf" else "text/plain"
    )

    try:
        extracted_text = ""
        pages = 1

        if file_ext == ".pdf":
            res = ocr_engine.extract_from_pdf_bytes(content_bytes, max_pages=20)
            extracted_text = res.get("full_text", "")
            pages = res.get("total_pages", 1)
        else:
            try:
                extracted_text = content_bytes.decode("utf-8", errors="ignore")
            except Exception:
                extracted_text = "Binary or unparseable text format."

        doc = Document(
            id=doc_id,
            user_id=current_user.id,
            filename=file.filename,
            storage_provider=saved_meta["storage_provider"],
            storage_key=saved_meta["storage_key"],
            storage_path=saved_meta["storage_path"],
            file_size_bytes=file_size,
            subject_name=subject_name,
            page_count=pages,
            processing_status="ready"
        )
        db.add(doc)

        # Create semantic chunks for RAG
        chunks = chunk_document_text(extracted_text, chunk_size=500, overlap=80)
        for idx, c in enumerate(chunks):
            chunk_entry = DocumentChunk(
                document_id=doc.id,
                chunk_index=idx,
                content=c
            )
            db.add(chunk_entry)

        db.commit()
    except Exception as exc:
        # Partial upload cleanup to prevent orphaned files
        logger.error(f"Document processing failed. Cleaning up stored asset: {str(exc)}")
        storage_service.delete_file(
            saved_meta["storage_provider"],
            saved_meta["storage_key"],
            saved_meta["storage_path"]
        )
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process and index uploaded document."
        )

    return {
        "id": doc.id,
        "filename": doc.filename,
        "page_count": pages,
        "chunks_indexed": len(chunks),
        "storage_provider": doc.storage_provider,
        "status": "ready"
    }

@router.post("/search")
def search_library(
    req: SearchDocumentRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = search_relevant_chunks(
        db=db,
        user_id=current_user.id,
        query=req.query,
        subject_id=req.subject_id,
        limit=req.limit
    )
    return {
        "query": req.query,
        "results_count": len(results),
        "chunks": results
    }

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Clean up stored object
    storage_service.delete_file(
        getattr(doc, "storage_provider", "local"),
        getattr(doc, "storage_key", None),
        getattr(doc, "storage_path", None)
    )

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully."}
