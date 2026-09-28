from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class AptitudeQuestionItem(BaseModel):
    id: str
    category: str
    category_display: str
    difficulty: str
    question: str
    options: List[str]
    # Note: correct_answer is excluded during test-taking for integrity
    time_limit_seconds: Optional[int] = 60

class AptitudeStartRequest(BaseModel):
    category: Optional[str] = "all"  # quantitative, logical, verbal, data_interpretation, or all
    difficulty: Optional[str] = "all"  # easy, medium, hard, or all
    num_questions: int = Field(default=10, ge=5, le=30)
    timer_minutes: Optional[int] = 15

class QuestionAnswerSubmit(BaseModel):
    question_id: str
    selected_answer: Optional[str] = None
    time_taken: Optional[int] = 0

class AptitudeSubmitRequest(BaseModel):
    category: Optional[str] = "all"
    difficulty: Optional[str] = "all"
    time_taken: int  # in seconds
    answers: List[QuestionAnswerSubmit]

class AptitudeReviewItem(BaseModel):
    question_id: str
    question: str
    category: str
    options: List[str]
    selected_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    explanation: str
    shortcut: Optional[str] = None

class AptitudeAttemptResponse(BaseModel):
    id: str
    user_id: str
    category: Optional[str]
    difficulty: Optional[str]
    score: float
    accuracy: float
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    time_taken: int
    created_at: datetime
    category_breakdown: Optional[Dict[str, Any]] = None
    review: Optional[List[AptitudeReviewItem]] = None

    model_config = ConfigDict(from_attributes=True)
