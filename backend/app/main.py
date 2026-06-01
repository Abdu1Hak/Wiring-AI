from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import NetlistResponse, ParseRequest, ParseResponse, WiringRequest
from app.services.component_service import (
    get_all_components,
    get_components_by_ids,
    parse_components_from_text,
)
from app.services.flow_service import build_react_flow
from app.services.step_service import generate_steps
from app.services.validation_service import validate_netlist
from app.services.wiring_service import generate_connections


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/components")
def get_components():
    components = get_all_components()

    return {
        "components": [component.model_dump() for component in components]
    }


@app.post("/components/parse", response_model=ParseResponse)
def parse_components(request: ParseRequest):
    matches, unmatched = parse_components_from_text(request.text)

    return ParseResponse(matches=matches, unmatched=unmatched)


@app.post("/wiring/generate", response_model=NetlistResponse)
def generate_wiring(request: WiringRequest):
    try:
        selected_components = get_components_by_ids(request.components)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    connections, rule_warnings = generate_connections(request.components)

    validation_warnings = validate_netlist(
        selected_components=selected_components,
        connections=connections,
    )

    steps = generate_steps(
        selected_components=selected_components,
        connections=connections,
    )

    react_flow = build_react_flow(
        selected_components=selected_components,
        connections=connections,
    )

    warnings = rule_warnings + validation_warnings

    return NetlistResponse(
        selected_components=selected_components,
        connections=connections,
        warnings=warnings,
        steps=steps,
        react_flow=react_flow,
    )