from pydantic import BaseModel, Field


class ComponentSummary(BaseModel):
    id: str
    name: str
    category: str
    frontendNodeType: str


class PinSummary(BaseModel):
    pinId: str
    label: str
    pinType: str
    reactFlowHandleId: str


class ComponentDetail(BaseModel):
    id: str
    name: str
    category: str
    description: str = ""
    frontendNodeType: str
    logicVoltage: float | None = None
    voltageMin: float | None = None
    voltageMax: float | None = None
    protocols: list[str] = Field(default_factory=list)
    safetyLevel: str = "safe_beginner"
    pins: list[PinSummary] = Field(default_factory=list)


class ComponentsListResponse(BaseModel):
    components: list[ComponentSummary]


class ComponentDetailResponse(BaseModel):
    component: ComponentDetail
