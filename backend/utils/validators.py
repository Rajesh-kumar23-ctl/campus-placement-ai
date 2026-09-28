import os
from fastapi import HTTPException, UploadFile, status

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

def validate_resume_file(file: UploadFile) -> str:
    """Validate uploaded resume file extension and size."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file submitted."
        )

    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats are PDF and DOCX only."
        )

    return ext
