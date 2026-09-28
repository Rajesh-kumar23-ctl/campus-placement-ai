from typing import Dict, Any, List
from backend.utils.helpers import (
    calculate_aptitude_score,
    calculate_interview_score,
    calculate_gd_score,
    calculate_readiness_score
)

class EvaluationService:
    """Consolidated evaluation and scoring engine."""

    @staticmethod
    def score_aptitude(correct: int, total: int) -> float:
        return calculate_aptitude_score(correct, total)

    @staticmethod
    def score_interview(tech: float, content: float, relevance: float, clarity: float, comm: float) -> float:
        return calculate_interview_score(tech, content, relevance, clarity, comm)

    @staticmethod
    def score_gd(content: float, relevance: float, clarity: float, structure: float, fluency: float) -> float:
        return calculate_gd_score(content, relevance, clarity, structure, fluency)

    @staticmethod
    def score_readiness(apt: float, gd: float, tech: float, hr: float, comm: float) -> float:
        return calculate_readiness_score(apt, gd, tech, hr, comm)

evaluation_service = EvaluationService()
