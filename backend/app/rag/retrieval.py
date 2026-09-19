# rag/retrieval.py
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.db.models import Employee, Skill, EmployeeSkill, DocumentChunk, Project, EmployeeProject
from .embeddings import get_embedding
from .normalization import normalize_skill, normalize_role

def semantic_resume_search(
    db: Session,
    query_text: str,
    top_k: int = 20,
    employee_ids: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """
    Search document_chunks using pgvector cosine distance.
    Returns list of chunks with distance and employee info.
    """
    query_embedding = get_embedding(query_text)
    
    query = db.query(
        DocumentChunk,
        DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
    )
    
    if employee_ids:
        query = query.filter(DocumentChunk.employee_id.in_(employee_ids))
        
    results = query.order_by("distance").limit(top_k).all()
    
    hits = []
    for chunk, dist in results:
        # Distance is cosine distance in [0, 2]; similarity is 1 - distance
        similarity = max(0.0, 1.0 - float(dist))
        hits.append({
            "chunk_id": chunk.id,
            "employee_id": chunk.employee_id,
            "content": chunk.content,
            "metadata": chunk.metadata_json or {},
            "similarity": round(similarity, 4),
            "distance": round(float(dist), 4),
        })
    return hits

def search_by_skill(db: Session, skills: List[str]) -> List[int]:
    """Retrieve employee IDs that match any of the specified skills."""
    normalized = [normalize_skill(s) for s in skills if s]
    if not normalized:
        return []
    
    matched_ids = (
        db.query(EmployeeSkill.employee_id)
        .join(Skill, EmployeeSkill.skill_id == Skill.id)
        .filter(Skill.name.in_(normalized))
        .distinct()
        .all()
    )
    return [row[0] for row in matched_ids]

def search_by_role(db: Session, role_pattern: str) -> List[int]:
    """Retrieve employee IDs matching a role name/category."""
    norm_role = normalize_role(role_pattern)
    matched = (
        db.query(Employee.id)
        .filter(or_(
            Employee.role.ilike(f"%{norm_role}%"),
            Employee.role.ilike(f"%{role_pattern}%")
        ))
        .all()
    )
    return [row[0] for row in matched]

def get_employee_profile(db: Session, employee_id: int) -> Optional[Dict[str, Any]]:
    """Fetch complete profile for an employee."""
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        return None
    
    skills = [
        {
            "name": es.skill.name,
            "proficiency": es.proficiency,
            "years": es.years_experience
        }
        for es in emp.skills
    ]
    
    projects = [
        {
            "name": ep.project.name,
            "domain": ep.project.domain,
            "description": ep.description or ep.project.description,
            "role": ep.role
        }
        for ep in emp.projects
    ]
    
    return {
        "id": emp.id,
        "name": emp.name,
        "email": emp.email,
        "role": emp.role,
        "department": emp.department,
        "years_experience": emp.years_experience,
        "skills": skills,
        "projects": projects,
        "resume_text": emp.resume_text,
    }

def hybrid_candidate_search(
    db: Session,
    project_description: str,
    required_roles: List[str],
    required_skills: List[str],
    top_k: int = 15
) -> List[Dict[str, Any]]:
    """
    Perform hybrid retrieval:
    1. Structured filtering by skills and roles
    2. Semantic vector retrieval across resume/project chunks
    3. Aggregate and score candidate pool with grounded evidence snippets
    """
    # 1. Structured candidate gathering
    skill_emp_ids = set(search_by_skill(db, required_skills))
    role_emp_ids = set()
    for r in required_roles:
        role_emp_ids.update(search_by_role(db, r))

    # Structured priority pool
    structured_ids = list(skill_emp_ids.union(role_emp_ids))
    
    # 2. Semantic retrieval across all chunks (or prioritizing structured matches)
    semantic_hits = semantic_resume_search(
        db,
        query_text=project_description,
        top_k=40
    )

    # 3. Organize candidate evidence and scores
    candidate_evidence: Dict[int, List[str]] = {}
    candidate_scores: Dict[int, float] = {}

    for hit in semantic_hits:
        eid = hit["employee_id"]
        candidate_scores[eid] = candidate_scores.get(eid, 0.0) + hit["similarity"]
        if eid not in candidate_evidence:
            candidate_evidence[eid] = []
        
        # Add snippet if concise and informative
        content = hit["content"]
        if len(content) > 200:
            content = content[:200] + "..."
        if content not in candidate_evidence[eid] and len(candidate_evidence[eid]) < 4:
            candidate_evidence[eid].append(content)

    # Boost score for structured skill and role matches
    for eid in structured_ids:
        candidate_scores[eid] = candidate_scores.get(eid, 0.0) + 1.2
        if eid in skill_emp_ids:
            candidate_scores[eid] += 0.5
        if eid in role_emp_ids:
            candidate_scores[eid] += 0.5

    # If candidate pool is too small, pull all employees
    all_employees = db.query(Employee).all()
    for emp in all_employees:
        if emp.id not in candidate_scores:
            candidate_scores[emp.id] = 0.1

    # Sort candidates by combined relevance
    sorted_eids = sorted(candidate_scores.keys(), key=lambda x: candidate_scores[x], reverse=True)[:top_k]

    candidate_results = []
    for eid in sorted_eids:
        emp = db.query(Employee).filter(Employee.id == eid).first()
        if not emp:
            continue
        
        emp_skills = [es.skill.name for es in emp.skills]
        evidence_list = candidate_evidence.get(eid, [])
        
        # Ensure at least 1 grounded piece of evidence
        if not evidence_list:
            evidence_list = [
                f"{emp.years_experience} years of experience as {emp.role} with core skills: {', '.join(emp_skills[:4])}"
            ]

        candidate_results.append({
            "employee_id": emp.id,
            "name": emp.name,
            "role": emp.role,
            "years_experience": emp.years_experience,
            "department": emp.department or "Engineering",
            "skills": emp_skills,
            "evidence": evidence_list,
            "relevance_score": round(candidate_scores[eid], 3)
        })

    return candidate_results
