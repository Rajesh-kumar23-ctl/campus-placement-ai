from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.database.database import get_db
from backend.models.user import User
from backend.models.aptitude import AptitudeAttempt
from backend.schemas.aptitude import (
    AptitudeQuestionItem,
    AptitudeStartRequest,
    AptitudeSubmitRequest,
    AptitudeAttemptResponse
)
from backend.dependencies import get_current_user
from backend.services.aptitude_service import aptitude_service

router = APIRouter(prefix="/api/aptitude", tags=["Aptitude"])

@router.get("/categories")
def get_categories():
    """List all available aptitude categories."""
    return aptitude_service.get_categories()

@router.post("/start", response_model=List[AptitudeQuestionItem])
def start_test(
    req: AptitudeStartRequest,
    current_user: User = Depends(get_current_user)
):
    """Start an aptitude test session with selected count, category, and difficulty."""
    questions = aptitude_service.start_test(req)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questions available for the selected criteria."
        )
    return questions

@router.post("/submit", response_model=AptitudeAttemptResponse)
def submit_test(
    req: AptitudeSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit test answers, receive objective score, accuracy, category breakdown, and detailed review."""
    return aptitude_service.submit_test(db, current_user.id, req)

@router.get("/results/{attempt_id}", response_model=AptitudeAttemptResponse)
def get_attempt_result(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch complete review and scoring for a specific aptitude attempt."""
    result = aptitude_service.get_attempt_result(db, attempt_id, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aptitude test result not found."
        )
    return result

@router.get("/history")
def get_attempts_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch history of all user aptitude test attempts."""
    attempts = db.query(AptitudeAttempt).filter(
        AptitudeAttempt.user_id == current_user.id
    ).order_by(AptitudeAttempt.created_at.desc()).all()

    return [
        {
            "id": a.id,
            "category": a.category or "All",
            "difficulty": a.difficulty or "Mixed",
            "score": a.score,
            "total_questions": a.total_questions,
            "correct_answers": a.correct_answers,
            "time_taken": a.time_taken,
            "created_at": a.created_at
        }
        for a in attempts
    ]
