from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.schemas.ai_planner_schema import AIPlannerResponse
from app.schemas.validation_schema import PlanRequest, RepairPlanRequest
from app.schemas.wiring_schema import PlanResponse
from app.services.ai_orchestrator_service import repair_plan, run_plan_pipeline

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest, session: Session = Depends(get_session)):
    return await run_plan_pipeline(
        session=session,
        project_description=request.projectDescription,
        selected_component_ids=request.selectedComponentIds,
    )


@router.post("/repair-plan", response_model=AIPlannerResponse)
async def repair_ai_plan(request: RepairPlanRequest, session: Session = Depends(get_session)):
    return await repair_plan(
        session=session,
        project_description=request.projectDescription,
        selected_component_ids=request.selectedComponentIds,
        previous_plan=request.previousAIPlan,
        validation_errors=request.validationErrors,
    )
