from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any

from backend.database.database import get_db
from backend.models.user import User
from backend.models.aptitude import AptitudeAttempt
from backend.models.gd import GDSession
from backend.models.interview import InterviewSession
from backend.models.simulation import PlacementSimulation
from backend.dependencies import get_current_user
from backend.services.recommendation_service import recommendation_service
from backend.schemas.progress import ProgressAnalyticsResponse

router = APIRouter(prefix="/api/progress", tags=["Progress & Analytics"])

@router.get("", response_model=ProgressAnalyticsResponse)
async def get_progress_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve comprehensive analytics and Chart.js datasets for the user."""
    rec_data = await recommendation_service.get_user_recommendations(db, current_user)
    cat_scores = rec_data["category_scores"]

    # History queries
    apt_attempts = db.query(AptitudeAttempt).filter(
        AptitudeAttempt.user_id == current_user.id
    ).order_by(AptitudeAttempt.created_at.asc()).all()

    gd_sessions = db.query(GDSession).filter(
        GDSession.user_id == current_user.id
    ).order_by(GDSession.created_at.asc()).all()

    interviews = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == "completed"
    ).order_by(InterviewSession.created_at.asc()).all()

    simulations = db.query(PlacementSimulation).filter(
        PlacementSimulation.user_id == current_user.id,
        PlacementSimulation.status == "completed"
    ).order_by(PlacementSimulation.created_at.asc()).all()

    # Averages
    avg_apt = round(sum(a.score for a in apt_attempts) / len(apt_attempts), 1) if apt_attempts else cat_scores["aptitude"]
    avg_gd = round(sum(s.score for s in gd_sessions) / len(gd_sessions), 1) if gd_sessions else cat_scores["gd"]
    avg_int = round(sum(i.score for i in interviews) / len(interviews), 1) if interviews else cat_scores["technical"]

    # Skill Radar
    skill_radar = {
        "Aptitude": cat_scores["aptitude"],
        "GD & Discussion": cat_scores["gd"],
        "Technical Skills": cat_scores["technical"],
        "HR & Culture": cat_scores["hr"],
        "Communication": cat_scores["communication"]
    }

    # Best & Weakest Skill
    sorted_skills = sorted(skill_radar.items(), key=lambda x: x[1])
    weakest_skill = sorted_skills[0][0]
    best_skill = sorted_skills[-1][0]

    # Performance Over Time
    time_series = []
    # If user has real attempts, combine them chronologically
    combined_timeline = []
    for a in apt_attempts:
        combined_timeline.append({"date": a.created_at, "score": a.score, "type": "Aptitude"})
    for g in gd_sessions:
        combined_timeline.append({"date": g.created_at, "score": g.score, "type": "GD"})
    for i in interviews:
        combined_timeline.append({"date": i.created_at, "score": i.score, "type": "Interview"})
    for s in simulations:
        combined_timeline.append({"date": s.created_at, "score": s.overall_score, "type": "Simulation"})

    combined_timeline.sort(key=lambda x: x["date"])

    if combined_timeline:
        for item in combined_timeline:
            time_series.append({
                "label": item["date"].strftime("%b %d"),
                "score": item["score"],
                "type": item["type"]
            })
    else:
        # Default starter baseline progression for chart rendering
        time_series = [
            {"label": "Day 1", "score": 60.0, "type": "Baseline"},
            {"label": "Day 3", "score": 68.0, "type": "Aptitude"},
            {"label": "Day 5", "score": 72.0, "type": "Interview"},
            {"label": "Day 7", "score": rec_data["readiness_percentage"], "type": "Current"}
        ]

    # Practice Activity (last 7 days distribution)
    today = datetime.utcnow().date()
    days_map = {}
    for i in range(7):
        d = today - timedelta(days=(6 - i))
        days_map[d.strftime("%a")] = 0

    for item in combined_timeline:
        d_str = item["date"].date().strftime("%a")
        if d_str in days_map:
            days_map[d_str] += 1

    practice_activity = [{"day": day, "count": count} for day, count in days_map.items()]

    return ProgressAnalyticsResponse(
        total_tests=len(apt_attempts),
        total_interviews=len(interviews),
        total_gd_sessions=len(gd_sessions),
        total_simulations=len(simulations),
        average_aptitude=avg_apt,
        average_gd=avg_gd,
        average_interview=avg_int,
        best_skill=best_skill,
        weakest_skill=weakest_skill,
        readiness_score=rec_data["readiness_percentage"],
        skill_radar=skill_radar,
        performance_over_time=time_series,
        practice_activity=practice_activity,
        weak_areas=rec_data["weak_areas"],
        recommendations=rec_data["recommendations"]
    )

@router.get("/aptitude")
def get_aptitude_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempts = db.query(AptitudeAttempt).filter(
        AptitudeAttempt.user_id == current_user.id
    ).order_by(AptitudeAttempt.created_at.asc()).all()
    return attempts

@router.get("/gd")
def get_gd_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(GDSession).filter(
        GDSession.user_id == current_user.id
    ).order_by(GDSession.created_at.asc()).all()
    return sessions

@router.get("/interview")
def get_interview_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == "completed"
    ).order_by(InterviewSession.created_at.asc()).all()
    return sessions
