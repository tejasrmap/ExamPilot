"""
ExamPilot Database Models and Data Schemas
GT InnoX LLP
"""

from typing import Dict, Optional, Any
from pydantic import BaseModel, Field
import datetime

class QuestionModel(BaseModel):
    id: Optional[int] = None
    question_text: str
    options: Dict[str, str] = Field(default_factory=dict)
    suggested_answer: Optional[str] = None
    answer_text: Optional[str] = None
    explanation: Optional[str] = None
    option_analysis: Dict[str, str] = Field(default_factory=dict)
    confidence: float = 0.0
    needs_review: bool = False
    subject_id: Optional[int] = None
    subject_name: Optional[str] = "General"
    created_at: Optional[str] = Field(default_factory=lambda: datetime.datetime.now().isoformat())

class FeedbackModel(BaseModel):
    id: Optional[int] = None
    question_id: int
    user_feedback: str
    corrected_answer: Optional[str] = None
    created_at: Optional[str] = Field(default_factory=lambda: datetime.datetime.now().isoformat())

class PracticeSessionModel(BaseModel):
    id: Optional[int] = None
    session_name: str
    started_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    completed_at: Optional[str] = None
    total_questions: int = 0
    correct_count: int = 0

class SettingModel(BaseModel):
    id: Optional[int] = None
    setting_key: str
    setting_value: str

