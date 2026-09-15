import pytest

from app.simulation.controls import SUPPORTED_ACTIONS


@pytest.mark.parametrize(
    "action",
    [
        "heartbeat",
        "traffic-change",
        "resource-lost",
        "hospital-reject",
        "ambulance-failure",
        "gps-lost",
        "route-blocked",
        "reset",
        "scenario/start",
    ],
)
def test_deterministic_simulation_controls_are_supported(action):
    assert action in SUPPORTED_ACTIONS
