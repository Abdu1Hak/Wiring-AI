"""
- Converts netlist to beginner steps
"""

from app.models import ComponentDef, WiringConnection


def get_component_name(component_map: dict[str, ComponentDef], component_id: str) -> str:
    component = component_map.get(component_id)
    return component.name if component else component_id


def get_pin_label(component_map: dict[str, ComponentDef], component_id: str, pin_id: str) -> str:
    component = component_map.get(component_id)

    if not component:
        return pin_id

    for pin in component.pins:
        if pin.id == pin_id:
            return pin.label

    return pin_id


def generate_steps(
    selected_components: list[ComponentDef],
    connections: list[WiringConnection],
) -> list[str]:
    component_map = {component.id: component for component in selected_components}
    steps: list[str] = []

    for index, connection in enumerate(connections, start=1):
        from_component = get_component_name(component_map, connection.from_component)
        to_component = get_component_name(component_map, connection.to_component)

        from_pin = get_pin_label(
            component_map,
            connection.from_component,
            connection.from_pin,
        )
        to_pin = get_pin_label(
            component_map,
            connection.to_component,
            connection.to_pin,
        )

        steps.append(
            f"{index}. Connect {from_component} {from_pin} to {to_component} {to_pin}."
        )

    return steps