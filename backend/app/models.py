from pydantic import BaseModel
from typing import Any, Literal


PinType = Literal[
    "power_out",
    "power_in",
    "ground",
    "digital_io",
    "digital_input",
    "digital_output",
    "digital_in",
    "digital_out",
    "analog",
    "analog_io",
    "analog_input",
    "analog_output",
    "analog_in",
    "analog_out",
    "signal",
    "passive",
]

class Pin(BaseModel):
    id: str
    label: str
    type: str
    voltage: float | None = None


class ComponentDef(BaseModel):
    id: str
    name: str
    aliases: list[str] = []
    category: str
    pins: list[Pin]
    layout: dict[str, list[str]] | None = None


class WiringConnection(BaseModel):
    from_component: str
    from_pin: str
    to_component: str
    to_pin: str
    type: str = "signal"
    label: str | None = None


class WiringRule(BaseModel):
    id: str
    requires: list[str]
    connections: list[WiringConnection]


class WiringRequest(BaseModel):
    components: list[str]


class ParseRequest(BaseModel):
    text: str


class ComponentMatch(BaseModel):
    input: str
    matched_component_id: str
    name: str
    confidence: float


class ParseResponse(BaseModel):
    matches: list[ComponentMatch]
    unmatched: list[str]


class FlowNode(BaseModel):
    id: str
    type: str
    position: dict[str, int]
    data: dict[str, Any]


class FlowEdge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: str
    targetHandle: str
    label: str | None = None
    type: str = "smoothstep"
    data: dict[str, Any] = {}


class NetlistResponse(BaseModel):
    selected_components: list[ComponentDef]
    connections: list[WiringConnection]
    warnings: list[str]
    steps: list[str]
    react_flow: dict[str, list[dict[str, Any]]]