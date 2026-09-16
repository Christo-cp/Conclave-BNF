from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RouteEstimate:
    distance_m: int
    duration_seconds: int
    traffic_duration_seconds: int
    confidence: float
    provider: str
    data_mode: str
    fallback_used: bool = False


class RoutingProvider(Protocol):
    name: str

    def calculate(self, scenario: dict, origin_code: str, destination_code: str) -> RouteEstimate:
        ...

    def ambulance_eta(self, scenario: dict, ambulance_code: str) -> int:
        ...

    def hospital_eta(self, scenario: dict, hospital_code: str) -> int:
        ...


class MockRoutingProvider:
    name = "mock"

    def calculate(self, scenario: dict, origin_code: str, destination_code: str) -> RouteEstimate:
        routes = scenario.get("routes", {})
        route = routes.get(f"{origin_code}:{destination_code}") or routes.get(destination_code) or routes.get("default")
        if not route:
            raise LookupError("No simulated route is defined for this pair.")
        return RouteEstimate(
            distance_m=int(route["distance_m"]),
            duration_seconds=int(route["duration_seconds"]),
            traffic_duration_seconds=int(route.get("traffic_duration_seconds", route["duration_seconds"])),
            confidence=float(route["confidence"]),
            provider=self.name,
            data_mode="SIMULATED",
        )

    def ambulance_eta(self, scenario: dict, ambulance_code: str) -> int:
        try:
            return int(scenario["ambulance_etas"].get(ambulance_code, scenario["default_ambulance_eta_s"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise LookupError(f"No simulated ETA is defined for {ambulance_code}.") from exc

    def hospital_eta(self, scenario: dict, hospital_code: str) -> int:
        try:
            return int(scenario["hospital_etas"].get(hospital_code, scenario["default_hospital_eta_s"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise LookupError(f"No simulated ETA is defined for {hospital_code}.") from exc
