from __future__ import annotations

from datetime import datetime, timedelta
from math import cos, exp, pi, sin
from typing import Any, Dict, List

import numpy as np

from services.api.ais.features import distance_km
from services.api.drift.forcing import blended_velocity, perturbed_velocity
from services.api.drift.particle_model import advect_point, simulate_path


def polygon_centroid(polygon: Dict[str, Any]) -> tuple[float, float]:
    coordinates = polygon["coordinates"][0]
    points = coordinates[:-1] if coordinates[0] == coordinates[-1] else coordinates
    latitude = sum(point[1] for point in points) / len(points)
    longitude = sum(point[0] for point in points) / len(points)
    return latitude, longitude


def point_in_polygon(latitude: float, longitude: float, polygon: Dict[str, Any]) -> bool:
    coordinates = polygon["coordinates"][0]
    inside = False
    previous = coordinates[-1]
    for current in coordinates:
        x1, y1 = previous
        x2, y2 = current
        denominator = y2 - y1
        intersects = ((y1 > latitude) != (y2 > latitude)) and (
            longitude
            < (x2 - x1) * (latitude - y1) / (denominator if abs(denominator) > 1e-12 else 1e-12)
            + x1
        )
        if intersects:
            inside = not inside
        previous = current
    return inside


def _ellipse_polygon(
    center_lat: float,
    center_lon: float,
    covariance: np.ndarray,
    scale: float,
) -> Dict[str, Any]:
    values, vectors = np.linalg.eigh(covariance)
    values = np.maximum(values, np.array([2.5e-6, 2.5e-6]))
    transform = vectors @ np.diag(np.sqrt(values) * scale)
    coordinates: list[list[float]] = []
    for index in range(32):
        angle = 2.0 * pi * index / 32.0
        offset = transform @ np.array([cos(angle), sin(angle)])
        coordinates.append(
            [round(center_lon + float(offset[1]), 7), round(center_lat + float(offset[0]), 7)]
        )
    coordinates.append(coordinates[0])
    return {"type": "Polygon", "coordinates": [coordinates]}


def search_source_region(
    observation_time: datetime,
    spill_polygon: Dict[str, Any],
    wind: Dict[str, Any],
    current: Dict[str, Any],
    *,
    seed: int = 26143,
    expected_age_hours: float = 6.0,
) -> Dict[str, Any]:
    """Reconstruct a probabilistic source region with forward-validated ensembles."""

    rng = np.random.default_rng(seed)
    spill_centroid = polygon_centroid(spill_polygon)
    release_hours = [1, 3, 6, 9, 12]
    windages = [0.01, 0.02, 0.03]
    members_per_setting = 12
    hypotheses: List[Dict[str, Any]] = []
    nominal_u, nominal_v = blended_velocity(wind, current, 0.02)
    wind_uncertainty = float(wind.get("uncertainty", 0.0))
    current_uncertainty = float(current.get("uncertainty", 0.0))

    for release_hour in release_hours:
        release_time = observation_time - timedelta(hours=release_hour)
        elapsed_seconds = release_hour * 3600.0
        age_prior = exp(-0.5 * ((release_hour - expected_age_hours) / 3.5) ** 2)
        for windage in windages:
            for _ in range(members_per_setting):
                reverse_u, reverse_v = perturbed_velocity(
                    wind,
                    current,
                    windage,
                    rng.normal(0.0, wind_uncertainty),
                    rng.normal(0.0, wind_uncertainty),
                    rng.normal(0.0, current_uncertainty),
                    rng.normal(0.0, current_uncertainty),
                )
                source_lat, source_lon = advect_point(
                    spill_centroid[0],
                    spill_centroid[1],
                    -elapsed_seconds,
                    reverse_u,
                    reverse_v,
                )

                validation_u = nominal_u + rng.normal(0.0, current_uncertainty * 0.35)
                validation_v = nominal_v + rng.normal(0.0, current_uncertainty * 0.35)
                replay_lat, replay_lon = advect_point(
                    source_lat,
                    source_lon,
                    elapsed_seconds,
                    validation_u,
                    validation_v,
                )
                miss_distance = distance_km(
                    replay_lat,
                    replay_lon,
                    spill_centroid[0],
                    spill_centroid[1],
                )
                centroid_score = exp(-0.5 * (miss_distance / 4.5) ** 2)

                contained = 0
                particle_count = 16
                for _particle_index in range(particle_count):
                    final_lat, final_lon = advect_point(
                        source_lat,
                        source_lon,
                        elapsed_seconds,
                        validation_u + rng.normal(0.0, 0.035),
                        validation_v + rng.normal(0.0, 0.035),
                    )
                    contained += int(point_in_polygon(final_lat, final_lon, spill_polygon))
                coverage_score = contained / particle_count
                score = 0.58 * centroid_score + 0.24 * coverage_score + 0.18 * age_prior
                hypotheses.append(
                    {
                        "latitude": source_lat,
                        "longitude": source_lon,
                        "weight": score,
                        "release_time": release_time,
                        "release_hour": release_hour,
                        "windage": windage,
                        "miss_distance_km": miss_distance,
                    }
                )

    maximum_weight = max(hypothesis["weight"] for hypothesis in hypotheses)
    for hypothesis in hypotheses:
        hypothesis["weight"] = hypothesis["weight"] / maximum_weight

    weights = np.array([hypothesis["weight"] for hypothesis in hypotheses], dtype=float)
    coordinates = np.array(
        [[hypothesis["latitude"], hypothesis["longitude"]] for hypothesis in hypotheses],
        dtype=float,
    )
    normalized_weights = weights / weights.sum()
    centroid = np.average(coordinates, axis=0, weights=normalized_weights)
    centered = coordinates - centroid
    covariance = (centered * normalized_weights[:, None]).T @ centered

    likely = [hypothesis for hypothesis in hypotheses if hypothesis["weight"] >= 0.90]
    release_times = [hypothesis["release_time"] for hypothesis in likely]
    if not release_times:
        release_times = [observation_time - timedelta(hours=9), observation_time - timedelta(hours=3)]

    top_hypotheses = sorted(hypotheses, key=lambda item: item["weight"], reverse=True)[:10]
    particle_paths = [
        {
            "vessel_id": f"source-hypothesis-{index + 1}",
            "points": simulate_path(
                start_latitude=hypothesis["latitude"],
                start_longitude=hypothesis["longitude"],
                start_time=hypothesis["release_time"],
                end_time=observation_time,
                velocity_u_mps=nominal_u,
                velocity_v_mps=nominal_v,
            ),
        }
        for index, hypothesis in enumerate(top_hypotheses)
    ]

    heatmap_points = [
        {
            "latitude": round(hypothesis["latitude"], 6),
            "longitude": round(hypothesis["longitude"], 6),
            "weight": round(hypothesis["weight"], 4),
            "release_time": hypothesis["release_time"],
        }
        for hypothesis in hypotheses
    ]
    return {
        "release_window": {
            "start": min(release_times),
            "end": max(release_times),
            "confidence_band": "moderate",
        },
        "source_region": {
            "centroid": {
                "latitude": round(float(centroid[0]), 6),
                "longitude": round(float(centroid[1]), 6),
            },
            "high_probability": _ellipse_polygon(centroid[0], centroid[1], covariance, 0.85),
            "medium_probability": _ellipse_polygon(centroid[0], centroid[1], covariance, 1.55),
            "low_probability": _ellipse_polygon(centroid[0], centroid[1], covariance, 2.35),
            "heatmap_points": heatmap_points,
        },
        "particles": particle_paths,
        "diagnostics": {
            "ensemble_members": len(hypotheses),
            "nominal_velocity_u_mps": round(nominal_u, 4),
            "nominal_velocity_v_mps": round(nominal_v, 4),
            "median_forward_miss_km": round(
                float(np.median([item["miss_distance_km"] for item in hypotheses])), 3
            ),
        },
    }
