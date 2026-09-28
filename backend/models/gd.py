import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from backend.database.database import Base

class GDSession(Base):
    __tablename__ = "gd_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    duration = Column(Integer, default=5)  # minutes
    difficulty = Column(String(20), default="Medium")
    num_participants = Column(Integer, default=3)
    score = Column(Float, default=0.0)  # 0-100 overall
    strengths = Column(JSON, default=list)
    improvements = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="gd_sessions")
    responses = relationship("GDResponse", back_populates="session", cascade="all, delete-orphan")

class GDResponse(Base):
    __tablename__ = "gd_responses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("gd_sessions.id"), nullable=False, index=True)
    speaker = Column(String(50), nullable=False)  # "User", "Moderator", "Participant 1", etc.
    response = Column(Text, nullable=False)
    content_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    clarity_score = Column(Float, default=0.0)
    structure_score = Column(Float, default=0.0)
    fluency_score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("GDSession", back_populates="responses")
