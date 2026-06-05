from sqlmodel import Session, select

from app.models import Component, ComponentPin
from app.schemas.ai_planner_schema import AIConnection, AIPlannerResponse
from app.schemas.validation_schema import ValidationErrorItem

ALLOWED_CONNECTION_TYPES = {
    "power_5v",
    "power_33v",
    "power_vin",
    "ground",
    "digital_signal",
    "analog_signal",
    "pwm_signal",
    "i2c_sda",
    "i2c_scl",
    "spi_mosi",
    "spi_miso",
    "spi_sck",
    "spi_cs",
    "uart_tx_to_rx",
    "uart_rx_to_tx",
    "passive_series",
    "motor_output",
    "relay_control",
    "driver_input",
    "driver_output",
    "data_signal",
}

MOTOR_IDS = {"dc_motor_small", "vibration_motor", "stepper_28byj48"}
LED_IDS = {"led_red", "led_green", "led_blue", "rgb_led_common_cathode"}
RESISTOR_IDS = {"resistor_220", "resistor_330", "resistor_1k", "resistor_10k"}
DRIVER_IDS = {"l298n_motor_driver", "tb6612fng_motor_driver", "uln2003_driver", "mosfet_module"}


def validate_connections(
    session: Session,
    selected_component_ids: list[str],
    connections: list[AIConnection],
) -> tuple[list[ValidationErrorItem], list[ValidationErrorItem]]:
    errors: list[ValidationErrorItem] = []
    warnings: list[ValidationErrorItem] = []

    selected_set = set(selected_component_ids)
    pins_map: dict[str, dict[str, ComponentPin]] = {}
    for component_id in selected_set:
        rows = session.exec(
            select(ComponentPin).where(ComponentPin.component_id == component_id)
        ).all()
        pins_map[component_id] = {p.pin_id: p for p in rows}

    for connection in connections:
        for role, component_id, pin_id in (
            ("from", connection.fromComponentId, connection.fromPinId),
            ("to", connection.toComponentId, connection.toPinId),
        ):
            component = session.get(Component, component_id)
            if not component:
                errors.append(
                    ValidationErrorItem(
                        code="COMPONENT_NOT_FOUND",
                        message=f"Component {component_id} does not exist in catalog.",
                        connectionId=connection.id,
                    )
                )
                continue
            if component_id not in selected_set:
                warnings.append(
                    ValidationErrorItem(
                        code="COMPONENT_NOT_SELECTED",
                        message=f"Component {component_id} used in connection but not in selection.",
                        connectionId=connection.id,
                    )
                )
            pin = pins_map.get(component_id, {}).get(pin_id)
            if not pin:
                errors.append(
                    ValidationErrorItem(
                        code="PIN_NOT_FOUND",
                        message=f"Pin {pin_id} does not exist on {component.name}.",
                        connectionId=connection.id,
                    )
                )

        if connection.connectionType not in ALLOWED_CONNECTION_TYPES:
            errors.append(
                ValidationErrorItem(
                    code="INVALID_CONNECTION_TYPE",
                    message=f"Connection type {connection.connectionType} is not allowed.",
                    connectionId=connection.id,
                )
            )

    _validate_safety(selected_component_ids, connections, errors, warnings)
    return errors, warnings


def validate_ai_plan(
    session: Session,
    plan: AIPlannerResponse,
    selected_component_ids: list[str],
) -> tuple[bool, list[ValidationErrorItem], list[ValidationErrorItem]]:
    if plan.status in ("unsafe_blocked", "incompatible", "missing_required_components", "needs_more_info"):
        return False, [], []

    errors, warnings = validate_connections(session, selected_component_ids, plan.connections)

    step_conn_ids = {cid for step in plan.steps for cid in step.relatedConnectionIds}
    conn_ids = {c.id for c in plan.connections}
    for step in plan.steps:
        for cid in step.relatedConnectionIds:
            if cid not in conn_ids:
                errors.append(
                    ValidationErrorItem(
                        code="STEP_REFERENCE_INVALID",
                        message=f"Step {step.stepNumber} references unknown connection {cid}.",
                    )
                )

    for cid in conn_ids - step_conn_ids:
        warnings.append(
            ValidationErrorItem(
                code="STEP_MISSING_CONNECTION",
                message=f"Connection {cid} has no related wiring step.",
            )
        )

    return len(errors) == 0, errors, warnings


def _validate_safety(
    selected_ids: list[str],
    connections: list[AIConnection],
    errors: list[ValidationErrorItem],
    warnings: list[ValidationErrorItem],
) -> None:
    selected = set(selected_ids)

    has_led = bool(selected & LED_IDS)
    has_resistor = bool(selected & RESISTOR_IDS)
    if has_led and not has_resistor:
        led_in_connections = any(
            c.fromComponentId in LED_IDS or c.toComponentId in LED_IDS for c in connections
        )
        if led_in_connections:
            errors.append(
                ValidationErrorItem(
                    code="LED_WITHOUT_RESISTOR",
                    message="LED wiring requires a current-limiting resistor in the selection.",
                )
            )

    has_motor = bool(selected & MOTOR_IDS)
    has_driver = bool(selected & DRIVER_IDS)
    if has_motor and not has_driver and connections:
        direct_motor = any(
            (c.fromComponentId in MOTOR_IDS or c.toComponentId in MOTOR_IDS)
            and "arduino" in c.fromComponentId + c.toComponentId
            for c in connections
        )
        if direct_motor:
            errors.append(
                ValidationErrorItem(
                    code="MOTOR_WITHOUT_DRIVER",
                    message="Motors must not connect directly to microcontroller pins.",
                )
            )

    if "arduino_uno" in selected and "esp32_devkit" in selected:
        warnings.append(
            ValidationErrorItem(
                code="LOGIC_VOLTAGE_MISMATCH",
                message="Mixing 5V Arduino with 3.3V ESP32 may require a logic level shifter.",
            )
        )
