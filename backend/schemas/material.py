from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

class MaterialItem(BaseModel):
    id: str
    title: str
    filename: str
    company: str
    subfolder: Optional[str] = None
    category: str
    format: str
    is_folder: bool = False
    file_id: str
    parent_folder_id: Optional[str] = None
    view_url: str
    download_url: str
    description: str
    tags: List[str] = []
    featured: bool = False

    model_config = ConfigDict(from_attributes=True)

class MaterialListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    drive_root_url: str
    materials: List[MaterialItem]

class CompanyMaterialSummary(BaseModel):
    company: str
    count: int
    categories: Dict[str, int]
    folder_url: str
