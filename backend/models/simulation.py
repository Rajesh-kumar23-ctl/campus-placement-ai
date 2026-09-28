import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from backend.database.database import Base

class PlacementSimulation(Base):
    __tablename__ = "placement_simulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    current_round = Column(String(20), default="aptitude")  # aptitude, gd, technical, hr, completed
    target_role = Column(String(100), default="Software Developer")

    # Round Scores
    aptitude_score = Column(Float, default=0.0)
    gd_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    hr_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)

    # Detailed report data
    strengths = Column(JSON, default=list)
    weak_areas = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    round_details = Column(JSON, default=dict)
    summary_report = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationship
    user = relationship("User", back_populates="simulations")
