from app.models import ComponentDef, FlowEdge, FlowNode, WiringConnection


def create_node(component: ComponentDef, index: int) -> FlowNode:
    positions = {
        "arduino_uno": {"x": 40, "y": 80},
        "hc_sr04": {"x": 680, "y": 170},
        "resistor": {"x": 610, "y": 470},
        "led": {"x": 930, "y": 470},
        "buzzer": {"x": 680, "y": 360},
        "servo": {"x": 680, "y": 520},
        "push_button": {"x": 680, "y": 520},
        "potentiometer": {"x": 680, "y": 520},
        "dht11": {"x": 680, "y": 170},
        "breadboard": {"x": 440, "y": 520},
    }

    return FlowNode(
        id=component.id,
        type="componentNode",
        position=positions.get(
            component.id,
            {"x": 120 + index * 360, "y": 160},
        ),
        data={
            "componentId": component.id,
            "label": component.name,
            "category": component.category,
            "pins": [pin.model_dump() for pin in component.pins],
            "layout": component.layout,
        },
    )


def create_edge(connection: WiringConnection, index: int) -> FlowEdge:
    return FlowEdge(
        id=(
            f"{connection.from_component}-"
            f"{connection.from_pin}-"
            f"{connection.to_component}-"
            f"{connection.to_pin}-"
            f"{index}"
        ),
        source=connection.from_component,
        target=connection.to_component,
        sourceHandle=connection.from_pin,
        targetHandle=connection.to_pin,
        label=connection.label or connection.type.title(),
        type="smoothstep",
        data={
            "wireType": connection.type,
        },
    )


def build_react_flow(selected_components: list[ComponentDef], connections: list[WiringConnection]) -> dict[str, list[dict]]:
    nodes = [
        create_node(component, index)
        for index, component in enumerate(selected_components)
    ]

    edges = [
        create_edge(connection, index)
        for index, connection in enumerate(connections)
    ]

    return {
        "nodes": [node.model_dump() for node in nodes],
        "edges": [edge.model_dump() for edge in edges],
    }