# rag/ingestion.py
import re
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Employee, Skill, EmployeeSkill, Project, EmployeeProject, DocumentChunk
from .normalization import normalize_skill, normalize_role
from .embeddings import get_embedding

EXTRACTION_SYSTEM_PROMPT = """You are an expert HR Resume Parser. Extract structured information from the resume text into valid JSON matching this schema:
{
  "name": "Candidate Full Name",
  "role": "Current or primary job title (e.g. Senior Backend Engineer)",
  "department": "Department (e.g. Engineering, Product, QA, Data)",
  "years_experience": 5.0,
  "skills": [
    {
      "name": "Python",
      "proficiency": "advanced",
      "years": 5.0
    }
  ],
  "projects": [
    {
      "name": "Project Title",
      "domain": "Domain (e.g. E-commerce, FinTech, Healthcare)",
      "description": "Brief description of responsibilities and impact",
      "technologies": ["Python", "FastAPI", "PostgreSQL"]
    }
  ],
  "certifications": ["AWS Certified Solutions Architect"],
  "education": ["B.S. Computer Science"]
}
Respond ONLY with the JSON object. Do not include markdown code block syntax or preamble."""

def extract_structured_resume_with_gemini(raw_text: str) -> Optional[Dict[str, Any]]:
    """Use Gemini to extract structured JSON from resume text."""
    if not settings.GEMINI_API_KEY:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=f"{EXTRACTION_SYSTEM_PROMPT}\n\nResume Content:\n{raw_text[:8000]}"
        )
        if response.text:
            text = response.text.strip()
            # Strip markdown formatting if any
            if text.startswith("```"):
                text = re.sub(r"^```[a-zA-Z]*\n", "", text)
                text = re.sub(r"\n```$", "", text)
            return json.loads(text)
    except Exception as e:
        print(f"Notice: Gemini extraction failed ({e}), falling back to heuristic parser.")
    return None

def heuristic_resume_parser(raw_text: str, filename: str = "") -> Dict[str, Any]:
    """Robust fallback extractor if LLM is unavailable."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    name = lines[0] if lines else Path(filename).stem.replace("_", " ").title()
    if len(name) > 50:
        name = "Candidate Profile"

    # Guess role from lines
    role = "Software Engineer"
    for line in lines[:5]:
        lower = line.lower()
        if any(keyword in lower for keyword in ["engineer", "developer", "lead", "architect", "qa", "analyst"]):
            role = line
            break

    # Look for years of experience
    exp_match = re.search(r"(\d+)\+?\s*years?(?:\s+of)?\s+experience", raw_text, re.IGNORECASE)
    years_exp = float(exp_match.group(1)) if exp_match else 3.0

    # Common skills dictionary
    known_skills = [
        "Python", "FastAPI", "PostgreSQL", "React", "Next.js", "TypeScript", "JavaScript",
        "AWS", "Docker", "Kubernetes", "PyTorch", "TensorFlow", "LLM", "RAG", "Playwright",
        "Selenium", "PyTest", "Django", "Flask", "Node.js", "GraphQL", "Redis", "Kafka",
        "CI/CD", "Tailwind CSS", "Go", "Java", "Spring Boot"
    ]
    extracted_skills = []
    for skill in known_skills:
        if re.search(r"\b" + re.escape(skill) + r"\b", raw_text, re.IGNORECASE):
            extracted_skills.append({
                "name": skill,
                "proficiency": "advanced" if years_exp >= 4 else "intermediate",
                "years": max(1.0, years_exp * 0.8)
            })

    return {
        "name": name,
        "role": normalize_role(role),
        "department": "Engineering",
        "years_experience": years_exp,
        "skills": extracted_skills,
        "projects": [
            {
                "name": f"{role} Core Initiatives",
                "domain": "Technology",
                "description": raw_text[:300] + "...",
                "technologies": [s["name"] for s in extracted_skills[:5]]
            }
        ],
        "certifications": [],
        "education": []
    }

def chunk_employee_data(employee_id: int, employee_name: str, role: str, raw_text: str, projects: List[Dict[str, Any]], skills: List[str]) -> List[Dict[str, Any]]:
    """
    Produce semantically rich document chunks for vector search:
    - Summary profile chunk
    - Individual project chunks with technical detail
    - Skills overview chunk
    """
    chunks = []
    
    # 1. Summary chunk
    skills_str = ", ".join(skills)
    summary_content = (
        f"Employee: {employee_name}. Role: {role}. "
        f"Core Technical Competencies: {skills_str}. "
        f"Overview: {raw_text[:400].strip()}"
    )
    chunks.append({
        "employee_id": employee_id,
        "content": summary_content,
        "metadata_json": {
            "type": "summary",
            "role": role,
            "skills": skills
        }
    })

    # 2. Individual project chunks
    for proj in projects:
        proj_name = proj.get("name", "Project")
        domain = proj.get("domain", "General")
        desc = proj.get("description", "")
        techs = proj.get("technologies", [])
        techs_str = ", ".join(techs) if techs else "Various technologies"
        
        proj_content = (
            f"{employee_name} ({role}) worked on '{proj_name}' in the {domain} domain. "
            f"Technologies used: {techs_str}. "
            f"Project details: {desc}"
        )
        chunks.append({
            "employee_id": employee_id,
            "content": proj_content,
            "metadata_json": {
                "type": "project",
                "project_name": proj_name,
                "domain": domain,
                "technologies": techs
            }
        })

    # 3. Text paragraph chunks for detailed experience
    paragraphs = [p.strip() for p in raw_text.split("\n\n") if len(p.strip()) > 80]
    for idx, p in enumerate(paragraphs[:4]):
        chunks.append({
            "employee_id": employee_id,
            "content": f"{employee_name} experience snippet: {p}",
            "metadata_json": {
                "type": "experience_detail",
                "snippet_index": idx
            }
        })

    return chunks

def ingest_employee(
    db: Session,
    raw_text: str,
    filename: Optional[str] = None,
    override_data: Optional[Dict[str, Any]] = None
) -> Employee:
    """
    Ingest an employee into PostgreSQL and index embeddings into pgvector.
    """
    # 1. Extract structured data
    structured = override_data
    if not structured:
        structured = extract_structured_resume_with_gemini(raw_text)
    if not structured:
        structured = heuristic_resume_parser(raw_text, filename or "resume")

    name = structured.get("name", "Unknown Candidate")
    role = normalize_role(structured.get("role", "Software Engineer"))
    department = structured.get("department", "Engineering")
    years_exp = float(structured.get("years_experience", 0.0))
    email = f"{name.lower().replace(' ', '.')}@company.com"

    # Check existing employee by name or email
    employee = db.query(Employee).filter((Employee.name == name) | (Employee.email == email)).first()
    if not employee:
        employee = Employee(
            name=name,
            email=email,
            role=role,
            department=department,
            years_experience=years_exp,
            resume_filename=filename,
            resume_text=raw_text
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
    else:
        employee.role = role
        employee.department = department
        employee.years_experience = years_exp
        employee.resume_filename = filename
        employee.resume_text = raw_text
        db.commit()

    # 2. Add skills with normalization
    db.query(EmployeeSkill).filter(EmployeeSkill.employee_id == employee.id).delete()
    db.commit()

    skill_names = []
    for skill_data in structured.get("skills", []):
        norm_name = normalize_skill(skill_data.get("name", ""))
        if not norm_name:
            continue
        skill_names.append(norm_name)

        skill_obj = db.query(Skill).filter(Skill.name == norm_name).first()
        if not skill_obj:
            skill_obj = Skill(name=norm_name)
            db.add(skill_obj)
            db.commit()
            db.refresh(skill_obj)

        emp_skill = EmployeeSkill(
            employee_id=employee.id,
            skill_id=skill_obj.id,
            proficiency=skill_data.get("proficiency", "intermediate"),
            years_experience=float(skill_data.get("years", 1.0))
        )
        db.add(emp_skill)
    db.commit()

    # 3. Add projects
    db.query(EmployeeProject).filter(EmployeeProject.employee_id == employee.id).delete()
    db.commit()

    for proj_data in structured.get("projects", []):
        proj_name = proj_data.get("name", "Project")
        domain = proj_data.get("domain", "Technology")
        desc = proj_data.get("description", "")

        project_obj = db.query(Project).filter(Project.name == proj_name).first()
        if not project_obj:
            project_obj = Project(
                name=proj_name,
                description=desc,
                domain=domain
            )
            db.add(project_obj)
            db.commit()
            db.refresh(project_obj)

        emp_proj = EmployeeProject(
            employee_id=employee.id,
            project_id=project_obj.id,
            role=role,
            description=desc
        )
        db.add(emp_proj)
    db.commit()

    # 4. Chunk & Generate pgvector embeddings
    db.query(DocumentChunk).filter(DocumentChunk.employee_id == employee.id).delete()
    db.commit()

    chunks_data = chunk_employee_data(
        employee_id=employee.id,
        employee_name=name,
        role=role,
        raw_text=raw_text,
        projects=structured.get("projects", []),
        skills=skill_names
    )

    for c in chunks_data:
        emb = get_embedding(c["content"])
        chunk_obj = DocumentChunk(
            employee_id=employee.id,
            content=c["content"],
            embedding=emb,
            metadata_json=c["metadata_json"]
        )
        db.add(chunk_obj)
    db.commit()

    return employee
