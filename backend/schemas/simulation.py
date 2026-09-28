from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class SimulationStartRequest(BaseModel):
    target_role: Optional[str] = "Software Developer"
    company_focus: Optional[str] = None  # e.g. "TCS", "Amazon", or generic

class SimulationRoundCompleteRequest(BaseModel):
    simulation_id: str
    round_type: str  # "aptitude", "gd", "technical", "hr"
    round_score: float
    round_data: Optional[Dict[str, Any]] = None

class SimulationFinalReportRequest(BaseModel):
    simulation_id: str

class SimulationReportResponse(BaseModel):
    id: str
    user_id: str
    status: str
    current_round: str
    target_role: str
    aptitude_score: float
    gd_score: float
    technical_score: float
    hr_score: float
    communication_score: float
    overall_score: float
    strengths: List[str]
    weak_areas: List[str]
    recommendations: List[str]
    summary_report: Optional[str] = None
    round_details: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
