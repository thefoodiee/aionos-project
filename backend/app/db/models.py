# db/models.py
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from .database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    role = Column(String(255), nullable=False, index=True)
    department = Column(String(255), nullable=True)
    years_experience = Column(Float, default=0.0)
    resume_filename = Column(String(255), nullable=True)
    resume_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    projects = relationship("EmployeeProject", back_populates="employee", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="employee", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    employee_skills = relationship("EmployeeSkill", back_populates="skill", cascade="all, delete-orphan")


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency = Column(String(50), default="intermediate")
    years_experience = Column(Float, default=1.0)

    __table_args__ = (
        UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
    )

    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employee_skills")

    @property
    def name(self) -> str:
        return self.skill.name if self.skill else ""


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(255), nullable=True)

    employee_projects = relationship("EmployeeProject", back_populates="project", cascade="all, delete-orphan")


class EmployeeProject(Base):
    __tablename__ = "employee_projects"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("employee_id", "project_id", name="uq_employee_project"),
    )

    employee = relationship("Employee", back_populates="projects")
    project = relationship("Project", back_populates="employee_projects")

    @property
    def name(self) -> str:
        return self.project.name if self.project else ""

    @property
    def domain(self) -> str:
        return self.project.domain if self.project else ""


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384))
    metadata_json = Column(JSON, default=dict)

    employee = relationship("Employee", back_populates="chunks")
