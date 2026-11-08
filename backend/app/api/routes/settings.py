import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.db.session import get_db
from backend.app.db.models import (
    Profile, UserSetting, Question, APIProvider, PracticeSession,
    Document, Conversation, UsageLog
)
from backend.app.core.deps import get_current_user

router = APIRouter(prefix="/settings", tags=["User Settings & Account Management"])

class UpdateSettingRequest(BaseModel):
    setting_key: str
    setting_value: str

class DeleteAccountRequest(BaseModel):
    confirm_email: str

@router.get("")
def get_user_settings(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings_records = db.query(UserSetting).filter(UserSetting.user_id == current_user.id).all()
    result = {s.setting_key: s.setting_value for s in settings_records}
    # Provide defaults
    if "theme" not in result:
        result["theme"] = "dark"
    if "auto_analyze" not in result:
        result["auto_analyze"] = "true"
    if "monthly_budget_usd" not in result:
        result["monthly_budget_usd"] = "25.0"
    return result

@router.put("")
def update_user_setting(
    req: UpdateSettingRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    setting = db.query(UserSetting).filter(
        UserSetting.user_id == current_user.id,
        UserSetting.setting_key == req.setting_key
    ).first()

    if setting:
        setting.setting_value = req.setting_value
    else:
        setting = UserSetting(
            user_id=current_user.id,
            setting_key=req.setting_key,
            setting_value=req.setting_value
        )
        db.add(setting)

    db.commit()
    return {"message": "Setting saved.", "key": req.setting_key, "value": req.setting_value}

@router.get("/export")
def export_user_data(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exports all user account data for portability and compliance."""
    questions = db.query(Question).filter(Question.user_id == current_user.id).all()
    sessions = db.query(PracticeSession).filter(PracticeSession.user_id == current_user.id).all()
    providers = db.query(APIProvider).filter(APIProvider.user_id == current_user.id).all()
    
    export_payload = {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "display_name": current_user.display_name,
            "created_at": str(current_user.created_at)
        },
        "questions": [
            {
                "id": q.id,
                "question": q.question_text,
                "options": json.loads(q.options_json) if q.options_json else {},
                "suggested_answer": q.suggested_answer,
                "explanation": q.explanation,
                "subject": q.subject_name,
                "created_at": str(q.created_at)
            }
            for q in questions
        ],
        "practice_sessions": [
            {
                "id": s.id,
                "title": s.title,
                "score_percentage": s.score_percentage,
                "total_questions": s.total_questions,
                "completed_at": str(s.completed_at)
            }
            for s in sessions
        ],
        "configured_providers": [
            {
                "provider": p.provider,
                "masked_key": p.masked_key,
                "default_model": p.default_model,
                "status": p.status
            }
            for p in providers
        ]
    }
    return export_payload

@router.delete("/account")
def delete_account(
    req: DeleteAccountRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if req.confirm_email.strip().lower() != current_user.email.strip().lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation email does not match authenticated user email."
        )

    # Cascade deletes all related data (questions, providers, sessions, documents, conversations, usage)
    db.delete(current_user)
    db.commit()
    return {"message": "User account and all associated data have been permanently deleted."}

