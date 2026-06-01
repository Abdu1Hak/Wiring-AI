"""
- Check bad circuits 
"""

from app.models import ComponentDef, WiringConnection


POWER_TYPES = ["power_out", "power_in"]
GROUND_TYPES = ["ground"]

SIGNAL_TYPES = [
    "signal",
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
    "pwm",
    "pwm_io",
    "pwm_input",
    "pwm_output",
    "i2c",
    "i2c_sda",
    "i2c_scl",
    "spi",
    "uart",
]


def get_pin(component: ComponentDef, pin_id: str):
    for pin in component.pins:
        if pin.id == pin_id:
            return pin

    return None



def validate_netlist(
    selected_components: list[ComponentDef],
    connections: list[WiringConnection],
) -> list[str]:
    warnings: list[str] = []

    component_ids = [component.id for component in selected_components]
    component_map = {component.id: component for component in selected_components}

    if "arduino_uno" not in component_ids:
        warnings.append("Most beginner circuits need a controller like Arduino Uno.")

    if "led" in component_ids and "resistor" not in component_ids:
        warnings.append("LED selected without a resistor. Add a resistor to avoid damaging the LED.")

    if len(connections) == 0:
        warnings.append("No connections were generated.")

    used_arduino_pins: dict[str, int] = {}

    for connection in connections:
        endpoints = [
            (connection.from_component, connection.from_pin),
            (connection.to_component, connection.to_pin),
        ]

        for component_id, pin_id in endpoints:
            component = component_map.get(component_id)

            if not component:
                warnings.append(
                    f"Connection references missing component: {component_id}."
                )
                continue

            pin = get_pin(component, pin_id)

            if not pin:
                warnings.append(
                    f"Connection references missing pin: {component.name}.{pin_id}."
                )
                continue

            if component_id == "arduino_uno":
                used_arduino_pins[pin_id] = used_arduino_pins.get(pin_id, 0) + 1

    for pin_id, count in used_arduino_pins.items():
        if count > 1 and not pin_id.startswith("gnd"):
            warnings.append(
                f"Arduino pin {pin_id.upper()} is used {count} times. This may cause a conflict."
            )

    for connection in connections:
        from_component = component_map.get(connection.from_component)
        to_component = component_map.get(connection.to_component)

        if not from_component or not to_component:
            continue

        from_pin = get_pin(from_component, connection.from_pin)
        to_pin = get_pin(to_component, connection.to_pin)

        if not from_pin or not to_pin:
            continue

        bad_power_to_signal = (
            from_pin.type in POWER_TYPES
            and to_pin.type in SIGNAL_TYPES
        )

        bad_signal_to_power = (
            from_pin.type in SIGNAL_TYPES
            and to_pin.type in POWER_TYPES
        )

        if bad_power_to_signal or bad_signal_to_power:
            warnings.append(
                f"Possible invalid connection: {from_component.name} {from_pin.label} to {to_component.name} {to_pin.label}."
            )

    has_ground_connection = any(
        connection.type == "ground"
        or connection.from_pin.startswith("gnd")
        or connection.to_pin.startswith("gnd")
        for connection in connections
    )

    if selected_components and not has_ground_connection:
        warnings.append("No ground connection found. Most circuits require a shared GND.")

    return warnings