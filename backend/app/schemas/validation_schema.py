from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.ai_planner_schema import AIConnection


class ValidationErrorItem(BaseModel):
    code: str
    message: str
    connectionId: str | None = None


class ValidateAIPlanRequest(BaseModel):
    selectedComponentIds: list[str]
    connections: list[AIConnection]


class ValidateAIPlanResponse(BaseModel):
    valid: bool
    errors: list[ValidationErrorItem] = Field(default_factory=list)
    warnings: list[ValidationErrorItem] = Field(default_factory=list)


class RepairPlanRequest(BaseModel):
    projectDescription: str
    selectedComponentIds: list[str]
    previousAIPlan: dict
    validationErrors: list[ValidationErrorItem]


class PlanRequest(BaseModel):
    projectDescription: str
    selectedComponentIds: list[str]
    mode: str = "generate_wiring"
