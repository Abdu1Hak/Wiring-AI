from typing import Any

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str
    type: str
    position: dict[str, float]
    data: dict[str, Any]


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: str
    targetHandle: str
    label: str = ""
    type: str = "smoothstep"
    data: dict[str, Any] = Field(default_factory=dict)


class ReactFlowGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
