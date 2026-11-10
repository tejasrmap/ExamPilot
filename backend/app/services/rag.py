import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.db.models import Document, DocumentChunk

def chunk_document_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    """Splits document text into overlapping semantic passages."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_len = 0

    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean:
            continue
        words = p_clean.split()
        if current_len + len(words) > chunk_size:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            # Keep overlap
            overlap_words = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = list(overlap_words) + words
            current_len = len(current_chunk)
        else:
            current_chunk.extend(words)
            current_len += len(words)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks if chunks else [text[:1500]]

def search_relevant_chunks(
    db: Session,
    user_id: str,
    query: str,
    subject_id: Optional[str] = None,
    limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Search document chunks for the authenticated user using text keyword relevance and BM25-style scoring.
    """
    # Clean query terms
    tokens = set(re.findall(r"\w{3,}", query.lower()))
    if not tokens:
        return []

    q = db.query(DocumentChunk).join(Document).filter(Document.user_id == user_id)
    if subject_id:
        q = q.filter(Document.subject_id == subject_id)

    chunks = q.all()
    scored = []
    for c in chunks:
        content_lower = c.content.lower()
        score = sum(1 for t in tokens if t in content_lower)
        if score > 0:
            scored.append({
                "chunk_id": c.id,
                "document_id": c.document_id,
                "content": c.content,
                "score": score
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]

