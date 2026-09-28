from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from backend.database.database import get_db
from backend.models.user import User
from backend.models.progress import Progress
from backend.schemas.auth import UserRegister, UserLogin, UserResponse, Token, UserUpdate
from backend.utils.security import hash_password, verify_password, create_access_token
from backend.dependencies import get_current_user
from backend.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new student user."""
    # Check if email exists
    existing = db.query(User).filter(User.email == user_data.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in."
        )

    hashed_pw = hash_password(user_data.password)

    new_user = User(
        name=user_data.name.strip(),
        email=user_data.email.lower().strip(),
        password_hash=hashed_pw,
        college=user_data.college.strip() if user_data.college else None,
        degree=user_data.degree.strip() if user_data.degree else None,
        branch=user_data.branch.strip() if user_data.branch else None,
        graduation_year=user_data.graduation_year,
        target_role=user_data.target_role or "Software Developer"
    )
    db.add(new_user)
    db.flush()

    # Initialize baseline skills progress
    skills = [("Aptitude", 75.0), ("GD", 65.0), ("Technical", 72.0), ("HR", 80.0), ("Communication", 70.0)]
    for skill_name, init_score in skills:
        p = Progress(user_id=new_user.id, skill=skill_name, score=init_score)
        db.add(p)

    db.commit()
    db.refresh(new_user)

    # Issue JWT token
    access_token = create_access_token(
        data={"sub": new_user.id, "email": new_user.email, "name": new_user.name},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Log in an existing user with email and password."""
    user = db.query(User).filter(User.email == credentials.email.lower().strip()).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "name": user.name},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve current authenticated user profile."""
    return UserResponse.model_validate(current_user)

@router.put("/profile", response_model=UserResponse)
def update_profile(data: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update profile details (name, college, branch, graduation year, target role)."""
    if data.name is not None:
        current_user.name = data.name.strip()
    if data.college is not None:
        current_user.college = data.college.strip()
    if data.degree is not None:
        current_user.degree = data.degree.strip()
    if data.branch is not None:
        current_user.branch = data.branch.strip()
    if data.graduation_year is not None:
        current_user.graduation_year = data.graduation_year
    if data.target_role is not None:
        current_user.target_role = data.target_role.strip()

    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint."""
    return {"message": "Logged out successfully."}
