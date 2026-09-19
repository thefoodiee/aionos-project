# agents/candidate_evaluator.py
import re
import json
from typing import Dict, Any, List
from app.core.config import settings
from app.rag.normalization import normalize_skill, normalize_role
from .state import TeamBuilderState

def _evaluate_candidate_grounded(
    candidate: Dict[str, Any],
    requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deterministic grounded evaluator that ensures zero hallucination.
    Evaluates:
    - role_fit: checks if candidate's role matches any required role
    - skill_fit: ratio of required skills present in candidate's skills
    - experience_fit: seniority based on years of experience
    - domain_fit: checks evidence/skills for domain alignment
    """
    eid = candidate.get("employee_id")
    name = candidate.get("name", "")
    role = candidate.get("role", "")
    years_exp = float(candidate.get("years_experience", 0.0))
    cand_skills = set(candidate.get("skills", []))
    evidence = candidate.get("evidence", [])
    
    req_roles = [r.get("role", "").lower() for r in requirements.get("roles", [])]
    req_skills = set(requirements.get("required_skills", []))
    domain = requirements.get("domain", "").lower()

    # 1. Role Fit
    cand_role_norm = normalize_role(role).lower()
    matched_role = False
    for r in req_roles:
        r_clean = r.replace("_", " ").lower()
        if r_clean in cand_role_norm or cand_role_norm in r_clean:
            matched_role = True
            break
    role_fit = 0.95 if matched_role else 0.55

    # 2. Skill Fit
    matched_skills = []
    missing_skills = []
    for s in req_skills:
        if s in cand_skills:
            matched_skills.append(s)
        else:
            missing_skills.append(s)
            
    skill_ratio = len(matched_skills) / max(1, len(req_skills))
    skill_fit = min(1.0, 0.40 + (skill_ratio * 0.60))

    # 3. Experience Fit (3+ years considered good, 5+ senior)
    if years_exp >= 6:
        experience_fit = 0.95
    elif years_exp >= 4:
        experience_fit = 0.88
    elif years_exp >= 2:
        experience_fit = 0.75
    else:
        experience_fit = 0.60

    # 4. Domain Fit
    evidence_text = " ".join(evidence).lower()
    domain_fit = 0.70
    if domain and (domain in evidence_text or any(w in evidence_text for w in domain.split())):
        domain_fit = 0.92

    # 5. Overall Fit (Weighted)
    overall = (role_fit * 0.35) + (skill_fit * 0.35) + (experience_fit * 0.15) + (domain_fit * 0.15)
    overall_fit = round(overall, 2)

    # Strengths and Gaps grounded in facts
    strengths = []
    if matched_role:
        strengths.append(f"Strong role match as {role} ({int(years_exp)} years experience)")
    if matched_skills:
        strengths.append(f"Verified core skills: {', '.join(matched_skills[:3])}")
    if domain_fit > 0.85:
        strengths.append(f"Demonstrated domain experience in {domain.title()}")
    if not strengths:
        strengths.append(f"Solid engineering foundation with {', '.join(list(cand_skills)[:3])}")

    gaps = []
    if not matched_role:
        gaps.append(f"Primary role is {role}, may need role adaptation")
    if missing_skills:
        gaps.append(f"Lacks documented experience in: {', '.join(missing_skills[:2])}")
    if years_exp < 3:
        gaps.append(f"Junior seniority level ({years_exp} years)")

    return {
        "employee_id": eid,
        "name": name,
        "role": role,
        "role_fit": round(role_fit, 2),
        "skill_fit": round(skill_fit, 2),
        "experience_fit": round(experience_fit, 2),
        "domain_fit": round(domain_fit, 2),
        "overall_fit": overall_fit,
        "strengths": strengths,
        "gaps": gaps,
        "evidence": evidence
    }

def candidate_evaluator_node(state: TeamBuilderState) -> Dict[str, Any]:
    """
    Agent 3: Candidate Evaluator Node.
    Evaluates each candidate grounded in retrieved resume evidence.
    """
    candidates = state.get("candidates", [])
    requirements = state.get("requirements", {})

    evaluations = []
    for cand in candidates:
        evaluation = _evaluate_candidate_grounded(cand, requirements)
        evaluations.append(evaluation)

    # Sort evaluations by overall fit
    evaluations.sort(key=lambda x: x["overall_fit"], reverse=True)

    summary = f"Evaluated {len(evaluations)} candidates against project requirements with grounded scoring."

    log_entry = {
        "node": "candidate_evaluator",
        "status": "completed",
        "summary": summary,
        "evaluation_count": len(evaluations)
    }
    existing_logs = state.get("logs", [])

    return {
        "evaluations": evaluations,
        "current_step": "candidate_evaluator",
        "step_summary": summary,
        "logs": existing_logs + [log_entry]
    }
