# agents/team_validator.py
from typing import Dict, Any, List
from .state import TeamBuilderState

def team_validator_node(state: TeamBuilderState) -> Dict[str, Any]:
    """
    Agent 5: Team Validator Node.
    Validates whether the composed team satisfies team size, roles, and mandatory skills.
    Controls iteration counter (up to 3 iterations) before declaring failure.
    """
    selected_team = state.get("selected_team", [])
    requirements = state.get("requirements", {})
    iteration = state.get("iteration", 1)

    target_size = requirements.get("team_size", 5)
    required_skills = requirements.get("required_skills", [])
    required_roles = requirements.get("roles", [])

    # 1. Validate team size
    team_size_valid = len(selected_team) >= target_size

    # 2. Validate collective skills
    all_team_skills = set()
    for member in selected_team:
        for s in member.get("skills", []):
            all_team_skills.add(s.lower())

    skill_coverage: Dict[str, bool] = {}
    missing_requirements = []

    for req_s in required_skills:
        has_skill = req_s.lower() in all_team_skills
        skill_coverage[req_s] = has_skill
        if not has_skill:
            missing_requirements.append(f"Missing required skill: {req_s}")

    # 3. Validate roles
    assigned_roles = [m.get("assigned_role", "").lower() for m in selected_team]
    roles_valid = True
    for role_item in required_roles:
        role_label = role_item.get("role", "").replace("_", " ").lower()
        count_needed = role_item.get("count", 1)
        count_present = sum(1 for ar in assigned_roles if role_label in ar or ar in role_label)
        if count_present < count_needed:
            roles_valid = False
            missing_requirements.append(f"Missing role requirement: {count_needed}x {role_label.title()}")

    # Determine overall validity
    skills_valid = all(skill_coverage.values()) if skill_coverage else True
    is_valid = team_size_valid and roles_valid and skills_valid

    validation_result = {
        "valid": is_valid,
        "team_size_valid": team_size_valid,
        "roles_valid": roles_valid,
        "required_skills": skill_coverage,
        "missing_requirements": missing_requirements,
        "iteration": iteration
    }

    if is_valid:
        summary = "Validation Passed: All team size, role, and skill requirements are satisfied."
    else:
        summary = f"Validation Warning (Iteration {iteration}/3): {len(missing_requirements)} requirement(s) unsatisfied."

    log_entry = {
        "node": "team_validator",
        "status": "completed",
        "valid": is_valid,
        "iteration": iteration,
        "summary": summary,
        "missing_requirements": missing_requirements
    }
    existing_logs = state.get("logs", [])

    return {
        "validation": validation_result,
        "iteration": iteration + 1,  # increment for next possible cycle
        "feasible": is_valid or iteration >= 3,
        "current_step": "team_validator",
        "step_summary": summary,
        "logs": existing_logs + [log_entry]
    }
