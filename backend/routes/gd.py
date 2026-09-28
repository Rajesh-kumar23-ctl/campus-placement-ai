from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from backend.database.database import get_db
from backend.models.user import User
from backend.schemas.gd import (
    GDTopicPrep,
    GDGenerateRequest,
    GDStartRequest,
    GDRespondRequest,
    GDEvaluateRequest,
    GDEvaluationResponse
)
from backend.dependencies import get_current_user
from backend.services.gd_service import gd_service

router = APIRouter(prefix="/api/gd", tags=["Group Discussion"])

@router.get("/topics")
def get_topics(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Retrieve GD topics with optional text search and category filter."""
    return gd_service.get_topics(search=search, category=category)

@router.get("/topics/{topic_id}")
def get_topic_detail(topic_id: str):
    """Retrieve full preparation details for a specific GD topic."""
    topic = gd_service.get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GD topic not found."
        )
    return topic

@router.post("/generate", response_model=GDTopicPrep)
async def generate_topic_prep(
    req: GDGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate comprehensive GD prep material for any topic (opening speech, pros/cons, speeches, examples)."""
    return await gd_service.generate_topic_prep(req)

@router.post("/start")
def start_simulation(
    req: GDStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initialize a new GD simulation session with Moderator and AI participants."""
    return gd_service.start_simulation(db, current_user.id, req)

@router.post("/respond")
async def user_respond(
    req: GDRespondRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit user response and receive AI participant counter-arguments/reactions."""
    try:
        return await gd_service.user_respond(db, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/evaluate", response_model=GDEvaluationResponse)
async def evaluate_gd(
    req: GDEvaluateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Evaluate user GD contributions across Content, Relevance, Clarity, Structure, and Fluency."""
    try:
        return await gd_service.evaluate_session(db, current_user.id, req.session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
