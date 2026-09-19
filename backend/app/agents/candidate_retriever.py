# agents/candidate_retriever.py
from typing import Dict, Any, List
from app.db.database import SessionLocal
from app.rag.retrieval import hybrid_candidate_search, search_by_skill
from .state import TeamBuilderState

def candidate_retriever_node(state: TeamBuilderState) -> Dict[str, Any]:
    """
    Agent 2: Candidate Retrieval Node.
    Executes hybrid retrieval (structured SQL filters + pgvector cosine similarity).
    If looping after a failed validation, specifically targets missing requirements.
    """
    requirements = state.get("requirements", {})
    desc = state.get("project_description", "")
    validation = state.get("validation", {})
    iteration = state.get("iteration", 1)
    
    required_skills = list(requirements.get("required_skills", []))
    roles = [r.get("role", "") for r in requirements.get("roles", [])]

    # If retrying, enhance search query with missing requirements
    missing = validation.get("missing_requirements", [])
    search_query = desc
    if missing and iteration > 1:
        search_query = f"{desc} Specialized expertise needed: {' '.join(missing)}"
        # Add missing items to required skills if relevant
        for m in missing:
            if m not in required_skills:
                required_skills.append(m)

    db = SessionLocal()
    try:
        candidates = hybrid_candidate_search(
            db=db,
            project_description=search_query,
            required_roles=roles,
            required_skills=required_skills,
            top_k=14
        )
    finally:
        db.close()

    summary = f"Retrieved {len(candidates)} candidates via hybrid search (SQL filtering + pgvector cosine similarity)."
    if iteration > 1:
        summary += f" (Retry iteration {iteration} targeting missing skills)"

    log_entry = {
        "node": "candidate_retriever",
        "status": "completed",
        "summary": summary,
        "candidate_count": len(candidates)
    }
    existing_logs = state.get("logs", [])

    return {
        "candidates": candidates,
        "current_step": "candidate_retriever",
        "step_summary": summary,
        "logs": existing_logs + [log_entry]
    }
