from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from services.api.ais.features import distance_km
from services.api.drift.forcing import blended_velocity
from services.api.drift.particle_model import advect_point, simulate_path


def _square_polygon(center_lat: float, center_lon: float, radius_deg: float) -> Dict:
    return {
        "type": "Polygon",
        "coordinates": [[
            [round(center_lon - radius_deg, 6), round(center_lat - radius_deg, 6)],
            [round(center_lon + radius_deg, 6), round(center_lat - radius_deg, 6)],
            [round(center_lon + radius_deg, 6), round(center_lat + radius_deg, 6)],
            [round(center_lon - radius_deg, 6), round(center_lat + radius_deg, 6)],
            [round(center_lon - radius_deg, 6), round(center_lat - radius_deg, 6)],
        ]],
    }


def search_source_region(
    observation_time: datetime,
    spill_centroid: Tuple[float, float],
    wind: Dict,
    current: Dict,
) -> Dict:
    release_hours = [1, 3, 6, 9, 12]
    windages = [0.01, 0.02, 0.03]
    heatmap_points: List[Dict] = []
    particle_paths: List[Dict] = []
    best = None
    best_score = -1.0
    for release_hour in release_hours:
        release_time = observation_time - timedelta(hours=release_hour)
        for windage in windages:
            velocity_u, velocity_v = blended_velocity(wind, current, windage)
            source_lat, source_lon = advect_point(
                spill_centroid[0], spill_centroid[1], -release_hour, velocity_u, velocity_v
            )
            replay_lat, replay_lon = advect_point(
                source_lat, source_lon, release_hour, velocity_u, velocity_v
            )
            miss_distance = distance_km(
                replay_lat, replay_lon, spill_centroid[0], spill_centroid[1]
            )
            time_weight = max(0.55, 1.0 - (abs(release_hour - 6) / 8.0))
            score = (
                max(0.0, 1.0 - (miss_distance / 8.0))
                * (1.0 - abs(windage - 0.02))
                * time_weight
            )
            point = {
                "latitude": round(source_lat, 6),
                "longitude": round(source_lon, 6),
                "weight": round(score, 4),
                "release_time": release_time,
            }
            heatmap_points.append(point)
            if score > best_score:
                best_score = score
                best = point
            particle_paths.append(
                {
                    "vessel_id": f"hypothesis-{release_hour}h-{int(windage * 1000)}",
                    "points": simulate_path(
                        start_latitude=source_lat,
                        start_longitude=source_lon,
                        start_time=release_time,
                        end_time=observation_time,
                        velocity_u=velocity_u,
                        velocity_v=velocity_v,
                    ),
                }
            )
    assert best is not None
    return {
        "release_window": {
            "start": observation_time - timedelta(hours=9),
            "end": observation_time - timedelta(hours=3),
            "confidence_band": "moderate",
        },
        "source_region": {
            "centroid": {"latitude": best["latitude"], "longitude": best["longitude"]},
            "high_probability": _square_polygon(best["latitude"], best["longitude"], 0.045),
            "medium_probability": _square_polygon(best["latitude"], best["longitude"], 0.085),
            "low_probability": _square_polygon(best["latitude"], best["longitude"], 0.13),
            "heatmap_points": heatmap_points,
        },
        "particles": particle_paths[:6],
    }
