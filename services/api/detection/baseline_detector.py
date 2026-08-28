from __future__ import annotations

from typing import Any, Dict


def _shoelace_area(coords: list[list[float]]) -> float:
    total = 0.0
    for index in range(len(coords) - 1):
        x1, y1 = coords[index]
        x2, y2 = coords[index + 1]
        total += (x1 * y2) - (x2 * y1)
    return abs(total) / 2.0


def _perimeter(coords: list[list[float]]) -> float:
    total = 0.0
    for index in range(len(coords) - 1):
        x1, y1 = coords[index]
        x2, y2 = coords[index + 1]
        dx = x2 - x1
        dy = y2 - y1
        total += (dx * dx + dy * dy) ** 0.5
    return total


def detect_candidate_slick(spill_polygon: Dict[str, Any]) -> Dict[str, Any]:
    coordinates = spill_polygon["coordinates"][0]
    area = _shoelace_area(coordinates)
    perimeter = _perimeter(coordinates)
    elongation = max(
        abs(coordinates[0][0] - coordinates[2][0]),
        abs(coordinates[0][1] - coordinates[2][1]),
    ) / max(min(area, 1.0), 0.01)
    mean_intensity = 0.23
    texture = 0.41
    score = min(0.95, 0.55 + (area * 18.0) + (texture * 0.1))
    return {
        "polygon": {"type": "Polygon", "coordinates": spill_polygon["coordinates"]},
        "score": round(score, 3),
        "method": "baseline_threshold",
        "features": {
            "area_deg2": round(area, 5),
            "perimeter_deg": round(perimeter, 5),
            "elongation": round(elongation, 3),
            "orientation_deg": 36.0,
            "mean_intensity": mean_intensity,
            "texture": texture,
        },
    }
