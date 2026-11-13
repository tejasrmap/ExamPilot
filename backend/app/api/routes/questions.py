import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from backend.app.db.session import get_db
from backend.app.db.models import Profile, Question, APIProvider, UsageLog, Subject
from backend.app.core.deps import get_current_user
from backend.app.core.security import decrypt_api_key
from backend.app.providers.registry import provider_registry
from backend.app.providers.base import QuestionAnalysisResult, OptionIdentity
from backend.app.services.domain_detector import detect_domain, detect_domain_with_details

router = APIRouter(prefix="/questions", tags=["Question Analysis & History"])

class AnalyseQuestionRequest(BaseModel):
    question_text: str
    options: Dict[str, str]
    structured_options: Optional[List[Dict[str, Any]]] = None
    subject: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    context_material: Optional[str] = None
    source_type: str = "scanner" # scanner, pdf, extension, manual

class FeedbackRequest(BaseModel):
    feedback: str # "correct", "incorrect", "reported"

class QuestionItemResponse(BaseModel):
    id: str
    question_text: str
    options: Dict[str, str]
    suggested_answer: Optional[str] = None
    answer_text: Optional[str] = None
    explanation: Optional[str] = None
    option_analysis: Optional[Dict[str, str]] = None
    confidence_level: Optional[str] = None
    confidence_reason: Optional[str] = None
    subject: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    user_feedback: Optional[str] = None
    created_at: datetime

@router.post("/analyse", response_model=QuestionAnalysisResult)
async def analyse_question(
    req: AnalyseQuestionRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.question_text.strip():
        raise HTTPException(status_code=400, detail="Question text cannot be empty.")
    if len(req.options) < 2:
        raise HTTPException(status_code=400, detail="At least two answer options are required for MCQ analysis.")

    # 1. Determine Subject / Domain with Curriculum Details
    domain_details = detect_domain_with_details(req.question_text, req.options)
    detected_subject = req.subject or domain_details["subject"]

    # 2. Select Provider and Model
    target_provider_name = req.provider.lower().strip() if req.provider else None
    
    if target_provider_name:
        saved_provider = db.query(APIProvider).filter(
            APIProvider.user_id == current_user.id,
            APIProvider.provider == target_provider_name
        ).first()
    else:
        # Get default provider or first available
        saved_provider = db.query(APIProvider).filter(
            APIProvider.user_id == current_user.id,
            APIProvider.is_default == True
        ).first()
        if not saved_provider:
            saved_provider = db.query(APIProvider).filter(
                APIProvider.user_id == current_user.id
            ).first()

    if not saved_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No AI Provider configured. Please add an API key under API Providers first."
        )

    target_provider = saved_provider.provider
    target_model = req.model or saved_provider.default_model

    # 3. Decrypt API Key
    try:
        api_key = decrypt_api_key(saved_provider.encrypted_api_key)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decrypt credentials for {target_provider}: {str(e)}"
        )

    # 4. Invoke Provider
    provider_adapter = provider_registry.get_provider(target_provider)
    if not target_model:
        models = await provider_adapter.list_models()
        target_model = models[0].id if models else "gpt-4o-mini"

    try:
        result: QuestionAnalysisResult = await provider_adapter.generate_analysis(
            api_key=api_key,
            model=target_model,
            question_text=req.question_text,
            options=req.options,
            subject=detected_subject,
            context_material=req.context_material,
            structured_options=req.structured_options
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI Provider error ({target_provider}): {str(e)}"
        )

    # Enrich result with stable option identity and curriculum evidence
    result.subject = detected_subject
    result.subject_confidence = domain_details.get("subject_confidence", 0.80)
    result.curriculum_confidence = domain_details.get("curriculum_confidence", 0.0)
    if not result.evidence:
        result.evidence = domain_details.get("evidence")

    if req.structured_options:
        structured_list = [
            OptionIdentity(**o) if isinstance(o, dict) else o for o in req.structured_options
        ]
        result.structured_options = structured_list
        matching_opt = None
        for o in structured_list:
            if o.internal_label.upper() == result.suggested_answer.upper():
                matching_opt = o
                break
            if o.original_label and o.original_label.upper() == result.suggested_answer.upper():
                matching_opt = o
                break
            if o.text.strip().lower() == result.answer_text.strip().lower():
                matching_opt = o
                break

        if matching_opt:
            result.original_label = matching_opt.original_label
            result.source_position = matching_opt.source_order
            if not result.answer_text or result.answer_text not in [so.text for so in structured_list]:
                result.answer_text = matching_opt.text
            result.suggested_answer = matching_opt.internal_label
    else:
        result.source_position = (ord(result.suggested_answer.upper()) - ord('A') + 1) if len(result.suggested_answer) == 1 and result.suggested_answer.isalpha() else None
        legacy_structured = []
        for idx, (lbl, txt) in enumerate(sorted(req.options.items())):
            legacy_structured.append(OptionIdentity(
                id=f"opt_{idx+1}",
                text=txt,
                original_label=lbl,
                internal_label=lbl,
                source_order=idx + 1,
                confidence=1.0,
                is_user_edited=False
            ))
        result.structured_options = legacy_structured
        result.original_label = result.suggested_answer

    # 5. Persist Question to History
    # Find or create subject record
    subject_record = db.query(Subject).filter(
        Subject.user_id == current_user.id,
        Subject.name == detected_subject
    ).first()
    if not subject_record:
        subject_record = Subject(user_id=current_user.id, name=detected_subject)
        db.add(subject_record)
        db.commit()
        db.refresh(subject_record)

    question_record = Question(
        user_id=current_user.id,
        question_text=req.question_text,
        options_json=json.dumps(req.options),
        suggested_answer=result.suggested_answer,
        answer_text=result.answer_text,
        explanation=result.explanation,
        option_analysis_json=json.dumps(result.option_analysis),
        confidence_level=result.confidence.level,
        confidence_reason=result.confidence.reason,
        subject_id=subject_record.id,
        subject_name=detected_subject,
        provider=target_provider,
        model=target_model,
        source_type=req.source_type
    )
    db.add(question_record)

    # 6. Record Usage Log
    usage_entry = UsageLog(
        user_id=current_user.id,
        provider=target_provider,
        model=target_model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        estimated_cost=result.estimated_cost,
        feature="question_analysis"
    )
    db.add(usage_entry)
    db.commit()

    return result

@router.get("", response_model=List[QuestionItemResponse])
def get_questions_history(
    search: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Question).filter(Question.user_id == current_user.id)
    if search:
        query = query.filter(Question.question_text.ilike(f"%{search.strip()}%"))
    if subject and subject != "All":
        query = query.filter(Question.subject_name == subject)

    records = query.order_by(desc(Question.created_at)).offset(offset).limit(limit).all()

    results = []
    for r in records:
        try:
            opts = json.loads(r.options_json) if r.options_json else {}
        except Exception:
            opts = {}
        try:
            op_ana = json.loads(r.option_analysis_json) if r.option_analysis_json else {}
        except Exception:
            op_ana = {}

        results.append(QuestionItemResponse(
            id=r.id,
            question_text=r.question_text,
            options=opts,
            suggested_answer=r.suggested_answer,
            answer_text=r.answer_text,
            explanation=r.explanation,
            option_analysis=op_ana,
            confidence_level=r.confidence_level,
            confidence_reason=r.confidence_reason,
            subject=r.subject_name or "General",
            provider=r.provider,
            model=r.model,
            user_feedback=r.user_feedback,
            created_at=r.created_at
        ))
    return results

@router.get("/{question_id}", response_model=QuestionItemResponse)
def get_question(
    question_id: str,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Question).filter(
        Question.id == question_id,
        Question.user_id == current_user.id
    ).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return QuestionItemResponse(
        id=q.id,
        question_text=q.question_text,
        options=json.loads(q.options_json) if q.options_json else {},
        suggested_answer=q.suggested_answer,
        answer_text=q.answer_text,
        explanation=q.explanation,
        option_analysis=json.loads(q.option_analysis_json) if q.option_analysis_json else {},
        confidence_level=q.confidence_level,
        confidence_reason=q.confidence_reason,
        subject=q.subject_name,
        provider=q.provider,
        model=q.model,
        user_feedback=q.user_feedback,
        created_at=q.created_at
    )

@router.post("/{question_id}/feedback")
def submit_feedback(
    question_id: str,
    req: FeedbackRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Question).filter(
        Question.id == question_id,
        Question.user_id == current_user.id
    ).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    
    q.user_feedback = req.feedback.lower().strip()
    db.commit()
    return {"message": "Feedback recorded successfully.", "status": q.user_feedback}

@router.delete("/{question_id}")
def delete_question(
    question_id: str,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Question).filter(
        Question.id == question_id,
        Question.user_id == current_user.id
    ).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(q)
    db.commit()
    return {"message": "Question deleted from history."}

