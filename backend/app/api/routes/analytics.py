from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.app.db.session import get_db
from backend.app.db.models import Profile, Question, PracticeSession, PracticeAnswer, UsageLog, Subject
from backend.app.core.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics & Usage Dashboard"])

@router.get("/overview")
def get_analytics_overview(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Real SQL aggregations for authenticated user
    total_questions = db.query(Question).filter(Question.user_id == current_user.id).count()
    total_practice = db.query(PracticeSession).filter(PracticeSession.user_id == current_user.id).count()

    # Practice accuracy
    completed_sessions = db.query(PracticeSession).filter(
        PracticeSession.user_id == current_user.id,
        PracticeSession.completed_at.isnot(None)
    ).all()

    avg_accuracy = 0.0
    if completed_sessions:
        avg_accuracy = round(sum(s.score_percentage for s in completed_sessions) / len(completed_sessions), 1)

    # Token & cost usage
    usage_records = db.query(UsageLog).filter(UsageLog.user_id == current_user.id).all()
    total_tokens = sum(u.input_tokens + u.output_tokens for u in usage_records)
    total_estimated_cost = round(sum(u.estimated_cost for u in usage_records), 4)

    # Activity by last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_questions = db.query(
        func.date(Question.created_at).label("day"),
        func.count(Question.id).label("count")
    ).filter(
        Question.user_id == current_user.id,
        Question.created_at >= seven_days_ago
    ).group_by(func.date(Question.created_at)).all()

    activity_by_day = [{"day": str(r.day), "scans": r.count} for r in recent_questions]

    return {
        "total_questions_scanned": total_questions,
        "practice_sessions_completed": total_practice,
        "average_accuracy_percentage": avg_accuracy,
        "total_tokens_used": total_tokens,
        "estimated_api_cost_usd": total_estimated_cost,
        "activity_last_7_days": activity_by_day
    }

@router.get("/subjects")
def get_subject_performance(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Questions per subject
    subject_counts = db.query(
        Question.subject_name,
        func.count(Question.id)
    ).filter(
        Question.user_id == current_user.id
    ).group_by(Question.subject_name).all()

    # Practice accuracy per subject
    practice_by_subject = db.query(
        PracticeSession.subject_name,
        func.avg(PracticeSession.score_percentage)
    ).filter(
        PracticeSession.user_id == current_user.id,
        PracticeSession.completed_at.isnot(None)
    ).group_by(PracticeSession.subject_name).all()

    practice_map = {r[0]: round(r[1], 1) for r in practice_by_subject if r[0]}

    breakdown = []
    for subj, count in subject_counts:
        s_name = subj or "General"
        breakdown.append({
            "subject": s_name,
            "question_count": count,
            "practice_accuracy": practice_map.get(s_name, 0.0)
        })

    return {
        "subjects": breakdown
    }

@router.get("/usage")
def get_detailed_usage(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Group by provider
    prov_usage = db.query(
        UsageLog.provider,
        func.count(UsageLog.id).label("requests"),
        func.sum(UsageLog.input_tokens).label("in_tokens"),
        func.sum(UsageLog.output_tokens).label("out_tokens"),
        func.sum(UsageLog.estimated_cost).label("cost")
    ).filter(
        UsageLog.user_id == current_user.id
    ).group_by(UsageLog.provider).all()

    provider_breakdown = [
        {
            "provider": r.provider,
            "requests": r.requests,
            "input_tokens": r.in_tokens or 0,
            "output_tokens": r.out_tokens or 0,
            "estimated_cost": round(r.cost or 0.0, 4)
        }
        for r in prov_usage
    ]

    # Recent 25 logs
    recent_logs = db.query(UsageLog).filter(
        UsageLog.user_id == current_user.id
    ).order_by(desc(UsageLog.created_at)).limit(25).all()

    return {
        "providers": provider_breakdown,
        "recent_logs": [
            {
                "id": l.id,
                "provider": l.provider,
                "model": l.model,
                "feature": l.feature,
                "input_tokens": l.input_tokens,
                "output_tokens": l.output_tokens,
                "estimated_cost": l.estimated_cost,
                "created_at": l.created_at
            }
            for l in recent_logs
        ]
    }

