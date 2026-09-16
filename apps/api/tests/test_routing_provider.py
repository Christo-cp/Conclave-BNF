import pytest

from app.core.errors import ApiError
from app.routing.service import RoutingService


def test_mock_provider_reads_deterministic_scenario_route():
    route = RoutingService().calculate(
        {"routes": {"INC-000001:H-003": {"distance_m": 4200, "duration_seconds": 600, "confidence": 0.95}}},
        "INC-000001",
        "H-003",
    )
    assert route.provider == "mock"
    assert route.data_mode == "SIMULATED"
    assert route.duration_seconds == 600


def test_missing_scenario_route_is_not_fabricated():
    with pytest.raises(ApiError) as error:
        RoutingService().calculate({"routes": {}}, "INC-000001", "H-003")
    assert error.value.code.value == "ROUTING_PROVIDER_ERROR"
