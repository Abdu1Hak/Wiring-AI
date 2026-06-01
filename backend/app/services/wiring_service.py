"""
- Reading Wiring_Rules.json and generate a netlist
"""

import json
from pathlib import Path

from app.models import WiringConnection, WiringRule


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WIRING_RULES_PATH = DATA_DIR / "wiring_rules.json"


def _load_json(path: Path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_endpoint(endpoint):
    """
    Supports either:
    "arduino_uno.5v"
    or:
    { "component": "arduino_uno", "pin": "5v" }
    """
    if isinstance(endpoint, str):
        component, pin = endpoint.split(".", 1)
        return component, pin

    if isinstance(endpoint, dict):
        return endpoint["component"], endpoint["pin"]

    raise ValueError(f"Invalid endpoint format: {endpoint}")


def normalize_connection(raw_connection: dict) -> WiringConnection:
    from_component, from_pin = parse_endpoint(raw_connection["from"])
    to_component, to_pin = parse_endpoint(raw_connection["to"])

    return WiringConnection(
        from_component=from_component,
        from_pin=from_pin,
        to_component=to_component,
        to_pin=to_pin,
        type=raw_connection.get("type", "signal"),
        label=raw_connection.get("label"),
    )


def load_wiring_rules() -> list[WiringRule]:
    raw = _load_json(WIRING_RULES_PATH)

    # Supports either:
    # [ {...}, {...} ]
    # or:
    # { "rules": [ {...}, {...} ] }
    rule_list = raw["rules"] if isinstance(raw, dict) and "rules" in raw else raw

    rules: list[WiringRule] = []

    for raw_rule in rule_list:
        connections = [
            normalize_connection(connection)
            for connection in raw_rule.get("connections", [])
        ]

        rules.append(
            WiringRule(
                id=raw_rule["id"],
                requires=raw_rule["requires"],
                connections=connections,
            )
        )

    return rules


def generate_connections(selected_component_ids: list[str]) -> tuple[list[WiringConnection], list[str]]:
    selected_set = set(selected_component_ids)
    rules = load_wiring_rules()

    connections: list[WiringConnection] = []
    warnings: list[str] = []

    matched_any_rule = False

    for rule in rules:
        required_set = set(rule.requires)

        if required_set.issubset(selected_set):
            matched_any_rule = True
            connections.extend(rule.connections)

    if not matched_any_rule:
        warnings.append("No wiring rule exists yet for this exact component combination.")

    return connections, warnings