"""
loads components.json - searches for components and matches aliasis
"""

import json
import re
from pathlib import Path

from app.models import ComponentDef, ComponentMatch


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COMPONENTS_PATH = DATA_DIR / "components.json"


def _load_json(path: Path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_components() -> dict[str, ComponentDef]:
    raw = _load_json(COMPONENTS_PATH)

    # Supports either:
    # [ {...}, {...} ]
    # or:
    # { "components": [ {...}, {...} ] }
    component_list = raw["components"] if isinstance(raw, dict) and "components" in raw else raw

    components: dict[str, ComponentDef] = {}

    for item in component_list:
        component = ComponentDef(**item)
        components[component.id] = component

    return components


def get_all_components() -> list[ComponentDef]:
    return list(load_components().values())


def get_components_by_ids(component_ids: list[str]) -> list[ComponentDef]:
    components = load_components()

    selected: list[ComponentDef] = []

    for component_id in component_ids:
        if component_id not in components:
            raise ValueError(f"Unsupported component: {component_id}")

        selected.append(components[component_id])

    return selected


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def split_component_text(text: str) -> list[str]:
    cleaned = normalize_text(text)

    # Handles:
    # "arduino, ultrasonic sensor, led"
    # "arduino and ultrasonic sensor and led"
    parts = re.split(r",|\band\b|\+|/|\n", cleaned)

    return [part.strip() for part in parts if part.strip()]


def parse_components_from_text(text: str) -> tuple[list[ComponentMatch], list[str]]:
    components = load_components()
    user_parts = split_component_text(text)

    matches: list[ComponentMatch] = []
    unmatched: list[str] = []

    for part in user_parts:
        best_match: ComponentDef | None = None
        best_score = 0.0

        for component in components.values():
            names_to_check = [component.name, component.id, *component.aliases]

            for name in names_to_check:
                normalized_name = normalize_text(name)

                if part == normalized_name:
                    score = 1.0
                elif part in normalized_name or normalized_name in part:
                    score = 0.85
                else:
                    score = 0.0

                if score > best_score:
                    best_score = score
                    best_match = component

        if best_match and best_score >= 0.75:
            already_added = any(
                match.matched_component_id == best_match.id for match in matches
            )

            if not already_added:
                matches.append(
                    ComponentMatch(
                        input=part,
                        matched_component_id=best_match.id,
                        name=best_match.name,
                        confidence=best_score,
                    )
                )
        else:
            unmatched.append(part)

    return matches, unmatched