from __future__ import annotations

from datetime import datetime, timedelta
from typing import List


def advect_point(
    latitude: float,
    longitude: float,
    hours: float,
    velocity_u: float,
    velocity_v: float,
) -> tuple[float, float]:
    return (
        latitude + (velocity_v * hours),
        longitude + (velocity_u * hours),
    )


def simulate_path(
    start_latitude: float,
    start_longitude: float,
    start_time: datetime,
    end_time: datetime,
    velocity_u: float,
    velocity_v: float,
    step_minutes: int = 30,
) -> List[dict]:
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
        elapsed_hours = (next_time - current_time).total_seconds() / 3600.0
        current_lat, current_lon = advect_point(
            current_lat, current_lon, elapsed_hours, velocity_u, velocity_v
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
