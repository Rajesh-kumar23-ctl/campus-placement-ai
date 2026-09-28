import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from backend.database.database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    interview_type = Column(String(50), nullable=False)  # technical, hr, managerial, cloud_engineer, software_developer, mock_interview
    target_role = Column(String(100), default="Software Developer")
    difficulty = Column(String(20), default="medium")
    status = Column(String(20), default="active")  # active, completed
    score = Column(Float, default=0.0)  # 0-100 overall
    feedback = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    improvements = Column(JSON, default=list)
    topics_to_revise = Column(JSON, default=list)
    resume_id = Column(String(36), ForeignKey("resumes.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan", order_by="InterviewQuestion.question_number")
    resume = relationship("Resume", back_populates="interviews")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    question_number = Column(Integer, nullable=False)
    category = Column(String(100), default="General")
    expected_topics = Column(JSON, default=list)

    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("interview_questions.id"), nullable=False, unique=True)
    answer = Column(Text, nullable=False)
    technical_score = Column(Float, default=0.0)
    content_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    clarity_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    improvements = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    question = relationship("InterviewQuestion", back_populates="answer")
