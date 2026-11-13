import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel, Field
from backend.app.db.session import get_db
from backend.app.db.models import Profile, PracticeSession, PracticeAnswer, Question, Subject
from backend.app.core.deps import get_current_user

router = APIRouter(prefix="/practice", tags=["Practice Tests"])

class CreateTestRequest(BaseModel):
    title: str = "Practice Quiz"
    subject: Optional[str] = None
    question_count: int = Field(default=5, ge=1, le=50)
    time_limit_minutes: Optional[int] = Field(default=10, ge=1, le=180)

class SubmitAnswerItem(BaseModel):
    question_id: str
    selected_answer: str

class SubmitTestRequest(BaseModel):
    session_id: str
    answers: List[SubmitAnswerItem]

@router.get("", response_model=List[Dict[str, Any]])
def list_practice_sessions(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(PracticeSession).filter(
        PracticeSession.user_id == current_user.id
    ).order_by(desc(PracticeSession.started_at)).all()

    return [
        {
            "id": s.id,
            "title": s.title,
            "subject_name": s.subject_name or "General",
            "total_questions": s.total_questions,
            "correct_answers": s.correct_answers,
            "score_percentage": s.score_percentage,
            "started_at": s.started_at,
            "completed_at": s.completed_at
        }
        for s in sessions
    ]

@router.post("", response_model=Dict[str, Any])
def create_practice_test(
    req: CreateTestRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a practice test strictly using questions owned by the authenticated user.
    Never falls back to other users' private questions.
    If the user has zero saved questions, generates a safe self-contained sample question
    isolated exclusively to this user's account.
    """
    query = db.query(Question).filter(Question.user_id == current_user.id)
    if req.subject and req.subject.strip() not in ("All", ""):
        query = query.filter(Question.subject_name == req.subject.strip())

    questions = query.order_by(func.random()).limit(req.question_count).all()

    # If the user has no questions in this subject or account, seed a safe sample strictly for this user
    if not questions:
        seed_opts = {
            "A": "Branch Target Buffer predicts target branch addresses in the instruction fetch stage.",
            "B": "Branch Target Buffer only stores return stack addresses.",
            "C": "Branch Target Buffer is used for cache coherency.",
            "D": "Branch Target Buffer must wait for instruction decode before acting."
        }
        seed_q = Question(
            user_id=current_user.id,
            question_text="Sample Question: Please check all answers that apply to Branch Target Buffer (BTB).",
            options_json=json.dumps(seed_opts),
            suggested_answer="A",
            answer_text=seed_opts["A"],
            explanation="The BTB is indexed by the Program Counter (PC) during the fetch stage to predict the target address of branches without waiting for instruction decode.",
            confidence_level="high",
            confidence_reason="Standard computer architecture principle (Patterson & Hennessy).",
            subject_name="Computer Science"
        )
        db.add(seed_q)
        db.commit()
        db.refresh(seed_q)
        questions = [seed_q]

    # Capture authorized question IDs in session
    authorized_qids = [q.id for q in questions]

    session = PracticeSession(
        user_id=current_user.id,
        title=req.title,
        subject_name=req.subject or "Comprehensive Practice",
        total_questions=len(questions),
        time_limit_minutes=req.time_limit_minutes,
        question_ids_json=json.dumps(authorized_qids),
        started_at=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Return question items without revealing correct answers
    test_questions = []
    for q in questions:
        opts = json.loads(q.options_json) if q.options_json else {}
        test_questions.append({
            "id": q.id,
            "question_text": q.question_text,
            "options": opts,
            "subject": q.subject_name
        })

    return {
        "session_id": session.id,
        "title": session.title,
        "total_questions": len(test_questions),
        "time_limit_minutes": session.time_limit_minutes,
        "questions": test_questions
    }

@router.post("/submit", response_model=Dict[str, Any])
def submit_practice_test(
    req: SubmitTestRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits answers for a practice session with strict security validation:
    1. Verifies session belongs to authenticated user.
    2. Prevents repeated submissions.
    3. Verifies every submitted question belongs to the user and was in this session.
    4. Prevents duplicate answers for the same question.
    5. Calculates score against actual session question set.
    """
    session = db.query(PracticeSession).filter(
        PracticeSession.id == req.session_id,
        PracticeSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practice session not found.")

    if session.completed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Practice session has already been completed and submitted."
        )

    # Determine authorized questions for this session
    authorized_qids = set()
    if session.question_ids_json:
        try:
            authorized_qids = set(json.loads(session.question_ids_json))
        except Exception:
            authorized_qids = set()

    # Prevent duplicate answer submissions for the same question
    seen_qids = set()
    for item in req.answers:
        if item.question_id in seen_qids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate answer submitted for question ID: {item.question_id}"
            )
        seen_qids.add(item.question_id)

    correct_count = 0
    results = []

    for item in req.answers:
        # Verify question was included in this session
        if authorized_qids and item.question_id not in authorized_qids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question {item.question_id} was not part of this practice session."
            )

        # Verify question belongs to authenticated user (strict tenant isolation)
        q = db.query(Question).filter(
            Question.id == item.question_id,
            Question.user_id == current_user.id
        ).first()
        if not q:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Question {item.question_id} does not belong to your account."
            )

        clean_selected = item.selected_answer.strip().upper() if item.selected_answer else ""
        if len(clean_selected) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid option identifier: {clean_selected}"
            )

        is_correct = (clean_selected == (q.suggested_answer or "").strip().upper())
        if is_correct:
            correct_count += 1

        ans_entry = PracticeAnswer(
            session_id=session.id,
            question_id=q.id,
            selected_answer=clean_selected,
            is_correct=is_correct,
            explanation=q.explanation
        )
        db.add(ans_entry)

        opts = json.loads(q.options_json) if q.options_json else {}
        results.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "options": opts,
            "selected_answer": clean_selected,
            "correct_answer": q.suggested_answer,
            "is_correct": is_correct,
            "explanation": q.explanation
        })

    # Total questions is anchored to the session size, not submitted answer count
    total = session.total_questions or max(len(req.answers), 1)
    percentage = round((correct_count / max(total, 1)) * 100.0, 1)

    session.correct_answers = correct_count
    session.score_percentage = percentage
    session.completed_at = datetime.utcnow()
    db.commit()

    return {
        "session_id": session.id,
        "total_questions": total,
        "correct_answers": correct_count,
        "score_percentage": percentage,
        "completed_at": session.completed_at,
        "results": results
    }
