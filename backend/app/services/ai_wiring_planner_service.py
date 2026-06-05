import json
import re
from typing import Any

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.schemas.ai_planner_schema import (
    AIConnection,
    AIPlannerResponse,
    AIStep,
    CompatibilityFinding,
)

SYSTEM_PROMPT = """You are Wiring AI, an electronics wiring planner for beginner low-voltage circuits.
You must analyze selected components, check compatibility, identify missing components, and propose pin-level wiring.
You may only use components and pins from the provided catalog context.
Return valid JSON only matching the AIPlannerResponse schema fields (camelCase keys).
Do not generate mains voltage, high-voltage, or unsafe circuits.
"""

UNSAFE_PATTERNS = re.compile(
    r"(wall\s*outlet|mains|120\s*v|220\s*v|240\s*v|house\s*power|ac\s*mains)",
    re.IGNORECASE,
)


def _has_unsafe_request(description: str) -> bool:
    return bool(UNSAFE_PATTERNS.search(description))


def _has_led_without_resistor(selected: set[str]) -> bool:
    leds = {"led_red", "led_green", "led_blue", "rgb_led_common_cathode"}
    resistors = {"resistor_220", "resistor_330", "resistor_1k", "resistor_10k"}
    return bool(selected & leds) and not (selected & resistors)


def _has_motor_without_driver(selected: set[str]) -> bool:
    motors = {"dc_motor_small", "vibration_motor", "stepper_28byj48"}
    drivers = {"l298n_motor_driver", "tb6612fng_motor_driver", "uln2003_driver"}
    return bool(selected & motors) and not (selected & drivers)


def _mock_plan(
    project_description: str,
    selected_component_ids: list[str],
    catalog_context: list[dict],
) -> AIPlannerResponse:
    selected = set(selected_component_ids)

    if _has_unsafe_request(project_description):
        return AIPlannerResponse(
            status="unsafe_blocked",
            projectTitle="Unsafe request blocked",
            projectSummary="Mains or high-voltage wiring is not supported.",
            projectGoal=project_description,
            selectedComponentIds=selected_component_ids,
            compatibilityStatus="unsafe_blocked",
            compatibilityFindings=[
                CompatibilityFinding(
                    type="mains_voltage",
                    severity="blocking",
                    message=(
                        "This app does not support wall outlet or mains voltage wiring. "
                        "Only low-voltage beginner electronics are supported."
                    ),
                )
            ],
        )

    if _has_led_without_resistor(selected):
        return AIPlannerResponse(
            status="missing_required_components",
            projectTitle="Missing resistor",
            projectSummary="An LED needs a current-limiting resistor.",
            projectGoal=project_description,
            selectedComponentIds=selected_component_ids,
            compatibilityStatus="missing_required_components",
            compatibilityFindings=[
                CompatibilityFinding(
                    type="missing_resistor",
                    severity="blocking",
                    message="The LED requires a current-limiting resistor.",
                    affectedComponentIds=[c for c in selected if c.startswith("led_")],
                    recommendedComponentIds=["resistor_220", "resistor_330"],
                )
            ],
        )

    if _has_motor_without_driver(selected):
        return AIPlannerResponse(
            status="missing_required_components",
            projectTitle="Motor driver required",
            projectSummary="Motors need a driver module for safe wiring.",
            projectGoal=project_description,
            selectedComponentIds=selected_component_ids,
            compatibilityStatus="missing_required_components",
            compatibilityFindings=[
                CompatibilityFinding(
                    type="missing_motor_driver",
                    severity="blocking",
                    message=(
                        "A DC motor should not be connected directly to an Arduino pin. "
                        "Add a motor driver."
                    ),
                    affectedComponentIds=[c for c in selected if "motor" in c],
                    recommendedComponentIds=["l298n_motor_driver", "tb6612fng_motor_driver"],
                )
            ],
        )

    if "esp32_devkit" in selected and "hc_sr04" in selected:
        has_shifter = "logic_level_shifter" in selected
        if not has_shifter:
            return AIPlannerResponse(
                status="incompatible",
                projectTitle="Logic level caution",
                projectSummary="HC-SR04 ECHO is 5V; ESP32 GPIO is 3.3V.",
                projectGoal=project_description,
                selectedComponentIds=selected_component_ids,
                compatibilityStatus="incompatible",
                compatibilityFindings=[
                    CompatibilityFinding(
                        type="logic_voltage_mismatch",
                        severity="blocking",
                        message=(
                            "HC-SR04 ECHO outputs 5V which may damage ESP32 inputs. "
                            "Add a logic level shifter."
                        ),
                        affectedComponentIds=["esp32_devkit", "hc_sr04"],
                        recommendedComponentIds=["logic_level_shifter"],
                    )
                ],
            )

    controller = next((c for c in selected if c.startswith("arduino") or c == "esp32_devkit"), None)
    if not controller and selected:
        return AIPlannerResponse(
            status="needs_more_info",
            projectTitle="Controller needed",
            projectSummary="Select a microcontroller board to control the circuit.",
            projectGoal=project_description,
            selectedComponentIds=selected_component_ids,
            compatibilityStatus="needs_more_info",
            compatibilityFindings=[
                CompatibilityFinding(
                    type="missing_controller",
                    severity="blocking",
                    message="A controller board is required for this project.",
                    recommendedComponentIds=["arduino_uno", "esp32_devkit"],
                )
            ],
        )

    connections: list[AIConnection] = []
    steps: list[AIStep] = []
    assumptions = ["Circuit uses USB or board regulator power.", "Power off while wiring."]

    if controller == "arduino_uno" and "hc_sr04" in selected:
        connections.extend(
            [
                AIConnection(id="conn_1", fromComponentId="arduino_uno", fromPinId="5v", toComponentId="hc_sr04", toPinId="vcc", connectionType="power_5v", wireColor="red", purpose="Power ultrasonic sensor."),
                AIConnection(id="conn_2", fromComponentId="arduino_uno", fromPinId="gnd_1", toComponentId="hc_sr04", toPinId="gnd", connectionType="ground", wireColor="black", purpose="Common ground for sensor."),
                AIConnection(id="conn_3", fromComponentId="arduino_uno", fromPinId="d9", toComponentId="hc_sr04", toPinId="trig", connectionType="digital_signal", wireColor="blue", purpose="Trigger pulse to sensor."),
                AIConnection(id="conn_4", fromComponentId="hc_sr04", fromPinId="echo", toComponentId="arduino_uno", toPinId="d10", connectionType="digital_signal", wireColor="blue", purpose="Echo return to Arduino."),
            ]
        )
        steps.extend(
            [
                AIStep(stepNumber=1, title="Sensor power", instruction="Connect Arduino 5V to HC-SR04 VCC.", relatedConnectionIds=["conn_1"], safetyNote="Unplug USB while wiring."),
                AIStep(stepNumber=2, title="Sensor ground", instruction="Connect Arduino GND to HC-SR04 GND.", relatedConnectionIds=["conn_2"]),
                AIStep(stepNumber=3, title="Ultrasonic signals", instruction="Connect D9→TRIG and ECHO→D10.", relatedConnectionIds=["conn_3", "conn_4"]),
            ]
        )

    if controller == "arduino_uno" and "led_red" in selected and "resistor_220" in selected:
        base_step = len(steps)
        connections.extend(
            [
                AIConnection(id="conn_led_1", fromComponentId="arduino_uno", fromPinId="d3", toComponentId="resistor_220", toPinId="terminal_1", connectionType="digital_signal", wireColor="green", purpose="Drive LED through resistor."),
                AIConnection(id="conn_led_2", fromComponentId="resistor_220", fromPinId="terminal_2", toComponentId="led_red", toPinId="anode", connectionType="passive_series", wireColor="white", purpose="Current limit for LED."),
                AIConnection(id="conn_led_3", fromComponentId="led_red", fromPinId="cathode", toComponentId="arduino_uno", toPinId="gnd_2", connectionType="ground", wireColor="black", purpose="LED return path."),
            ]
        )
        steps.extend(
            [
                AIStep(stepNumber=base_step + 1, title="LED series resistor", instruction="Wire D3 → resistor → LED anode.", relatedConnectionIds=["conn_led_1", "conn_led_2"], safetyNote="Never connect LED directly without resistor."),
                AIStep(stepNumber=base_step + 2, title="LED ground", instruction="Connect LED cathode to GND.", relatedConnectionIds=["conn_led_3"]),
            ]
        )

    if controller == "arduino_uno" and "oled_i2c_096" in selected:
        connections.extend(
            [
                AIConnection(id="conn_oled_1", fromComponentId="arduino_uno", fromPinId="5v", toComponentId="oled_i2c_096", toPinId="vcc", connectionType="power_5v", wireColor="red", purpose="Power OLED."),
                AIConnection(id="conn_oled_2", fromComponentId="arduino_uno", fromPinId="gnd_1", toComponentId="oled_i2c_096", toPinId="gnd", connectionType="ground", wireColor="black", purpose="OLED ground."),
                AIConnection(id="conn_oled_3", fromComponentId="arduino_uno", fromPinId="a4", toComponentId="oled_i2c_096", toPinId="sda", connectionType="i2c_sda", wireColor="teal", purpose="I2C data."),
                AIConnection(id="conn_oled_4", fromComponentId="arduino_uno", fromPinId="a5", toComponentId="oled_i2c_096", toPinId="scl", connectionType="i2c_scl", wireColor="yellow", purpose="I2C clock."),
            ]
        )
        steps.append(
            AIStep(stepNumber=len(steps) + 1, title="OLED I2C", instruction="Connect 5V, GND, SDA (A4), SCL (A5).", relatedConnectionIds=["conn_oled_1", "conn_oled_2", "conn_oled_3", "conn_oled_4"])
        )

    if not connections:
        return AIPlannerResponse(
            status="needs_more_info",
            projectTitle="More detail needed",
            projectSummary="Could not infer a safe wiring pattern for this selection.",
            projectGoal=project_description,
            selectedComponentIds=selected_component_ids,
            compatibilityStatus="needs_more_info",
        )

    title = "Beginner wiring plan"
    if "hc_sr04" in selected and "led_red" in selected:
        title = "Arduino Distance Sensor LED Alert"
    elif "hc_sr04" in selected:
        title = "Arduino Ultrasonic Sensor"
    elif "oled_i2c_096" in selected:
        title = "Arduino OLED Display"

    return AIPlannerResponse(
        status="success",
        projectTitle=title,
        projectSummary=f"Wiring plan for: {project_description or 'selected components'}",
        projectGoal=project_description or "Wire selected beginner components safely.",
        selectedComponentIds=selected_component_ids,
        compatibilityStatus="compatible_with_warnings",
        compatibilityFindings=[
            CompatibilityFinding(
                type="safety_reminder",
                severity="warning",
                message="Power off the board while making connections.",
                affectedComponentIds=[controller] if controller else [],
            )
        ],
        assumptions=assumptions,
        connections=connections,
        steps=steps,
    )


async def call_openai_planner(
    project_description: str,
    catalog_context: dict[str, Any],
) -> AIPlannerResponse:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    user_prompt = f"""Project description:
{project_description}

Catalog context JSON:
{json.dumps(catalog_context)}

Return JSON matching AIPlannerResponse with camelCase keys."""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    return AIPlannerResponse.model_validate(data)


async def generate_wiring_plan(
    project_description: str,
    selected_component_ids: list[str],
    catalog_context: dict[str, Any],
) -> AIPlannerResponse:
    if OPENAI_API_KEY:
        try:
            return await call_openai_planner(project_description, catalog_context)
        except Exception:
            pass

    return _mock_plan(
        project_description,
        selected_component_ids,
        catalog_context.get("selectedComponents", []),
    )
