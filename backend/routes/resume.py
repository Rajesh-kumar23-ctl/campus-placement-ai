from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.database.database import get_db
from backend.models.user import User
from backend.models.resume import Resume
from backend.schemas.resume import ResumeResponse, ResumeQuestionGenerateRequest
from backend.dependencies import get_current_user
from backend.services.resume_service import resume_service
from backend.utils.validators import validate_resume_file

router = APIRouter(prefix="/api/resume", tags=["Resume AI"])

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse a candidate resume (PDF or DOCX), extracting skills, projects, and interview questions."""
    validate_resume_file(file)
    resume = await resume_service.save_and_parse_resume(db, current_user.id, file)
    return ResumeResponse.model_validate(resume)

@router.get("/latest", response_model=ResumeResponse)
def get_latest_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the user's latest parsed resume."""
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(Resume.created_at.desc()).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume uploaded yet."
        )
    return ResumeResponse.model_validate(resume)

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific uploaded resume."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found."
        )
    return ResumeResponse.model_validate(resume)

@router.post("/questions")
async def generate_resume_questions(
    req: ResumeQuestionGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate interview questions directly tied to candidate's parsed skills and projects."""
    questions = await resume_service.generate_resume_questions(
        db, req.resume_id, req.target_role or current_user.target_role or "Software Developer"
    )
    return {"resume_id": req.resume_id, "questions": questions}
