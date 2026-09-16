from app.core.errors import ApiError, ErrorCode
from app.routing.providers import MockRoutingProvider, RouteEstimate


class RoutingService:
    def __init__(self, provider: MockRoutingProvider | None = None) -> None:
        self.provider = provider or MockRoutingProvider()

    def calculate(self, scenario: dict, origin_code: str, destination_code: str, variant: str = "primary") -> RouteEstimate:
        try:
            return self.provider.calculate(scenario, origin_code, destination_code, variant)
        except LookupError as exc:
            raise ApiError(409, ErrorCode.ROUTING_PROVIDER_ERROR, "No simulated route is available.") from exc

    def variants(self, scenario: dict, origin_code: str, destination_code: str) -> list[str]:
        return self.provider.variants(scenario, origin_code, destination_code)

    def ambulance_eta(self, scenario: dict, ambulance_code: str) -> int:
        try:
            return self.provider.ambulance_eta(scenario, ambulance_code)
        except LookupError as exc:
            raise ApiError(409, ErrorCode.ROUTING_PROVIDER_ERROR, "No simulated ambulance ETA is available.") from exc

    def hospital_eta(self, scenario: dict, hospital_code: str) -> int:
        try:
            return self.provider.hospital_eta(scenario, hospital_code)
        except LookupError as exc:
            raise ApiError(409, ErrorCode.ROUTING_PROVIDER_ERROR, "No simulated hospital ETA is available.") from exc
