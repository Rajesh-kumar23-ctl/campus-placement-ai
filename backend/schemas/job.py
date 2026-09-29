from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

class JobListing(BaseModel):
    id: str
    title: str
    company_name: str
    company_id: Optional[str] = None
    location: str
    via: str = "Google Jobs / Official Portal"
    posted_at: str = "Recently"
    schedule_type: str = "Full-time"
    experience: str = "0 - 1 Years (Freshers Eligible)"
    description_snippet: str = ""
    apply_url: str
    google_jobs_url: str
    batch_eligibility: str = "2024 / 2025 / 2026 Graduates"
    is_live: bool = True
    source: str = "Google Jobs Engine"

    model_config = ConfigDict(from_attributes=True)

class LiveJobsResponse(BaseModel):
    total: int
    query: str
    company: Optional[str] = None
    location: Optional[str] = None
    google_jobs_search_url: str
    jobs: List[JobListing]
    engine_status: str

    model_config = ConfigDict(from_attributes=True)
