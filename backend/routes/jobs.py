from fastapi import APIRouter, Query
from typing import Optional

from backend.schemas.job import LiveJobsResponse
from backend.services.job_service import get_live_jobs

router = APIRouter(prefix="/api/jobs", tags=["Live Jobs & Real-Time Vacancies"])

@router.get("/live", response_model=LiveJobsResponse)
def get_live_company_jobs(
    company: Optional[str] = Query(None, description="Company name or ID (e.g., infosys, tcs, accenture)"),
    role: Optional[str] = Query(None, description="Job role or keywords (e.g., software engineer, intern, python)"),
    location: Optional[str] = Query(None, description="City or region (e.g., Bengaluru, Hyderabad, India)"),
    limit: int = Query(15, ge=1, le=50)
):
    """Retrieve real-time company vacancies with official application links powered by Google Jobs engine."""
    return get_live_jobs(company=company, role=role, location=location, limit=limit)

@router.get("/company/{company_id}", response_model=LiveJobsResponse)
def get_company_specific_jobs(
    company_id: str,
    limit: int = Query(10, ge=1, le=30)
):
    """Retrieve real-time recruitment drives and direct application links for a specific company."""
    return get_live_jobs(company=company_id, limit=limit)
