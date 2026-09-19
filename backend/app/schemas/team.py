# schemas/team.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .project import ProjectRequirement

class TeamBuildRequest(BaseModel):
    project_description: str
    team_size: Optional[int] = None

class CandidateItem(BaseModel):
    employee_id: int
    name: str
    role: str
    years_experience: float
    department: Optional[str] = "Engineering"
    skills: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)

class CandidateEvaluation(BaseModel):
    employee_id: int
    name: str
    role: str
    role_fit: float
    skill_fit: float
    experience_fit: float
    domain_fit: float
    overall_fit: float
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)

class TeamMember(BaseModel):
    employee_id: int
    name: str
    role: str
    assigned_role: str
    project_fit: float
    skills: List[str] = Field(default_factory=list)
    why_selected: str
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)

class TeamValidation(BaseModel):
    valid: bool
    team_size_valid: bool
    roles_valid: bool
    required_skills: Dict[str, bool] = Field(default_factory=dict)
    missing_requirements: List[str] = Field(default_factory=list)

class TeamExplanation(BaseModel):
    team_strengths: List[str] = Field(default_factory=list)
    skill_coverage: Dict[str, bool] = Field(default_factory=dict)
    role_coverage: Dict[str, str] = Field(default_factory=dict)
    executive_summary: Optional[str] = None

class TeamResult(BaseModel):
    requirements: ProjectRequirement
    candidates: List[CandidateItem] = Field(default_factory=list)
    evaluations: List[CandidateEvaluation] = Field(default_factory=list)
    team: List[TeamMember] = Field(default_factory=list)
    validation: TeamValidation
    explanation: TeamExplanation
    iteration: int = 1
    feasible: bool = True
