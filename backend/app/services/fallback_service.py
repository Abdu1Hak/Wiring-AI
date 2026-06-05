from app.schemas.ai_planner_schema import AIPlannerResponse, CompatibilityFinding


def fallback_message_for_status(status: str) -> str:
    messages = {
        "missing_required_components": (
            "I could not safely generate a wiring plan because required support "
            "components are missing. Add the recommended parts from the catalog."
        ),
        "incompatible": (
            "The selected components appear incompatible for a safe beginner circuit."
        ),
        "unsafe_blocked": (
            "This app only supports low-voltage beginner electronics. "
            "The request was blocked for safety."
        ),
        "no_valid_plan": (
            "I could not safely generate a wiring plan with the selected components."
        ),
        "needs_more_info": (
            "Please add a clearer project description or select a controller and outputs."
        ),
    }
    return messages.get(status, messages["no_valid_plan"])


def build_blocked_plan(
    status: str,
    findings: list[CompatibilityFinding],
    project_description: str = "",
) -> AIPlannerResponse:
    compatibility_status = status if status != "no_valid_plan" else "incompatible"
    if status == "unsafe_blocked":
        compatibility_status = "unsafe_blocked"
    elif status == "missing_required_components":
        compatibility_status = "missing_required_components"

    return AIPlannerResponse(
        status=status,
        projectTitle="Wiring plan unavailable",
        projectSummary=fallback_message_for_status(status),
        projectGoal=project_description,
        selectedComponentIds=[],
        compatibilityStatus=compatibility_status,  # type: ignore[arg-type]
        compatibilityFindings=findings,
        connections=[],
        steps=[],
    )
