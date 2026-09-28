from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class ResumeResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    summary: Optional[str] = None
    skills: List[str]
    projects: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]
    certifications: List[str]
    potential_questions: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ResumeQuestionGenerateRequest(BaseModel):
    resume_id: str
    target_role: Optional[str] = "Software Developer"
    difficulty: Optional[str] = "medium"
