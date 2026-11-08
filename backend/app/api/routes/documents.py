import os
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from backend.app.db.session import get_db
from backend.app.db.models import Profile, Document, DocumentChunk, Subject
from backend.app.core.deps import get_current_user
from backend.app.services.ocr import ocr_engine
from backend.app.services.rag import chunk_document_text, search_relevant_chunks

router = APIRouter(prefix="/documents", tags=["Knowledge Library & Documents"])

UPLOAD_STORAGE_DIR = "backend/storage/documents"
os.makedirs(UPLOAD_STORAGE_DIR, exist_ok=True)

class SearchDocumentRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    subject_id: Optional[str] = None
    limit: int = 5

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
    content_bytes = await file.read()
    file_size = len(content_bytes)
    file_ext = os.path.splitext(file.filename)[1].lower()

    doc_id = str(uuid.uuid4())
    save_filename = f"{doc_id}_{file.filename}"
    save_path = os.path.join(UPLOAD_STORAGE_DIR, save_filename)

    with open(save_path, "wb") as f:
        f.write(content_bytes)

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
        storage_path=save_path,
        file_size_bytes=file_size,
        subject_name=subject_name,
        page_count=pages,
        processing_status="ready"
    )
    db.add(doc)
    db.commit()

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

    return {
        "id": doc.id,
        "filename": doc.filename,
        "page_count": pages,
        "chunks_indexed": len(chunks),
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
        raise HTTPException(status_code=404, detail="Document not found")

    if os.path.exists(doc.storage_path):
        try:
            os.remove(doc.storage_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully."}

