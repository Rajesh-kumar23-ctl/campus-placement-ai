from sqlalchemy import Column, String, JSON, Text
from backend.database.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    tier = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    hiring_pattern = Column(JSON, default=dict)
    preparation_areas = Column(JSON, default=list)
    technical_topics = Column(JSON, default=list)
    hr_topics = Column(JSON, default=list)
    sample_questions = Column(JSON, default=list)
