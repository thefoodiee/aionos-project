# services/employee_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models import Employee, Skill, EmployeeSkill, Project, EmployeeProject, DocumentChunk
from app.schemas.employee import EmployeeCreate, ResumeExtractionResponse
from app.rag.parser import ResumeParser
from app.rag.ingestion import ingest_employee, extract_structured_resume_with_gemini, heuristic_resume_parser
from app.core.config import settings

def list_employees(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None
) -> List[Employee]:
    """Retrieve employees with optional searching and role filtering."""
    query = db.query(Employee)
    if search:
        query = query.filter(or_(
            Employee.name.ilike(f"%{search}%"),
            Employee.role.ilike(f"%{search}%"),
            Employee.department.ilike(f"%{search}%")
        ))
    if role:
        query = query.filter(Employee.role.ilike(f"%{role}%"))
    return query.offset(skip).limit(limit).all()

def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    """Retrieve single employee by ID."""
    return db.query(Employee).filter(Employee.id == employee_id).first()

def parse_and_preview_resume(content_bytes: bytes, filename: str) -> ResumeExtractionResponse:
    """Extract raw text from PDF, DOCX, or Image and generate structured preview."""
    parsed = ResumeParser.extract_text(
        content_bytes=content_bytes,
        filename=filename,
        gemini_api_key=settings.GEMINI_API_KEY,
        gemini_model=settings.GEMINI_MODEL
    )
    raw_text = parsed.get("text", "")

    # Structured extraction
    structured = extract_structured_resume_with_gemini(raw_text)
    if not structured:
        structured = heuristic_resume_parser(raw_text, filename)

    return ResumeExtractionResponse(
        name=structured.get("name", "Extracted Candidate"),
        role=structured.get("role", "Software Engineer"),
        years_experience=float(structured.get("years_experience", 0.0)),
        department=structured.get("department", "Engineering"),
        skills=structured.get("skills", []),
        projects=structured.get("projects", []),
        certifications=structured.get("certifications", []),
        education=structured.get("education", []),
        raw_text=raw_text,
        filename=filename
    )

def save_employee_from_parsed(
    db: Session,
    employee_data: EmployeeCreate
) -> Employee:
    """Save an employee with skills, projects, and generated vector chunks."""
    override_dict = {
        "name": employee_data.name,
        "role": employee_data.role,
        "department": employee_data.department,
        "years_experience": employee_data.years_experience,
        "skills": [s.model_dump() for s in employee_data.skills],
        "projects": [p.model_dump() for p in employee_data.projects]
    }
    raw_text = employee_data.resume_text or f"{employee_data.name} - {employee_data.role}. Experience: {employee_data.years_experience} years."
    
    return ingest_employee(
        db=db,
        raw_text=raw_text,
        filename=employee_data.resume_filename,
        override_data=override_dict
    )
