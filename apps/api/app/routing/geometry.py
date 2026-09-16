from __future__ import annotations

import math
from hashlib import blake2b

Point = tuple[float, float]

BOW_BY_VARIANT = {"primary": 0.18, "alternative": -0.32}


def _bow(variant: str) -> float:
    known = BOW_BY_VARIANT.get(variant)
    if known is not None:
        return known
    digest = blake2b(variant.encode(), digest_size=2).digest()
    return (int.from_bytes(digest, "big") / 65535.0 - 0.5) * 0.8


def simulated_path(origin: Point, destination: Point, *, variant: str = "primary", vertices: int = 14) -> tuple[Point, ...]:
    """Deterministic SIMULATED road-like polyline between two real coordinates.

    The shape is synthetic and exists only so a map can draw a line that joins the
    true seeded points; every operational number (distance, duration, ETA) still
    comes from the scenario, never from this curve.
    """
    if vertices < 2:
        raise ValueError("A path needs at least two vertices.")
    (start_lat, start_lng), (end_lat, end_lng) = origin, destination
    span_lat, span_lng = end_lat - start_lat, end_lng - start_lng
    length = math.hypot(span_lat, span_lng)
    if length == 0:
        return (origin, destination)
    normal = (-span_lng / length, span_lat / length)
    bow = _bow(variant) * length
    path: list[Point] = []
    for index in range(vertices):
        fraction = index / (vertices - 1)
        offset = bow * math.sin(math.pi * fraction)
        wobble = bow * 0.18 * math.sin(3 * math.pi * fraction)
        path.append((
            round(start_lat + span_lat * fraction + normal[0] * (offset + wobble), 6),
            round(start_lng + span_lng * fraction + normal[1] * (offset + wobble), 6),
        ))
    path[0], path[-1] = (round(start_lat, 6), round(start_lng, 6)), (round(end_lat, 6), round(end_lng, 6))
    return tuple(path)


def as_json(path: tuple[Point, ...]) -> list[dict[str, float]]:
    return [{"lat": lat, "lng": lng} for lat, lng in path]
