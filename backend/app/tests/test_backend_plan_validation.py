from sqlmodel import Session

from app.schemas.ai_planner_schema import AIConnection
from app.services.backend_plan_validator_service import validate_connections

def test_pin_not_found(session: Session):
    errors, _ = validate_connections(
        session,
        ["arduino_uno", "hc_sr04"],
        [
            AIConnection(
                id="conn_bad",
                fromComponentId="arduino_uno",
                fromPinId="d99",
                toComponentId="hc_sr04",
                toPinId="trig",
                connectionType="digital_signal",
                wireColor="blue",
                purpose="bad pin",
            )
        ],
    )
    assert any(e.code == "PIN_NOT_FOUND" for e in errors)


def test_valid_ultrasonic_connection(session: Session):
    errors, _ = validate_connections(
        session,
        ["arduino_uno", "hc_sr04"],
        [
            AIConnection(
                id="conn_1",
                fromComponentId="arduino_uno",
                fromPinId="d9",
                toComponentId="hc_sr04",
                toPinId="trig",
                connectionType="digital_signal",
                wireColor="blue",
                purpose="Trigger",
            )
        ],
    )
    assert errors == []
