# agents/project_analyzer.py
import re
import json
from typing import Dict, Any, List
from app.core.config import settings
from app.rag.normalization import normalize_skill, normalize_role
from .prompts import PROJECT_ANALYZER_SYSTEM_PROMPT
from .state import TeamBuilderState

def _heuristic_project_analyzer(description: str, target_size: int = 5) -> Dict[str, Any]:
    """Deterministic fallback analyzer when LLM API is unavailable."""
    lower = description.lower()
    
    # Identify roles requested
    roles = []
    if "lead" in lower or "architect" in lower:
        roles.append({"role": "technical_lead", "count": 1})
    if "backend" in lower or "back-end" in lower:
        # Check for count like 'two backend' or '2 backend'
        count = 2 if ("two backend" in lower or "2 backend" in lower) else 1
        roles.append({"role": "backend_developer", "count": count})
    if "frontend" in lower or "front-end" in lower or "react" in lower:
        roles.append({"role": "frontend_developer", "count": 1})
    if "ml" in lower or "machine learning" in lower or "ai" in lower or "nlp" in lower:
        roles.append({"role": "ml_engineer", "count": 1})
    if "qa" in lower or "quality" in lower or "test" in lower:
        roles.append({"role": "qa_engineer", "count": 1})
    if "devops" in lower or "infra" in lower:
        roles.append({"role": "devops_engineer", "count": 1})

    # Default roles if none matched
    if not roles:
        roles = [
            {"role": "technical_lead", "count": 1},
            {"role": "backend_developer", "count": 2},
            {"role": "frontend_developer", "count": 1},
            {"role": "ml_engineer", "count": 1},
        ]

    # Adjust counts to match target_size
    current_sum = sum(r["count"] for r in roles)
    if current_sum < target_size:
        diff = target_size - current_sum
        # Add to backend or generic
        roles[0]["count"] += diff
    elif current_sum > target_size and len(roles) > 1:
        roles = roles[:target_size]

    # Extract common skills mentioned
    known_skills = [
        "React", "FastAPI", "PostgreSQL", "AWS", "LLM", "RAG", "Python",
        "Docker", "Kubernetes", "TypeScript", "PyTorch", "Playwright", "Selenium"
    ]
    required_skills = []
    for s in known_skills:
        if re.search(r"\b" + re.escape(s) + r"\b", description, re.IGNORECASE):
            required_skills.append(normalize_skill(s))

    if not required_skills:
        required_skills = ["Python", "React", "PostgreSQL", "FastAPI", "AWS"]

    # Detect domain
    domain = "General Software"
    if "customer support" in lower:
        domain = "Customer Support"
    elif "e-commerce" in lower or "ecommerce" in lower:
        domain = "E-Commerce"
    elif "payment" in lower or "fintech" in lower:
        domain = "Financial Services"
    elif "health" in lower:
        domain = "Healthcare"

    return {
        "team_size": sum(r["count"] for r in roles),
        "roles": roles,
        "required_skills": required_skills,
        "preferred_skills": ["Docker", "Git", "CI/CD"],
        "domain": domain
    }

def project_analyzer_node(state: TeamBuilderState) -> Dict[str, Any]:
    """
    Agent 1: Project Analyzer Node.
    Extracts structured requirements from project description.
    """
    desc = state.get("project_description", "")
    target_size = state.get("target_team_size") or 5
    
    requirements = None

    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = f"{PROJECT_ANALYZER_SYSTEM_PROMPT}\n\nProject Description:\n{desc}\nTarget Team Size: {target_size}"
            resp = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )
            if resp.text:
                clean = resp.text.strip()
                if clean.startswith("```"):
                    clean = re.sub(r"^```[a-zA-Z]*\n", "", clean)
                    clean = re.sub(r"\n```$", "", clean)
                data = json.loads(clean)
                # Normalize skills
                data["required_skills"] = [normalize_skill(s) for s in data.get("required_skills", [])]
                data["preferred_skills"] = [normalize_skill(s) for s in data.get("preferred_skills", [])]
                requirements = data
        except Exception as e:
            print(f"Notice: Gemini Project Analyzer error ({e}). Using heuristic fallback.")

    if not requirements:
        requirements = _heuristic_project_analyzer(desc, target_size)

    role_summary = ", ".join(f"{r['count']}x {r['role'].replace('_', ' ').title()}" for r in requirements.get("roles", []))
    summary = f"Extracted {requirements.get('team_size', target_size)} roles ({role_summary}) and {len(requirements.get('required_skills', []))} required skills."

    log_entry = {
        "node": "project_analyzer",
        "status": "completed",
        "summary": summary,
        "data": requirements
    }
    existing_logs = state.get("logs", [])

    return {
        "requirements": requirements,
        "current_step": "project_analyzer",
        "step_summary": summary,
        "logs": existing_logs + [log_entry]
    }
