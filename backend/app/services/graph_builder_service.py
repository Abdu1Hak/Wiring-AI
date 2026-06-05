from sqlmodel import Session, select

from app.models import Component, ComponentPin
from app.schemas.ai_planner_schema import AIConnection
from app.schemas.graph_schema import GraphEdge, GraphNode, ReactFlowGraph


def node_id_for_component(component_id: str) -> str:
    return f"node_{component_id}"


def build_graph(
    session: Session,
    component_ids: list[str],
    connections: list[AIConnection],
) -> ReactFlowGraph:
    components = {
        c.id: c
        for c in session.exec(select(Component)).all()
        if c.id in component_ids
    }

    nodes: list[GraphNode] = []
    x_offset = 0
    for index, component_id in enumerate(component_ids):
        component = components.get(component_id)
        if not component:
            continue

        pin_rows = session.exec(
            select(ComponentPin).where(ComponentPin.component_id == component_id)
        ).all()

        nodes.append(
            GraphNode(
                id=node_id_for_component(component_id),
                type=component.frontend_node_type,
                position={"x": x_offset + (index % 3) * 320, "y": (index // 3) * 220},
                data={
                    "componentId": component.id,
                    "label": component.name,
                    "category": component.category,
                    "pins": [
                        {
                            "pinId": p.pin_id,
                            "label": p.label,
                            "handleId": p.react_flow_handle_id,
                            "pinType": p.pin_type,
                            "position": p.position,
                            "direction": p.direction,
                        }
                        for p in pin_rows
                    ],
                },
            )
        )

    edges: list[GraphEdge] = []
    for connection in connections:
        source_component = connection.fromComponentId
        target_component = connection.toComponentId
        source_pin = session.exec(
            select(ComponentPin).where(
                ComponentPin.component_id == source_component,
                ComponentPin.pin_id == connection.fromPinId,
            )
        ).first()
        target_pin = session.exec(
            select(ComponentPin).where(
                ComponentPin.component_id == target_component,
                ComponentPin.pin_id == connection.toPinId,
            )
        ).first()
        if not source_pin or not target_pin:
            continue

        edges.append(
            GraphEdge(
                id=f"edge_{connection.id}",
                source=node_id_for_component(source_component),
                target=node_id_for_component(target_component),
                sourceHandle=source_pin.react_flow_handle_id,
                targetHandle=target_pin.react_flow_handle_id,
                label=f"{source_pin.label} → {target_pin.label}",
                type="smoothstep",
                data={
                    "connectionType": connection.connectionType,
                    "wireColor": connection.wireColor,
                    "purpose": connection.purpose,
                    "safetyNote": connection.safetyNote,
                },
            )
        )

    return ReactFlowGraph(nodes=nodes, edges=edges)
