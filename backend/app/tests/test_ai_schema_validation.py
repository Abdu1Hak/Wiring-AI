import pytest
from pydantic import ValidationError

from app.schemas.ai_planner_schema import AIConnection, AIPlannerResponse


def test_valid_ai_planner_response():
    plan = AIPlannerResponse(
        status="success",
        projectTitle="Test",
        projectSummary="Summary",
        projectGoal="Goal",
        selectedComponentIds=["arduino_uno"],
        compatibilityStatus="compatible",
        connections=[
            AIConnection(
                id="c1",
                fromComponentId="arduino_uno",
                fromPinId="d9",
                toComponentId="hc_sr04",
                toPinId="trig",
                connectionType="digital_signal",
                wireColor="blue",
                purpose="Trigger",
            )
        ],
        steps=[],
    )
    assert plan.status == "success"


def test_invalid_status_rejected():
    with pytest.raises(ValidationError):
        AIPlannerResponse(
            status="invalid_status",
            projectTitle="T",
            projectSummary="S",
            projectGoal="G",
            selectedComponentIds=[],
            compatibilityStatus="compatible",
        )
