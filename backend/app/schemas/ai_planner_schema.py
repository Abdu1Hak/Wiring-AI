from typing import Literal

from pydantic import BaseModel, Field


class CompatibilityFinding(BaseModel):
    type: str
    severity: Literal["info", "warning", "blocking"]
    message: str
    affectedComponentIds: list[str] = Field(default_factory=list)
    affectedPinIds: list[str] = Field(default_factory=list)
    recommendedComponentIds: list[str] = Field(default_factory=list)


class AIConnection(BaseModel):
    id: str
    fromComponentId: str
    fromPinId: str
    toComponentId: str
    toPinId: str
    connectionType: str
    wireColor: str
    purpose: str
    safetyNote: str | None = None


class AIStep(BaseModel):
    stepNumber: int
    title: str
    instruction: str
    relatedConnectionIds: list[str]
    safetyNote: str | None = None


class AIPlannerResponse(BaseModel):
    status: Literal[
        "success",
        "needs_more_info",
        "missing_required_components",
        "incompatible",
        "unsafe_blocked",
        "no_valid_plan",
    ]
    projectTitle: str = ""
    projectSummary: str = ""
    projectGoal: str = ""
    selectedComponentIds: list[str] = Field(default_factory=list)
    recommendedComponentIds: list[str] = Field(default_factory=list)
    compatibilityStatus: Literal[
        "compatible",
        "compatible_with_warnings",
        "missing_required_components",
        "incompatible",
        "unsafe_blocked",
        "needs_more_info",
    ] = "needs_more_info"
    compatibilityFindings: list[CompatibilityFinding] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    connections: list[AIConnection] = Field(default_factory=list)
    steps: list[AIStep] = Field(default_factory=list)
