# routers/team_builder.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.team import TeamBuildRequest, TeamResult
from app.schemas.project import ProjectRequirement
from app.services.team_service import execute_team_build, execute_team_build_stream
from app.agents.project_analyzer import project_analyzer_node

router = APIRouter(prefix="/team-builder", tags=["Team Builder"])

@router.post("/analyze", response_model=ProjectRequirement)
def analyze_project(request: TeamBuildRequest):
    """
    Agent 1 (Standalone): Analyzes project description and returns structured requirements
    including required roles, counts, mandatory skills, and domain.
    """
    if not request.project_description.strip():
        raise HTTPException(status_code=400, detail="Project description cannot be empty")

    state = {
        "project_description": request.project_description,
        "target_team_size": request.team_size,
        "logs": []
    }
    result = project_analyzer_node(state)
    return result.get("requirements", {})

@router.post("/run", response_model=TeamResult)
def build_team_synchronous(request: TeamBuildRequest):
    """
    Executes the full LangGraph Agentic Pipeline synchronously:
    Analyzer -> Retriever -> Evaluator -> Builder -> Validator -> Explanation
    """
    if not request.project_description.strip():
        raise HTTPException(status_code=400, detail="Project description cannot be empty")

    try:
        return execute_team_build(
            project_description=request.project_description,
            team_size=request.team_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Team builder workflow failed: {str(e)}")

@router.post("/stream-run")
async def build_team_stream(request: TeamBuildRequest):
    """
    Executes the Agentic Pipeline with Server-Sent Events (SSE) streaming.
    Streams real-time step notifications as each LangGraph agent executes.
    """
    if not request.project_description.strip():
        raise HTTPException(status_code=400, detail="Project description cannot be empty")

    generator = execute_team_build_stream(
        project_description=request.project_description,
        team_size=request.team_size
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
