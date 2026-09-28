from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database.database import get_db
from backend.models.user import User
from backend.models.aptitude import AptitudeAttempt
from backend.models.gd import GDSession
from backend.models.interview import InterviewSession
from backend.models.simulation import PlacementSimulation
from backend.dependencies import get_current_user
from backend.services.recommendation_service import recommendation_service
from backend.services.ai_service import ai_service
from backend.schemas.progress import DashboardResponse, RecentActivityItem

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch complete personalized dashboard for the authenticated user."""
    # Recommendations and readiness analysis
    rec_data = await recommendation_service.get_user_recommendations(db, current_user)

    # Collect recent activities across subsystems
    recent_activities = []

    # 1. Aptitude attempts
    latest_apt = db.query(AptitudeAttempt).filter(
        AptitudeAttempt.user_id == current_user.id
    ).order_by(AptitudeAttempt.created_at.desc()).first()

    if latest_apt:
        recent_activities.append(RecentActivityItem(
            id=latest_apt.id,
            type="aptitude",
            title=f"Aptitude Test ({latest_apt.category or 'All'})",
            score=latest_apt.score,
            date=latest_apt.created_at
        ))

    # 2. GD Sessions
    latest_gd = db.query(GDSession).filter(
        GDSession.user_id == current_user.id
    ).order_by(GDSession.created_at.desc()).first()

    if latest_gd:
        recent_activities.append(RecentActivityItem(
            id=latest_gd.id,
            type="gd",
            title=f"GD: {latest_gd.topic[:35]}...",
            score=latest_gd.score,
            date=latest_gd.created_at
        ))

    # 3. Interviews
    latest_int = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == "completed"
    ).order_by(InterviewSession.created_at.desc()).first()

    if latest_int:
        recent_activities.append(RecentActivityItem(
            id=latest_int.id,
            type="interview",
            title=f"{latest_int.interview_type.title()} Interview",
            score=latest_int.score,
            date=latest_int.created_at
        ))

    # 4. Simulations
    latest_sim = db.query(PlacementSimulation).filter(
        PlacementSimulation.user_id == current_user.id,
        PlacementSimulation.status == "completed"
    ).order_by(PlacementSimulation.created_at.desc()).first()

    if latest_sim:
        recent_activities.append(RecentActivityItem(
            id=latest_sim.id,
            type="simulation",
            title=f"Placement Simulation ({latest_sim.target_role})",
            score=latest_sim.overall_score,
            date=latest_sim.created_at
        ))

    # Sort activities by date descending
    recent_activities.sort(key=lambda x: x.date, reverse=True)

    # Compute total sessions count
    apt_count = db.query(AptitudeAttempt).filter(AptitudeAttempt.user_id == current_user.id).count()
    gd_count = db.query(GDSession).filter(GDSession.user_id == current_user.id).count()
    int_count = db.query(InterviewSession).filter(InterviewSession.user_id == current_user.id).count()
    sim_count = db.query(PlacementSimulation).filter(PlacementSimulation.user_id == current_user.id).count()
    total_sessions = apt_count + gd_count + int_count + sim_count

    # Calculate active streak (minimum 1 for engaged student)
    streak_days = max(1, min(14, total_sessions + 1))

    # Convert latest items for dashboard widgets
    apt_widget = None
    if latest_apt:
        apt_widget = {
            "id": latest_apt.id,
            "score": latest_apt.score,
            "correct": latest_apt.correct_answers,
            "total": latest_apt.total_questions,
            "date": latest_apt.created_at.strftime("%b %d, %Y")
        }

    gd_widget = None
    if latest_gd:
        gd_widget = {
            "id": latest_gd.id,
            "topic": latest_gd.topic,
            "score": latest_gd.score,
            "date": latest_gd.created_at.strftime("%b %d, %Y")
        }

    int_widget = None
    if latest_int:
        int_widget = {
            "id": latest_int.id,
            "track": latest_int.interview_type,
            "role": latest_int.target_role,
            "score": latest_int.score,
            "date": latest_int.created_at.strftime("%b %d, %Y")
        }

    return DashboardResponse(
        user_name=current_user.name,
        target_role=current_user.target_role or "Software Developer",
        readiness_percentage=rec_data["readiness_percentage"],
        category_scores=rec_data["category_scores"],
        streak_days=streak_days,
        total_sessions=total_sessions,
        recent_activities=recent_activities[:5],
        weak_areas=rec_data["weak_areas"],
        recommendations=rec_data["recommendations"],
        latest_aptitude=apt_widget,
        latest_gd=gd_widget,
        latest_interview=int_widget
    )

@router.get("/ai-status")
def get_ai_status():
    """Returns whether live AI API is configured or application is running in Practice/Fallback mode."""
    return {
        "is_configured": ai_service.is_configured(),
        "provider": ai_service.provider if ai_service.is_configured() else "offline_fallback",
        "model": ai_service.model if ai_service.is_configured() else "curated_banks",
        "notice": "AI is fully operational." if ai_service.is_configured() else "Practice Mode — AI provider is not configured. Offline curated question banks and heuristic evaluation active."
    }
