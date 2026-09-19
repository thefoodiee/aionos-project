# schemas/employee.py
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

class SkillItem(BaseModel):
    name: str
    proficiency: str = "intermediate"
    years: float = 1.0

class ProjectItem(BaseModel):
    name: str
    domain: Optional[str] = "General"
    description: Optional[str] = ""
    technologies: List[str] = Field(default_factory=list)

class EmployeeCreate(BaseModel):
    name: str
    email: Optional[str] = None
    role: str
    department: Optional[str] = "Engineering"
    years_experience: float = 0.0
    skills: List[SkillItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    resume_filename: Optional[str] = None
    resume_text: Optional[str] = None

class SkillResponse(BaseModel):
    id: Optional[int] = None
    name: str
    proficiency: str = "intermediate"
    years_experience: float = 1.0

    @model_validator(mode="before")
    @classmethod
    def extract_from_orm(cls, data: Any) -> Any:
        if hasattr(data, "skill") and data.skill:
            return {
                "id": getattr(data, "id", None),
                "name": getattr(data.skill, "name", ""),
                "proficiency": getattr(data, "proficiency", "intermediate"),
                "years_experience": getattr(data, "years_experience", 1.0),
            }
        return data

    model_config = ConfigDict(from_attributes=True)

class ProjectResponse(BaseModel):
    id: Optional[int] = None
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None
    role: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extract_from_orm(cls, data: Any) -> Any:
        if hasattr(data, "project") and data.project:
            return {
                "id": getattr(data, "id", None),
                "name": getattr(data.project, "name", ""),
                "domain": getattr(data.project, "domain", None),
                "description": getattr(data, "description", None) or getattr(data.project, "description", None),
                "role": getattr(data, "role", None),
            }
        return data

    model_config = ConfigDict(from_attributes=True)

class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    role: str
    department: Optional[str] = None
    years_experience: float
    skills: List[SkillResponse] = Field(default_factory=list)
    projects: List[ProjectResponse] = Field(default_factory=list)
    resume_filename: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ResumeExtractionResponse(BaseModel):
    name: str
    role: str
    years_experience: float
    department: Optional[str] = "Engineering"
    skills: List[SkillItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    raw_text: str
    filename: str
