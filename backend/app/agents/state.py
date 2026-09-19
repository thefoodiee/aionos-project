# agents/state.py
from typing import TypedDict, List, Dict, Any, Optional

class TeamBuilderState(TypedDict):
    # Inputs
    project_description: str
    target_team_size: Optional[int]

    # Agent 1 outputs
    requirements: Dict[str, Any]

    # Agent 2 outputs
    candidates: List[Dict[str, Any]]

    # Agent 3 outputs
    evaluations: List[Dict[str, Any]]

    # Agent 4 outputs
    selected_team: List[Dict[str, Any]]

    # Agent 5 outputs
    validation: Dict[str, Any]
    iteration: int

    # Agent 6 outputs
    final_explanation: Dict[str, Any]

    # Workflow tracing and real-time streaming
    current_step: str
    step_summary: str
    logs: List[Dict[str, Any]]
    feasible: bool
