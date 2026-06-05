def test_unsafe_wall_power_blocked(client):
    response = client.post(
        "/api/ai/plan",
        json={
            "projectDescription": "Connect Arduino to 120V wall outlet",
            "selectedComponentIds": ["arduino_uno"],
            "mode": "generate_wiring",
        },
    )
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "unsafe_blocked"
    assert data["aiPlanAccepted"] is False


def test_missing_resistor(client):
    response = client.post(
        "/api/ai/plan",
        json={
            "projectDescription": "Blink an LED",
            "selectedComponentIds": ["arduino_uno", "led_red"],
            "mode": "generate_wiring",
        },
    )
    data = response.json()
    assert data["status"] == "missing_required_components"


def test_motor_without_driver(client):
    response = client.post(
        "/api/ai/plan",
        json={
            "projectDescription": "Spin a motor",
            "selectedComponentIds": ["arduino_uno", "dc_motor_small"],
            "mode": "generate_wiring",
        },
    )
    data = response.json()
    assert data["status"] == "missing_required_components"


def test_valid_ultrasonic_plan(client):
    response = client.post(
        "/api/ai/plan",
        json={
            "projectDescription": "Arduino distance sensor",
            "selectedComponentIds": ["arduino_uno", "hc_sr04"],
            "mode": "generate_wiring",
        },
    )
    data = response.json()
    assert data["status"] == "success"
    assert data["aiPlanAccepted"] is True
    assert len(data["graph"]["edges"]) >= 1
