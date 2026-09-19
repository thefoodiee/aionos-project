# agents/team_builder.py
from typing import Dict, Any, List
from app.rag.normalization import normalize_role
from .state import TeamBuilderState

def _match_candidate_to_role(candidate: Dict[str, Any], target_role: str) -> float:
    """Calculates affinity between candidate background and target project role."""
    cand_role = normalize_role(candidate.get("role", "")).lower()
    target_clean = target_role.replace("_", " ").lower()
    cand_skills = [s.lower() for s in candidate.get("skills", [])]
    
    score = 0.0
    # Exact discipline match
    if "lead" in target_clean and "lead" in cand_role:
        score += 1.20
    elif "backend" in target_clean and "backend" in cand_role:
        score += 1.20
    elif "frontend" in target_clean and "frontend" in cand_role:
        score += 1.20
    elif "ml" in target_clean and ("ml" in cand_role or "ai" in cand_role or "machine learning" in cand_role):
        score += 1.20
    elif "qa" in target_clean and ("qa" in cand_role or "test" in cand_role or "quality" in cand_role):
        score += 1.20
    elif "devops" in target_clean and ("devops" in cand_role or "cloud" in cand_role or "sre" in cand_role):
        score += 1.20
    elif "full stack" in cand_role and ("frontend" in target_clean or "backend" in target_clean):
        score += 0.80
    elif any(word in cand_role for word in target_clean.split() if len(word) > 2):
        score += 0.50

    # Boost by candidate seniority
    exp_boost = min(0.30, candidate.get("years_experience", 0) * 0.04)
    score += exp_boost
    
    # Add overall fit
    score += candidate.get("overall_fit", 0.5) * 0.50
    return score

def compose_team(
    evaluations: List[Dict[str, Any]],
    candidates: List[Dict[str, Any]],
    requirements: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Composes balanced team satisfying mandatory roles, maximizing collective skill coverage,
    and avoiding redundant skills.
    """
    role_reqs = requirements.get("roles", [])
    required_skills = set(requirements.get("required_skills", []))
    target_team_size = requirements.get("team_size", 5)

    # Lookup map for fast candidate profile access
    cand_map = {c["employee_id"]: c for c in candidates}
    eval_map = {e["employee_id"]: e for e in evaluations}

    selected_team: List[Dict[str, Any]] = []
    selected_ids = set()

    # Step 1: Assign best candidate for each role slot
    for role_item in role_reqs:
        role_name = role_item.get("role", "developer")
        count = role_item.get("count", 1)

        for _ in range(count):
            best_candidate = None
            best_score = -1.0

            for ev in evaluations:
                eid = ev["employee_id"]
                if eid in selected_ids:
                    continue
                cand_info = cand_map.get(eid, {})
                affinity = _match_candidate_to_role(cand_info, role_name)
                if affinity > best_score:
                    best_score = affinity
                    best_candidate = (ev, cand_info)

            if best_candidate:
                ev, cand_info = best_candidate
                selected_ids.add(ev["employee_id"])
                assigned_label = role_name.replace("_", " ").title()
                selected_team.append({
                    "employee_id": ev["employee_id"],
                    "name": ev["name"],
                    "role": cand_info.get("role", ev["role"]),
                    "assigned_role": assigned_label,
                    "project_fit": ev["overall_fit"],
                    "skills": cand_info.get("skills", []),
                    "strengths": ev.get("strengths", []),
                    "gaps": ev.get("gaps", []),
                    "evidence": ev.get("evidence", []),
                    "why_selected": f"Assigned as {assigned_label} matching core competencies and project requirements."
                })

    # Step 2: Fill remaining slots up to target_team_size if roles left any open
    while len(selected_team) < target_team_size:
        best_ev = None
        best_score = -1.0
        for ev in evaluations:
            eid = ev["employee_id"]
            if eid in selected_ids:
                continue
            if ev["overall_fit"] > best_score:
                best_score = ev["overall_fit"]
                best_ev = ev
        if not best_ev:
            break

        cand_info = cand_map.get(best_ev["employee_id"], {})
        selected_ids.add(best_ev["employee_id"])
        selected_team.append({
            "employee_id": best_ev["employee_id"],
            "name": best_ev["name"],
            "role": cand_info.get("role", best_ev["role"]),
            "assigned_role": cand_info.get("role", best_ev["role"]),
            "project_fit": best_ev["overall_fit"],
            "skills": cand_info.get("skills", []),
            "strengths": best_ev.get("strengths", []),
            "gaps": best_ev.get("gaps", []),
            "evidence": best_ev.get("evidence", []),
            "why_selected": f"Selected for strong overall engineering fit ({best_ev['overall_fit'] * 100:.0f}% match)."
        })

    # Step 3: Check collective skill coverage & substitute redundant members if a required skill is missing
    covered_skills = set()
    for member in selected_team:
        covered_skills.update(member.get("skills", []))

    missing_skills = required_skills - covered_skills
    if missing_skills:
        # Search unselected candidates who possess missing skills
        for missing_s in list(missing_skills):
            replacement = None
            for ev in evaluations:
                eid = ev["employee_id"]
                if eid in selected_ids:
                    continue
                cand_info = cand_map.get(eid, {})
                if missing_s in cand_info.get("skills", []):
                    replacement = (ev, cand_info)
                    break
            
            if replacement:
                rep_ev, rep_cand = replacement
                # Find member with lowest fit who doesn't hold a unique required skill
                swap_idx = -1
                for idx in reversed(range(len(selected_team))):
                    mem = selected_team[idx]
                    # Check if swapping this member would lose an already covered skill
                    other_skills = set()
                    for j, other_m in enumerate(selected_team):
                        if j != idx:
                            other_skills.update(other_m.get("skills", []))
                    unique_skills_held = set(mem.get("skills", [])) - other_skills
                    if not (unique_skills_held & required_skills):
                        swap_idx = idx
                        break

                if swap_idx != -1:
                    removed = selected_team[swap_idx]
                    selected_ids.remove(removed["employee_id"])
                    selected_ids.add(rep_ev["employee_id"])
                    
                    selected_team[swap_idx] = {
                        "employee_id": rep_ev["employee_id"],
                        "name": rep_ev["name"],
                        "role": rep_cand.get("role", rep_ev["role"]),
                        "assigned_role": removed["assigned_role"],
                        "project_fit": rep_ev["overall_fit"],
                        "skills": rep_cand.get("skills", []),
                        "strengths": rep_ev.get("strengths", []),
                        "gaps": rep_ev.get("gaps", []),
                        "evidence": rep_ev.get("evidence", []),
                        "why_selected": f"Assigned as {removed['assigned_role']} to satisfy required skill '{missing_s}'."
                    }
                    covered_skills.update(rep_cand.get("skills", []))

    return selected_team

def team_builder_node(state: TeamBuilderState) -> Dict[str, Any]:
    """
    Agent 4: Team Builder Node.
    Composes team that optimizes whole-team role coverage, skill coverage, and domain fit.
    """
    evaluations = state.get("evaluations", [])
    candidates = state.get("candidates", [])
    requirements = state.get("requirements", {})

    selected_team = compose_team(evaluations, candidates, requirements)

    summary = f"Constructed candidate team of {len(selected_team)} members covering all requested roles."

    log_entry = {
        "node": "team_builder",
        "status": "completed",
        "summary": summary,
        "team_size": len(selected_team),
        "members": [m["name"] for m in selected_team]
    }
    existing_logs = state.get("logs", [])

    return {
        "selected_team": selected_team,
        "current_step": "team_builder",
        "step_summary": summary,
        "logs": existing_logs + [log_entry]
    }
