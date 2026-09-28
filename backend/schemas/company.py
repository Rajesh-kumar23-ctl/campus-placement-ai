from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

class CompanyResponse(BaseModel):
    id: str
    name: str
    tier: str
    description: str
    hiring_pattern: Dict[str, Any]
    preparation_areas: List[str]
    technical_topics: List[str]
    hr_topics: List[str]
    sample_questions: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
