from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class SkillScore(BaseModel):
    skill: str
    score: float
    updated_at: datetime

class RecentActivityItem(BaseModel):
    id: str
    type: str  # "aptitude", "gd", "interview", "simulation"
    title: str
    score: float
    date: datetime

class PersonalizedRecommendation(BaseModel):
    category: str
    insight: str
    action_items: List[str]
    priority: str  # "high", "medium", "low"

class DashboardResponse(BaseModel):
    user_name: str
    target_role: str
    readiness_percentage: float
    category_scores: Dict[str, float]  # aptitude, gd, technical, hr, communication
    streak_days: int
    total_sessions: int
    recent_activities: List[RecentActivityItem]
    weak_areas: List[str]
    recommendations: List[PersonalizedRecommendation]
    latest_aptitude: Optional[Dict[str, Any]] = None
    latest_gd: Optional[Dict[str, Any]] = None
    latest_interview: Optional[Dict[str, Any]] = None

class ProgressAnalyticsResponse(BaseModel):
    total_tests: int
    total_interviews: int
    total_gd_sessions: int
    total_simulations: int
    average_aptitude: float
    average_gd: float
    average_interview: float
    best_skill: str
    weakest_skill: str
    readiness_score: float
    skill_radar: Dict[str, float]
    performance_over_time: List[Dict[str, Any]]
    practice_activity: List[Dict[str, Any]]
    weak_areas: List[str]
    recommendations: List[PersonalizedRecommendation]
