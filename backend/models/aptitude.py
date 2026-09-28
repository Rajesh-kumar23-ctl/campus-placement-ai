import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database.database import Base

class AptitudeQuestion(Base):
    __tablename__ = "aptitude_questions"

    id = Column(String(50), primary_key=True)
    category = Column(String(50), nullable=False, index=True)
    category_display = Column(String(100), nullable=False)
    difficulty = Column(String(20), nullable=False, index=True)
    question = Column(String, nullable=False)
    options = Column(JSON, nullable=False)  # list of 4 options
    correct_answer = Column(String, nullable=False)
    explanation = Column(String, nullable=False)
    shortcut = Column(String, nullable=True)

class AptitudeAttempt(Base):
    __tablename__ = "aptitude_attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(50), nullable=True)
    difficulty = Column(String(20), nullable=True)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)  # percentage 0-100
    time_taken = Column(Integer, nullable=False)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="aptitude_attempts")
    answers = relationship("AptitudeAnswer", back_populates="attempt", cascade="all, delete-orphan")

class AptitudeAnswer(Base):
    __tablename__ = "aptitude_answers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    attempt_id = Column(String(36), ForeignKey("aptitude_attempts.id"), nullable=False, index=True)
    question_id = Column(String(50), nullable=False)
    selected_answer = Column(String, nullable=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    time_taken = Column(Integer, default=0)

    # Relationship
    attempt = relationship("AptitudeAttempt", back_populates="answers")
