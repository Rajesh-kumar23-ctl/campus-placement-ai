import json
import math
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional, Dict, Any

from backend.config import settings
from backend.schemas.material import MaterialItem, MaterialListResponse, CompanyMaterialSummary

router = APIRouter(prefix="/api/materials", tags=["Placement Materials"])

def _load_data() -> Dict[str, Any]:
    file_path = settings.DATA_DIR / "placement_materials.json"
    if not file_path.exists():
        return {"drive_root_url": "", "materials": [], "categories": []}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("", response_model=MaterialListResponse)
def get_materials(
    search: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
    featured_only: Optional[bool] = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100)
):
    """Retrieve placement materials with multi-faceted search, company, and category filters."""
    data = _load_data()
    materials = data.get("materials", [])
    drive_root_url = data.get("drive_root_url", "")

    # Filters
    if search:
        q = search.lower().strip()
        materials = [
            m for m in materials
            if q in m["title"].lower()
            or q in m["company"].lower()
            or q in m["filename"].lower()
            or q in m["description"].lower()
            or any(q in t.lower() for t in m.get("tags", []))
        ]

    if company and company.lower() != "all":
        c_clean = company.lower().strip()
        materials = [m for m in materials if c_clean in m["company"].lower()]

    if category and category.lower() != "all":
        cat_clean = category.lower().strip()
        materials = [m for m in materials if cat_clean in m["category"].lower()]

    if format and format.lower() != "all":
        fmt_clean = format.lower().strip()
        materials = [m for m in materials if fmt_clean in m["format"].lower()]

    if featured_only:
        materials = [m for m in materials if m.get("featured", False)]

    total = len(materials)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    offset = (page - 1) * limit
    paginated = materials[offset : offset + limit]

    return MaterialListResponse(
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages,
        drive_root_url=drive_root_url,
        materials=paginated
    )

@router.get("/companies", response_model=List[CompanyMaterialSummary])
def get_material_companies():
    """Get list of all companies/platforms with their material counts and folder links."""
    data = _load_data()
    materials = data.get("materials", [])
    
    comp_map: Dict[str, Dict[str, Any]] = {}
    for m in materials:
        c = m["company"]
        if c not in comp_map:
            folder_id = m.get("parent_folder_id", "")
            comp_map[c] = {
                "company": c,
                "count": 0,
                "categories": {},
                "folder_url": f"https://drive.google.com/drive/folders/{folder_id}" if folder_id else data.get("drive_root_url", "")
            }
        comp_map[c]["count"] += 1
        cat = m["category"]
        comp_map[c]["categories"][cat] = comp_map[c]["categories"].get(cat, 0) + 1

    sorted_companies = sorted(comp_map.values(), key=lambda x: x["count"], reverse=True)
    return [CompanyMaterialSummary(**c) for c in sorted_companies]

@router.get("/categories")
def get_material_categories():
    """Get list of categories with item counts."""
    data = _load_data()
    materials = data.get("materials", [])
    
    cat_counts: Dict[str, int] = {}
    for m in materials:
        c = m["category"]
        cat_counts[c] = cat_counts.get(c, 0) + 1
        
    return {
        "categories": [
            {"name": k, "count": v}
            for k, v in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)
        ],
        "total_materials": len(materials),
        "drive_root_url": data.get("drive_root_url", "")
    }

@router.get("/company/{company_name}", response_model=List[MaterialItem])
def get_company_materials(company_name: str, limit: int = Query(50, ge=1, le=100)):
    """Retrieve placement materials for a specific company (e.g. for company detail page)."""
    data = _load_data()
    materials = data.get("materials", [])
    c_clean = company_name.lower().strip()

    filtered = [
        m for m in materials
        if c_clean in m["company"].lower() or m["company"].lower() in c_clean
    ]
    return filtered[:limit]

@router.get("/drive-info")
def get_drive_root_info():
    """Get Google Drive master folder URL and high-level stats."""
    data = _load_data()
    return {
        "drive_root_url": data.get("drive_root_url", ""),
        "folder_name": data.get("drive_folder_name", "Placement material"),
        "total_materials": len(data.get("materials", [])),
        "companies_count": data.get("companies_count", 0),
        "categories": data.get("categories", [])
    }

@router.get("/{material_id}", response_model=MaterialItem)
def get_material_detail(material_id: str):
    """Retrieve full metadata for a single material item."""
    data = _load_data()
    materials = data.get("materials", [])
    for m in materials:
        if m["id"] == material_id:
            return m
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found.")
