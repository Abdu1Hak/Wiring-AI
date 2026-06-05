from pydantic import BaseModel, Field

from app.schemas.ai_planner_schema import AIConnection, AIStep, CompatibilityFinding
from app.schemas.graph_schema import ReactFlowGraph
from app.schemas.validation_schema import ValidationErrorItem


class PlanResponse(BaseModel):
    status: str
    projectTitle: str = ""
    projectSummary: str = ""
    aiPlanAccepted: bool = False
    compatibilityFindings: list[CompatibilityFinding] = Field(default_factory=list)
    graph: ReactFlowGraph = Field(default_factory=ReactFlowGraph)
    connections: list[AIConnection] = Field(default_factory=list)
    steps: list[AIStep] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    fallbackMessage: str | None = None
    validationErrors: list[ValidationErrorItem] = Field(default_factory=list)
