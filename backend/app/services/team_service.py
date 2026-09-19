# services/team_service.py
import json
from typing import Dict, Any, Optional, AsyncGenerator
from app.agents.workflow import run_workflow, run_workflow_stream
from app.schemas.team import TeamResult, TeamValidation, TeamExplanation

def execute_team_build(project_description: str, team_size: Optional[int] = None) -> TeamResult:
    """Synchronous team formation execution."""
    final_state = run_workflow(project_description, team_size)
    
    val_data = final_state.get("validation", {})
    exp_data = final_state.get("final_explanation", {})

    validation_obj = TeamValidation(
        valid=val_data.get("valid", False),
        team_size_valid=val_data.get("team_size_valid", False),
        roles_valid=val_data.get("roles_valid", False),
        required_skills=val_data.get("required_skills", {}),
        missing_requirements=val_data.get("missing_requirements", [])
    )

    explanation_obj = TeamExplanation(
        team_strengths=exp_data.get("team_strengths", []),
        skill_coverage=exp_data.get("skill_coverage", {}),
        role_coverage=exp_data.get("role_coverage", {}),
        executive_summary=exp_data.get("executive_summary")
    )

    return TeamResult(
        requirements=final_state.get("requirements", {}),
        candidates=final_state.get("candidates", []),
        evaluations=final_state.get("evaluations", []),
        team=final_state.get("selected_team", []),
        validation=validation_obj,
        explanation=explanation_obj,
        iteration=final_state.get("iteration", 1),
        feasible=final_state.get("feasible", True)
    )

async def execute_team_build_stream(
    project_description: str,
    team_size: Optional[int] = None
) -> AsyncGenerator[str, None]:
    """SSE streaming execution yielding event data."""
    async for event in run_workflow_stream(project_description, team_size):
        payload = json.dumps(event)
        yield f"data: {payload}\n\n"
