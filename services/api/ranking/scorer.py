from __future__ import annotations

from datetime import datetime
from math import exp
from typing import Any, Dict, List

from services.api.ais.features import (
    distance_km,
    overlapping_gap_count,
    position_at_time,
    trajectory_course_consistency,
)
from services.api.drift.forcing import blended_velocity
from services.api.drift.particle_model import advect_point
from services.api.drift.source_search import polygon_centroid
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
    source_region: Dict[str, Any],
    release_window: Dict[str, object],
    observation_time: datetime,
    observed_slick: Dict[str, Any],
    wind: Dict[str, Any],
    current: Dict[str, Any],
) -> List[Dict[str, Any]]:
    ranked: List[Dict[str, Any]] = []
    heatmap_points = source_region["heatmap_points"]
    strongest = sorted(heatmap_points, key=lambda item: item["weight"], reverse=True)[:45]
    spill_lat, spill_lon = polygon_centroid(observed_slick)
    nominal_u, nominal_v = blended_velocity(wind, current, 0.02)

    for vessel_id, track in tracks.items():
        weighted_origin = 0.0
        weighted_forward = 0.0
        covered_weight = 0.0
        total_weight = sum(float(item["weight"]) for item in strongest) or 1.0
        source_distances: list[float] = []

        for hypothesis in strongest:
            release_time = hypothesis["release_time"]
            if isinstance(release_time, str):
                release_time = datetime.fromisoformat(release_time.replace("Z", "+00:00"))
            position = position_at_time(track, release_time)
            if position is None:
                continue
            weight = float(hypothesis["weight"])
            covered_weight += weight
            source_distance = distance_km(
                position["latitude"],
                position["longitude"],
                float(hypothesis["latitude"]),
                float(hypothesis["longitude"]),
            )
            source_distances.append(source_distance)
            weighted_origin += weight * exp(-0.5 * (source_distance / 7.0) ** 2)

            elapsed_seconds = (observation_time - release_time).total_seconds()
            final_lat, final_lon = advect_point(
                position["latitude"],
                position["longitude"],
                elapsed_seconds,
                nominal_u,
                nominal_v,
            )
            forward_miss = distance_km(final_lat, final_lon, spill_lat, spill_lon)
            weighted_forward += weight * exp(-0.5 * (forward_miss / 11.0) ** 2)

        origin_score = weighted_origin / max(covered_weight, 1e-9)
        forward_score = weighted_forward / max(covered_weight, 1e-9)
        release_score = covered_weight / total_weight
        trajectory_score = trajectory_course_consistency(track)
        gap_count = overlapping_gap_count(
            gaps.get(vessel_id, []),
            release_window["start"],
            release_window["end"],
        )
        coverage_quality = min(1.0, release_score / 0.75)
        ais_quality = max(0.0, coverage_quality - 0.25 * gap_count)
        components = {
            "origin_region_overlap": _component_score(origin_score),
            "release_time_match": _component_score(release_score),
            "drift_consistency": _component_score(forward_score),
            "trajectory_heading": _component_score(trajectory_score),
            "ais_data_quality": _component_score(ais_quality),
        }
        lead_score = round(
            sum(components[key] * weight for key, weight in WEIGHTS.items()) * 100.0,
            1,
        )
        reasons, warnings = build_reasons(components, gap_count)
        nearest_distance = min(source_distances) if source_distances else min(
            distance_km(
                float(row["latitude"]),
                float(row["longitude"]),
                source_region["centroid"]["latitude"],
                source_region["centroid"]["longitude"],
            )
            for row in track
        )
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
