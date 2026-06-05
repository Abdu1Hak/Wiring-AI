from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.schemas.ai_planner_schema import AIPlannerResponse
from app.schemas.validation_schema import ValidateAIPlanRequest, ValidateAIPlanResponse
from app.services.backend_plan_validator_service import validate_connections

router = APIRouter(prefix="/api/wiring", tags=["wiring"])


@router.post("/validate-ai-plan", response_model=ValidateAIPlanResponse)
def validate_ai_plan_endpoint(
    request: ValidateAIPlanRequest,
    session: Session = Depends(get_session),
):
    errors, warnings = validate_connections(
        session=session,
        selected_component_ids=request.selectedComponentIds,
        connections=request.connections,
    )
    return ValidateAIPlanResponse(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
