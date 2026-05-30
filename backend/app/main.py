from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal

app = FastAPI()

app.add_middleware( # Middle ware is the code that runs before or after route executes 
    CORSMiddleware, # CORS (Cross-Origin Resource sharing: an origin is protocol+domain+port, CORSMiddleware will block cross-origin request by default unless allowed)
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # the origins allowed to send request to backends are explicitely stated here
    allow_credentials=True, # without it the frontend to backend communication cna lose cookie/session infromation 
    allow_methods=["*"], # All HTTPS methods like GET,POST,PUT,DELETE,PATCH are allowed
    allow_headers=["*"], # Headers are extra information send with request methods that are allowable by the browser
)

# define the structure of data the api expects and returns
# Pin type is a custom type, it will create a type constraint, these are beginner common pin types
PinType = Literal[
    "power_out",
    "power_in",
    "ground",
    "digital_io",
    "analog",
    "signal",
    "passive",
]
# Base Model is a Pydantic class that Pin will inherit from automatically giving you data validation, type checking, and json conversion
# in a regular class you would have to declare your class object/function within an init function, here pydnatic is doing the same thing by generating the constructor automatically
class Pin(BaseModel):
    id: str
    label: str
    type: PinType


class ComponentDef(BaseModel):
    id: str
    name: str
    category: str
    pins: list[Pin]


class WiringRequest(BaseModel):
    components: list[str]


class FlowNode(BaseModel):
    id: str
    type: str
    position: dict
    data: dict


class FlowEdge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: str
    targetHandle: str
    label: str | None = None
    type: str = "smoothstep"


class WiringResponse(BaseModel):
    nodes: list[FlowNode]
    edges: list[FlowEdge]
    warnings: list[str]


COMPONENTS: dict[str, ComponentDef] = {
    "arduino_uno": ComponentDef(
    id="arduino_uno",
    name="Arduino Uno",
    category="microcontroller",
    pins=[
        Pin(id="ioref", label="IOREF", type="power_out"),
        Pin(id="reset", label="RESET", type="signal"),
        Pin(id="3v3", label="3.3V", type="power_out"),
        Pin(id="5v", label="5V", type="power_out"),
        Pin(id="gnd_1", label="GND", type="ground"),
        Pin(id="gnd_2", label="GND", type="ground"),
        Pin(id="vin", label="VIN", type="power_in"),

        Pin(id="a0", label="A0", type="analog"),
        Pin(id="a1", label="A1", type="analog"),
        Pin(id="a2", label="A2", type="analog"),
        Pin(id="a3", label="A3", type="analog"),
        Pin(id="a4", label="A4 / SDA", type="analog"),
        Pin(id="a5", label="A5 / SCL", type="analog"),

        Pin(id="d0", label="D0 / RX", type="digital_io"),
        Pin(id="d1", label="D1 / TX", type="digital_io"),
        Pin(id="d2", label="D2", type="digital_io"),
        Pin(id="d3", label="D3 PWM", type="digital_io"),
        Pin(id="d4", label="D4", type="digital_io"),
        Pin(id="d5", label="D5 PWM", type="digital_io"),
        Pin(id="d6", label="D6 PWM", type="digital_io"),
        Pin(id="d7", label="D7", type="digital_io"),
        Pin(id="d8", label="D8", type="digital_io"),
        Pin(id="d9", label="D9 PWM", type="digital_io"),
        Pin(id="d10", label="D10 PWM", type="digital_io"),
        Pin(id="d11", label="D11 PWM", type="digital_io"),
        Pin(id="d12", label="D12", type="digital_io"),
        Pin(id="d13", label="D13", type="digital_io"),
        Pin(id="gnd_3", label="GND", type="ground"),
        Pin(id="aref", label="AREF", type="signal"),
        Pin(id="sda", label="SDA", type="signal"),
        Pin(id="scl", label="SCL", type="signal"),
        ],
    ),
    "hc_sr04": ComponentDef(
        id="hc_sr04",
        name="HC-SR04 Ultrasonic Sensor",
        category="sensor",
        pins=[
            Pin(id="vcc", label="VCC", type="power_in"),
            Pin(id="trig", label="TRIG", type="signal"),
            Pin(id="echo", label="ECHO", type="signal"),
            Pin(id="gnd", label="GND", type="ground"),
        ],
    ),
    "led": ComponentDef(
        id="led",
        name="LED",
        category="output",
        pins=[
            Pin(id="anode", label="Anode +", type="signal"),
            Pin(id="cathode", label="Cathode -", type="ground"),
        ],
    ),
    "resistor": ComponentDef(
        id="resistor",
        name="Resistor",
        category="passive",
        pins=[
            Pin(id="pin1", label="Pin 1", type="passive"),
            Pin(id="pin2", label="Pin 2", type="passive"),
        ],
    ),
}

# .modle_dump() is a pydnatic function that will turn a componentDef ictionary into a python dictionary
AVAILABLE_COMPONENTS = [
    component.model_dump() for component in COMPONENTS.values()
]


def create_node(component_id: str, index: int) -> FlowNode:
    component = COMPONENTS[component_id]

    positions = {
        "arduino_uno": {"x": 40, "y": 80},
        "hc_sr04": {"x": 680, "y": 170},
        "resistor": {"x": 610, "y": 470},
        "led": {"x": 930, "y": 470},
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
        },
    )

def make_edge(
    edge_id: str,
    source: str,
    source_handle: str,
    target: str,
    target_handle: str,
    label: str | None = None,
) -> FlowEdge:
    return FlowEdge(
        id=edge_id,
        source=source,
        target=target,
        sourceHandle=source_handle,
        targetHandle=target_handle,
        label=label,
    )


@app.get("/components")
def get_components():
    return {"components": AVAILABLE_COMPONENTS}


@app.post("/wiring/generate", response_model=WiringResponse)
def generate_wiring(request: WiringRequest):
    selected = request.components
    warnings: list[str] = []

    for component_id in selected:
        if component_id not in COMPONENTS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported component: {component_id}",
            )

    nodes = [
        create_node(component_id, index)
        for index, component_id in enumerate(selected)
    ]

    edges: list[FlowEdge] = []

    selected_set = set(selected)

    if "arduino_uno" not in selected_set:
        warnings.append("Most beginner circuits need a controller like Arduino Uno.")

    if {"arduino_uno", "hc_sr04"}.issubset(selected_set):
        edges.extend(
            [
                make_edge("hc-vcc-arduino-5v", "hc_sr04", "vcc", "arduino_uno", "5v", "Power"),
                make_edge("hc-gnd-arduino-gnd", "hc_sr04", "gnd", "arduino_uno", "gnd_1", "Ground"),
                make_edge("hc-trig-arduino-d9", "hc_sr04", "trig", "arduino_uno", "d9", "Trigger"),
                make_edge("hc-echo-arduino-d10", "hc_sr04", "echo", "arduino_uno", "d10", "Echo"),
            ]
        )

    if {"arduino_uno", "led"}.issubset(selected_set) and "resistor" not in selected_set:
        warnings.append("LED selected without a resistor. Add a resistor to avoid damaging the LED.")

    if {"arduino_uno", "led", "resistor"}.issubset(selected_set):
        edges.extend(
            [
                make_edge("arduino-d8-resistor", "arduino_uno", "d8", "resistor", "pin1", "Signal"),
                make_edge("resistor-led-anode", "resistor", "pin2", "led", "anode", "Current limit"),
                make_edge("led-cathode-gnd", "led", "cathode", "arduino_uno", "gnd", "Ground"),
            ]
        )

    if len(edges) == 0:
        warnings.append("No wiring rule exists yet for this exact component combination.")

    return WiringResponse(nodes=nodes, edges=edges, warnings=warnings)