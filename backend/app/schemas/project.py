# schemas/project.py
from typing import List, Optional
from pydantic import BaseModel, Field

class ProjectRoleRequirement(BaseModel):
    role: str
    count: int = 1

class ProjectRequirement(BaseModel):
    team_size: int = 5
    roles: List[ProjectRoleRequirement] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    domain: Optional[str] = "General"
