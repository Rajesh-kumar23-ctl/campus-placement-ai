import json
import re
from typing import Dict, Any, Optional
from backend.config import settings

def calculate_aptitude_score(correct: int, total: int) -> float:
    """Calculate objective aptitude score percentage."""
    if total <= 0:
        return 0.0
    return round((correct / total) * 100.0, 1)

def calculate_interview_score(
    technical: float,
    content: float,
    relevance: float,
    clarity: float,
    communication: float
) -> float:
    """
    Calculate weighted interview score based on:
    Technical 30%, Content 20%, Relevance 20%, Clarity 15%, Communication 15%
    Each input can be 0-10 or 0-100. Normalizes to 0-100 scale.
    """
    # Normalize if values are on 0-10 scale
    def norm(v):
        return v * 10.0 if v <= 10.0 else v

    weights = settings.INTERVIEW_WEIGHTS
    score = (
        norm(technical) * weights["technical"] +
        norm(content) * weights["content"] +
        norm(relevance) * weights["relevance"] +
        norm(clarity) * weights["clarity"] +
        norm(communication) * weights["communication"]
    )
    return round(score, 1)

def calculate_gd_score(
    content: float,
    relevance: float,
    clarity: float,
    structure: float,
    fluency: float
) -> float:
    """
    Calculate weighted GD score based on:
    Content 25%, Relevance 20%, Clarity 20%, Structure 15%, Fluency 20%
    Normalizes to 0-100 scale.
    """
    def norm(v):
        return v * 10.0 if v <= 10.0 else v

    weights = settings.GD_WEIGHTS
    score = (
        norm(content) * weights["content"] +
        norm(relevance) * weights["relevance"] +
        norm(clarity) * weights["clarity"] +
        norm(structure) * weights["structure"] +
        norm(fluency) * weights["fluency"]
    )
    return round(score, 1)

def calculate_readiness_score(
    aptitude: float = 0.0,
    gd: float = 0.0,
    technical: float = 0.0,
    hr: float = 0.0,
    communication: float = 0.0
) -> float:
    """
    Calculate overall Preparation Readiness metric:
    Aptitude 25%, GD 20%, Technical 30%, HR 15%, Communication 10%
    """
    weights = settings.READINESS_WEIGHTS
    score = (
        aptitude * weights["aptitude"] +
        gd * weights["gd"] +
        technical * weights["technical"] +
        hr * weights["hr"] +
        communication * weights["communication"]
    )
    return round(score, 1)

def parse_ai_json(text: str) -> Optional[Dict[str, Any]]:
    """Cleanly parse JSON from LLM response, stripping markdown code fences if present."""
    if not text:
        return None

    cleaned = text.strip()

    # Match ```json ... ``` or ``` ... ```
    json_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if json_block:
        cleaned = json_block.group(1).strip()

    try:
        return json.loads(cleaned)
    except Exception:
        # Try finding the first '{' and last '}'
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start:end+1])
            except Exception:
                pass
        return None
