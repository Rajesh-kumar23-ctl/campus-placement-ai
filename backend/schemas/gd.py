from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class GDTopicPrep(BaseModel):
    id: Optional[str] = None
    topic: str
    category: str
    difficulty: str
    overview: str
    opening_statement: str
    key_arguments_for: List[str]
    key_arguments_against: List[str]
    real_world_examples: List[str]
    thirty_sec_speech: str
    one_min_speech: str
    conclusion: str
    things_to_avoid: List[str]
    follow_up_questions: List[str]

class GDGenerateRequest(BaseModel):
    topic: str
    category: Optional[str] = "General"
    difficulty: Optional[str] = "Medium"

class GDStartRequest(BaseModel):
    topic: str
    difficulty: Optional[str] = "Medium"
    duration_minutes: int = Field(default=5, ge=3, le=15)
    num_participants: int = Field(default=3, ge=2, le=5)

class GDRespondRequest(BaseModel):
    session_id: str
    user_response: str
    turn: Optional[int] = 1

class GDEvaluateRequest(BaseModel):
    session_id: str

class GDEvaluationResponse(BaseModel):
    session_id: str
    topic: str
    overall: float
    content: float
    relevance: float
    clarity: float
    structure: float
    fluency: float
    strengths: List[str]
    improvements: List[str]
    better_response: str
    feedback: str
