from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class InterviewStartRequest(BaseModel):
    interview_type: str = Field(..., description="technical, hr, managerial, cloud_engineer, software_developer, mock_interview")
    target_role: Optional[str] = "Software Developer"
    difficulty: Optional[str] = "medium"
    experience_level: Optional[str] = "entry"
    use_resume: Optional[bool] = False
    resume_id: Optional[str] = None
    total_questions: Optional[int] = Field(default=5, ge=3, le=10)

class InterviewAnswerSubmit(BaseModel):
    session_id: str
    question_id: str
    answer: str
    time_taken_seconds: Optional[int] = 0

class InterviewAnswerResponse(BaseModel):
    answer_id: str
    question_id: str
    overall_score: float
    technical_accuracy: float
    content: float
    relevance: float
    clarity: float
    communication: float
    feedback: str
    strengths: List[str]
    improvements: List[str]
    is_last_question: bool
    next_question: Optional[Dict[str, Any]] = None

class InterviewFollowupRequest(BaseModel):
    session_id: str
    question_id: str

class InterviewEndRequest(BaseModel):
    session_id: str

class InterviewSessionResponse(BaseModel):
    id: str
    interview_type: str
    target_role: str
    difficulty: str
    status: str
    score: float
    technical_accuracy: Optional[float] = 0.0
    content: Optional[float] = 0.0
    relevance: Optional[float] = 0.0
    clarity: Optional[float] = 0.0
    communication: Optional[float] = 0.0
    strengths: List[str]
    improvements: List[str]
    topics_to_revise: List[str]
    feedback: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    questions: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True)
