import json
from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from backend.config import settings
from backend.schemas.company import CompanyResponse
from backend.schemas.job import LiveJobsResponse
from backend.services.job_service import get_live_jobs

router = APIRouter(prefix="/api/companies", tags=["Companies"])

def _load_companies():
    path = settings.DATA_DIR / "companies.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@router.get("", response_model=List[CompanyResponse])
def get_companies(search: Optional[str] = Query(None)):
    """Retrieve all company preparation tracks (TCS, Infosys, Amazon, etc.)."""
    companies = _load_companies()
    if search:
        q = search.lower().strip()
        companies = [c for c in companies if q in c["name"].lower() or q in c["description"].lower() or q in c["id"].lower()]
    return companies

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: str):
    """Retrieve full preparation syllabus, hiring rounds, and sample questions for a company."""
    companies = _load_companies()
    for c in companies:
        if c["id"].lower() == company_id.lower():
            return c
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found.")

@router.get("/{company_id}/jobs", response_model=LiveJobsResponse)
def get_company_live_jobs(company_id: str, limit: int = Query(10, ge=1, le=30)):
    """Retrieve real-time company vacancies and direct application links powered by Google Jobs."""
    return get_live_jobs(company=company_id, limit=limit)

