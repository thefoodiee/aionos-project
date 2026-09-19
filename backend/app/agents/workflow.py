# agents/workflow.py
import json
import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
from langgraph.graph import StateGraph, START, END

from .state import TeamBuilderState
from .project_analyzer import project_analyzer_node
from .candidate_retriever import candidate_retriever_node
from .candidate_evaluator import candidate_evaluator_node
from .team_builder import team_builder_node
from .team_validator import team_validator_node
from .explanation import explanation_node

def should_retry(state: TeamBuilderState) -> str:
    """
    Conditional routing function after Team Validator.
    If invalid and iteration <= 3, loops back to candidate_retriever.
    Otherwise, routes to explanation.
    """
    validation = state.get("validation", {})
    iteration = state.get("iteration", 1)
    is_valid = validation.get("valid", False)

    # Note: iteration was incremented in team_validator_node
    # So if iteration was 1, it became 2; if it was 2, it became 3.
    # We allow up to 2 retries (i.e. up to iteration <= 3)
    if not is_valid and iteration <= 3:
        return "candidate_retriever"
    return "explanation"

def build_team_builder_graph():
    """
    Assembles the LangGraph StateGraph workflow matching TASK.md specification.
    """
    workflow = StateGraph(TeamBuilderState)

    # 1. Register Nodes
    workflow.add_node("project_analyzer", project_analyzer_node)
    workflow.add_node("candidate_retriever", candidate_retriever_node)
    workflow.add_node("candidate_evaluator", candidate_evaluator_node)
    workflow.add_node("team_builder", team_builder_node)
    workflow.add_node("team_validator", team_validator_node)
    workflow.add_node("explanation", explanation_node)

    # 2. Register Edges
    workflow.add_edge(START, "project_analyzer")
    workflow.add_edge("project_analyzer", "candidate_retriever")
    workflow.add_edge("candidate_retriever", "candidate_evaluator")
    workflow.add_edge("candidate_evaluator", "team_builder")
    workflow.add_edge("team_builder", "team_validator")

    # 3. Register Conditional Edge from Validator
    workflow.add_conditional_edges(
        "team_validator",
        should_retry,
        {
            "candidate_retriever": "candidate_retriever",
            "explanation": "explanation"
        }
    )

    workflow.add_edge("explanation", END)

    return workflow.compile()

# Global compiled graph
team_builder_app = build_team_builder_graph()

def run_workflow(project_description: str, target_team_size: Optional[int] = None) -> Dict[str, Any]:
    """
    Executes the compiled LangGraph workflow synchronously.
    """
    initial_state: TeamBuilderState = {
        "project_description": project_description,
        "target_team_size": target_team_size,
        "requirements": {},
        "candidates": [],
        "evaluations": [],
        "selected_team": [],
        "validation": {},
        "iteration": 1,
        "final_explanation": {},
        "current_step": "start",
        "step_summary": "Initializing Team Builder Pipeline...",
        "logs": [],
        "feasible": True
    }

    final_state = team_builder_app.invoke(initial_state)
    return final_state

async def run_workflow_stream(
    project_description: str,
    target_team_size: Optional[int] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Streams workflow execution node-by-node for real-time frontend visualization.
    Yields step progress and state updates as Server-Sent Events.
    """
    state: TeamBuilderState = {
        "project_description": project_description,
        "target_team_size": target_team_size,
        "requirements": {},
        "candidates": [],
        "evaluations": [],
        "selected_team": [],
        "validation": {},
        "iteration": 1,
        "final_explanation": {},
        "current_step": "start",
        "step_summary": "Initializing Agentic Pipeline...",
        "logs": [],
        "feasible": True
    }

    yield {
        "event": "start",
        "node": "start",
        "message": "Starting Agentic AI Workflow",
        "state": state
    }
    await asyncio.sleep(0.05)

    # Execute Project Analyzer
    yield {"event": "node_start", "node": "project_analyzer", "message": "Analyzing project description & extracting structured roles..."}
    res = project_analyzer_node(state)
    state.update(res)
    yield {"event": "node_complete", "node": "project_analyzer", "summary": state["step_summary"], "data": state["requirements"]}
    await asyncio.sleep(0.05)

    # Retrieval and validation loop
    max_loops = 3
    while True:
        # Candidate Retriever
        yield {"event": "node_start", "node": "candidate_retriever", "message": f"Querying employee database via hybrid RAG (iteration {state.get('iteration', 1)})..."}
        res = candidate_retriever_node(state)
        state.update(res)
        yield {"event": "node_complete", "node": "candidate_retriever", "summary": state["step_summary"], "data": {"candidate_count": len(state["candidates"])}}
        await asyncio.sleep(0.05)

        # Candidate Evaluator
        yield {"event": "node_start", "node": "candidate_evaluator", "message": "Evaluating candidate profiles & grounded evidence against project requirements..."}
        res = candidate_evaluator_node(state)
        state.update(res)
        yield {"event": "node_complete", "node": "candidate_evaluator", "summary": state["step_summary"], "data": {"evaluation_count": len(state["evaluations"])}}
        await asyncio.sleep(0.05)

        # Team Builder
        yield {"event": "node_start", "node": "team_builder", "message": "Optimizing whole-team role coverage, skill synergy, and domain fit..."}
        res = team_builder_node(state)
        state.update(res)
        yield {"event": "node_complete", "node": "team_builder", "summary": state["step_summary"], "data": {"team_size": len(state["selected_team"])}}
        await asyncio.sleep(0.05)

        # Team Validator
        yield {"event": "node_start", "node": "team_validator", "message": "Validating team size, role fulfillment, and required skills..."}
        res = team_validator_node(state)
        state.update(res)
        is_valid = state["validation"].get("valid", False)
        yield {"event": "node_complete", "node": "team_validator", "summary": state["step_summary"], "data": state["validation"]}
        await asyncio.sleep(0.05)

        if is_valid or state.get("iteration", 1) > max_loops:
            break

        yield {
            "event": "node_retry",
            "node": "team_validator",
            "message": f"Constraints not yet fully satisfied. Looping back to retrieval (Attempt {state.get('iteration', 1)}/{max_loops})...",
            "missing": state["validation"].get("missing_requirements", [])
        }
        await asyncio.sleep(0.05)

    # Explanation Agent
    yield {"event": "node_start", "node": "explanation", "message": "Generating final evidence-backed justifications and skill coverage analysis..."}
    res = explanation_node(state)
    state.update(res)
    yield {"event": "node_complete", "node": "explanation", "summary": state["step_summary"], "data": state["final_explanation"]}
    await asyncio.sleep(0.05)

    yield {
        "event": "complete",
        "node": "end",
        "message": "Team Building Complete",
        "final_state": state
    }
