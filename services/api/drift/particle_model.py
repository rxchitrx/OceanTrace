from __future__ import annotations

from datetime import datetime, timedelta
from math import cos, degrees, radians
from typing import List


EARTH_RADIUS_M = 6_371_008.8


def advect_point(
    latitude: float,
    longitude: float,
    elapsed_seconds: float,
    velocity_u_mps: float,
    velocity_v_mps: float,
) -> tuple[float, float]:
    """Advect a surface point using eastward/northward velocity in metres/second."""

    latitude_delta = degrees((velocity_v_mps * elapsed_seconds) / EARTH_RADIUS_M)
    latitude_for_scale = max(-89.999, min(89.999, latitude + latitude_delta / 2.0))
    longitude_delta = degrees(
        (velocity_u_mps * elapsed_seconds)
        / (EARTH_RADIUS_M * max(0.01, cos(radians(latitude_for_scale))))
    )
    return latitude + latitude_delta, longitude + longitude_delta


def simulate_path(
    start_latitude: float,
    start_longitude: float,
    start_time: datetime,
    end_time: datetime,
    velocity_u_mps: float,
    velocity_v_mps: float,
    step_minutes: int = 30,
) -> List[dict]:
    if end_time < start_time:
        raise ValueError("end_time must be after start_time")
    if step_minutes <= 0:
        raise ValueError("step_minutes must be positive")

    points = []
    current_time = start_time
    current_lat = start_latitude
    current_lon = start_longitude
    points.append(
        {
            "timestamp": current_time.isoformat(),
            "latitude": round(current_lat, 6),
            "longitude": round(current_lon, 6),
        }
    )
    while current_time < end_time:
        next_time = min(current_time + timedelta(minutes=step_minutes), end_time)
        elapsed_seconds = (next_time - current_time).total_seconds()
        current_lat, current_lon = advect_point(
            current_lat,
            current_lon,
            elapsed_seconds,
            velocity_u_mps,
            velocity_v_mps,
        )
        current_time = next_time
        points.append(
            {
                "timestamp": current_time.isoformat(),
                "latitude": round(current_lat, 6),
                "longitude": round(current_lon, 6),
            }
        )
    return points
