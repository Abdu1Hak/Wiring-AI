from sqlmodel import Session, select

from app.models import CompatibilityRule, Component, ComponentPin
from app.schemas.component_schema import ComponentDetail, ComponentSummary, PinSummary


def list_components(session: Session) -> list[ComponentSummary]:
    components = session.exec(
        select(Component).where(Component.is_active == True).order_by(Component.name)
    ).all()
    return [
        ComponentSummary(
            id=c.id,
            name=c.name,
            category=c.category,
            frontendNodeType=c.frontend_node_type,
        )
        for c in components
    ]


def get_component_detail(session: Session, component_id: str) -> ComponentDetail | None:
    component = session.get(Component, component_id)
    if not component or not component.is_active:
        return None

    pin_rows = session.exec(
        select(ComponentPin).where(ComponentPin.component_id == component_id)
    ).all()

    return ComponentDetail(
        id=component.id,
        name=component.name,
        category=component.category,
        description=component.description,
        frontendNodeType=component.frontend_node_type,
        logicVoltage=component.logic_voltage,
        voltageMin=component.voltage_min,
        voltageMax=component.voltage_max,
        protocols=component.communication_protocols or [],
        safetyLevel=component.safety_level,
        pins=[
            PinSummary(
                pinId=p.pin_id,
                label=p.label,
                pinType=p.pin_type,
                reactFlowHandleId=p.react_flow_handle_id,
            )
            for p in pin_rows
        ],
    )


def get_components_context(session: Session, component_ids: list[str]) -> list[dict]:
    context = []
    for component_id in component_ids:
        detail = get_component_detail(session, component_id)
        if not detail:
            continue
        context.append(
            {
                "id": detail.id,
                "name": detail.name,
                "category": detail.category,
                "logicVoltage": detail.logicVoltage,
                "voltageMin": detail.voltageMin,
                "voltageMax": detail.voltageMax,
                "protocols": detail.protocols,
                "safetyLevel": detail.safetyLevel,
                "pins": [
                    {
                        "pinId": p.pinId,
                        "label": p.label,
                        "pinType": p.pinType,
                        "reactFlowHandleId": p.reactFlowHandleId,
                    }
                    for p in detail.pins
                ],
            }
        )
    return context


def get_catalog_summary(session: Session, limit: int = 30) -> list[dict]:
    components = session.exec(select(Component).where(Component.is_active == True)).all()[:limit]
    return [{"id": c.id, "name": c.name, "category": c.category} for c in components]


def get_known_rules(session: Session) -> list[dict]:
    rules = session.exec(select(CompatibilityRule)).all()
    return [{"rule": r.message, "blocking": r.blocking} for r in rules]


def load_pins_map(session: Session, component_ids: list[str]) -> dict[str, dict[str, ComponentPin]]:
    result: dict[str, dict[str, ComponentPin]] = {}
    for component_id in component_ids:
        pins = session.exec(
            select(ComponentPin).where(ComponentPin.component_id == component_id)
        ).all()
        result[component_id] = {p.pin_id: p for p in pins}
    return result
