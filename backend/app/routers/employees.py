# routers/employees.py
import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.employee import (
    EmployeeResponse,
    EmployeeCreate,
    ResumeExtractionResponse,
)
from app.services.employee_service import (
    list_employees,
    get_employee,
    parse_and_preview_resume,
    save_employee_from_parsed,
)
from app.core.config import settings

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("", response_model=List[EmployeeResponse])
def get_all_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    search: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List employees with optional name, skill, or role search."""
    return list_employees(db, skip=skip, limit=limit, search=search, role=role)

@router.post("/seed")
def seed_test_employees(
    force: bool = Query(False, description="Force re-ingest test seed candidates"),
    db: Session = Depends(get_db),
):
    """
    Seed or verify the database with the 18 test candidates,
    complete with skills, project histories, and vector embeddings.
    """
    try:
        from seed import seed_database, SEED_EMPLOYEES
        from app.db.models import Employee
        current_count = db.query(Employee).count()
        if not force and current_count >= len(SEED_EMPLOYEES):
            return {
                "status": "ready",
                "count": current_count,
                "message": f"Database already primed with {current_count} candidate profiles."
            }
        res = seed_database(force=True)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to seed candidate data: {str(e)}")

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee_by_id(employee_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed employee profile by ID."""
    employee = get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.post("", response_model=EmployeeResponse)
def create_employee_profile(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
):
    """Save an employee with skills and projects, automatically indexing into pgvector."""
    try:
        emp = save_employee_from_parsed(db, employee_data)
        return emp
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create employee: {str(e)}")

@router.post("/upload-resume", response_model=ResumeExtractionResponse)
async def upload_resume(
    file: UploadFile = File(...),
):
    """
    Upload resume in PDF (PyMuPDF), DOCX (python-docx), or Image format (PNG, JPG, WEBP).
    Extracts text and structured profile using Gemini LLM/multimodal vision.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    content_bytes = await file.read()
    if len(content_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Optionally persist to DOCUMENT_STORAGE_PATH
    try:
        storage_dir = settings.DOCUMENT_STORAGE_PATH
        os.makedirs(storage_dir, exist_ok=True)
        save_path = os.path.join(storage_dir, file.filename)
        with open(save_path, "wb") as f:
            f.write(content_bytes)
    except Exception:
        pass

    try:
        extraction = parse_and_preview_resume(content_bytes, file.filename)
        return extraction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume extraction error: {str(e)}")
