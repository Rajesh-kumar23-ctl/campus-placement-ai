import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Placement Coach"
    TAGLINE: str = "Prepare Smarter. Practice Harder. Perform Better."
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./placement_coach.db")

    # Security & JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super_secret_placement_coach_jwt_key_2026_xyz")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # CORS
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000")

    # AI Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "")

    # Google Jobs / SerpApi Configuration
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", os.getenv("GOOGLE_JOBS_API_KEY", ""))

    # Directories
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOADS_DIR: Path = BASE_DIR / "uploads"
    FRONTEND_DIR: Path = BASE_DIR / "frontend"

    # Evaluation Weights
    # Interview Score: Tech 30%, Content 20%, Relevance 20%, Clarity 15%, Communication 15%
    INTERVIEW_WEIGHTS: dict = {
        "technical": 0.30,
        "content": 0.20,
        "relevance": 0.20,
        "clarity": 0.15,
        "communication": 0.15
    }

    # GD Score: Content 25%, Relevance 20%, Clarity 20%, Structure 15%, Fluency 20%
    GD_WEIGHTS: dict = {
        "content": 0.25,
        "relevance": 0.20,
        "clarity": 0.20,
        "structure": 0.15,
        "fluency": 0.20
    }

    # Preparation Readiness: Aptitude 25%, GD 20%, Technical 30%, HR 15%, Communication 10%
    READINESS_WEIGHTS: dict = {
        "aptitude": 0.25,
        "gd": 0.20,
        "technical": 0.30,
        "hr": 0.15,
        "communication": 0.10
    }

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")

settings = Settings()
