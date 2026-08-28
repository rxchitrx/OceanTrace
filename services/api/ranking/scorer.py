from __future__ import annotations

from typing import Dict, List

from services.api.ais.features import distance_km, release_window_match
from services.api.ranking.explanations import build_reasons


WEIGHTS = {
    "origin_region_overlap": 0.35,
    "release_time_match": 0.20,
    "drift_consistency": 0.25,
    "trajectory_heading": 0.10,
    "ais_data_quality": 0.10,
}


def _component_score(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def score_vessels(
    tracks: Dict[str, List[Dict[str, str]]],
    gaps: Dict[str, List[dict]],
    source_centroid: Dict[str, float],
    release_window: Dict[str, object],
) -> List[Dict]:
    ranked: List[Dict] = []
    for vessel_id, track in tracks.items():
        nearest_distance = min(
            distance_km(
                float(row["latitude"]),
                float(row["longitude"]),
                source_centroid["latitude"],
                source_centroid["longitude"],
            )
            for row in track
        )
        overlap = 1.0 if nearest_distance <= 6.0 else max(0.0, 1.0 - ((nearest_distance - 6.0) / 20.0))
        release_match = release_window_match(
            track, release_window["start"], release_window["end"]
        )
        final_course = float(track[-1]["course_over_ground"]) / 360.0
        drift_consistency = max(0.0, 1.0 - (nearest_distance / 18.0))
        ais_quality = max(0.0, 1.0 - (0.25 * len(gaps.get(vessel_id, []))))
        components = {
            "origin_region_overlap": _component_score(overlap),
            "release_time_match": _component_score(release_match),
            "drift_consistency": _component_score(drift_consistency),
            "trajectory_heading": _component_score(1.0 - abs(0.35 - final_course)),
            "ais_data_quality": _component_score(ais_quality),
        }
        lead_score = round(sum(components[key] * weight for key, weight in WEIGHTS.items()) * 100.0, 1)
        reasons, warnings = build_reasons(components, len(gaps.get(vessel_id, [])))
        ranked.append(
            {
                "vessel_id": vessel_id,
                "name": track[0]["name"],
                "mmsi": track[0]["mmsi"],
                "vessel_type": track[0]["vessel_type"],
                "lead_score": lead_score,
                "components": components,
                "reasons": reasons,
                "warnings": warnings,
                "nearest_distance_km": round(nearest_distance, 2),
            }
        )
    ranked.sort(key=lambda vessel: vessel["lead_score"], reverse=True)
    return ranked
