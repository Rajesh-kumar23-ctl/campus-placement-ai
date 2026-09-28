from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.database.database import get_db
from backend.models.user import User
from backend.models.interview import InterviewSession
from backend.schemas.interview import (
    InterviewStartRequest,
    InterviewAnswerSubmit,
    InterviewAnswerResponse,
    InterviewEndRequest,
    InterviewSessionResponse
)
from backend.dependencies import get_current_user
from backend.services.interview_service import interview_service

router = APIRouter(prefix="/api/interview", tags=["AI Interview"])

@router.post("/start")
def start_interview(
    req: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start an AI Interview session for selected track (Cloud Engineer, Technical, HR, etc.)."""
    return interview_service.start_interview(db, current_user.id, req)

@router.post("/answer", response_model=InterviewAnswerResponse)
async def submit_answer(
    req: InterviewAnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit candidate's answer for evaluation and receive dynamic next question."""
    try:
        return await interview_service.submit_answer(db, current_user.id, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/end", response_model=InterviewSessionResponse)
async def end_interview(
    req: InterviewEndRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End interview session and generate final performance evaluation report."""
    try:
        return await interview_service.end_interview(db, current_user.id, req.session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/history")
def get_interview_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List completed interview sessions."""
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.created_at.desc()).all()

    return [
        {
            "id": s.id,
            "interview_type": s.interview_type,
            "target_role": s.target_role,
            "difficulty": s.difficulty,
            "status": s.status,
            "score": s.score,
            "created_at": s.created_at,
            "completed_at": s.completed_at
        }
        for s in sessions
    ]

@router.get("/{session_id}", response_model=InterviewSessionResponse)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full interview transcript, questions, answers, and scores."""
    session_data = interview_service.get_session_details(db, session_id, current_user.id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found."
        )
    return session_data
