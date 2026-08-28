from __future__ import annotations

from datetime import datetime
from math import atan2, cos, degrees, radians, sin, sqrt
from typing import Dict, List, Optional


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat_scale = 111.195
    lon_scale = 111.195 * cos(radians((lat1 + lat2) / 2.0))
    dlat = (lat2 - lat1) * lat_scale
    dlon = (lon2 - lon1) * lon_scale
    return sqrt((dlat * dlat) + (dlon * dlon))


def bearing_degrees(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad, lat2_rad = radians(lat1), radians(lat2)
    delta_lon = radians(lon2 - lon1)
    x = sin(delta_lon) * cos(lat2_rad)
    y = cos(lat1_rad) * sin(lat2_rad) - sin(lat1_rad) * cos(lat2_rad) * cos(delta_lon)
    return (degrees(atan2(x, y)) + 360.0) % 360.0


def angular_similarity(a: float, b: float) -> float:
    difference = abs((a - b + 180.0) % 360.0 - 180.0)
    return max(0.0, 1.0 - difference / 180.0)


def grouped_tracks(rows: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    tracks: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        tracks.setdefault(row["vessel_id"], []).append(row)
    return tracks


def position_at_time(
    track: List[Dict[str, str]],
    target: datetime,
    *,
    maximum_gap_minutes: int = 150,
) -> Optional[Dict[str, float]]:
    if not track:
        return None
    points = sorted(track, key=lambda row: row["timestamp"])
    for row in points:
        if parse_timestamp(row["timestamp"]) == target:
            return {
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "course_over_ground": float(row["course_over_ground"]),
            }

    for previous, current in zip(points, points[1:]):
        start = parse_timestamp(previous["timestamp"])
        end = parse_timestamp(current["timestamp"])
        if not (start <= target <= end):
            continue
        duration_minutes = (end - start).total_seconds() / 60.0
        if duration_minutes <= 0 or duration_minutes > maximum_gap_minutes:
            return None
        fraction = (target - start).total_seconds() / (end - start).total_seconds()
        return {
            "latitude": float(previous["latitude"])
            + (float(current["latitude"]) - float(previous["latitude"])) * fraction,
            "longitude": float(previous["longitude"])
            + (float(current["longitude"]) - float(previous["longitude"])) * fraction,
            "course_over_ground": float(previous["course_over_ground"])
            + (float(current["course_over_ground"]) - float(previous["course_over_ground"]))
            * fraction,
        }
    return None


def trajectory_course_consistency(track: List[Dict[str, str]]) -> float:
    scores: list[float] = []
    for previous, current in zip(track, track[1:]):
        distance = distance_km(
            float(previous["latitude"]),
            float(previous["longitude"]),
            float(current["latitude"]),
            float(current["longitude"]),
        )
        if distance < 0.05:
            continue
        computed = bearing_degrees(
            float(previous["latitude"]),
            float(previous["longitude"]),
            float(current["latitude"]),
            float(current["longitude"]),
        )
        reported = float(previous["course_over_ground"])
        scores.append(angular_similarity(computed, reported))
    return sum(scores) / len(scores) if scores else 0.5


def overlapping_gap_count(
    vessel_gaps: List[dict],
    start: datetime,
    end: datetime,
) -> int:
    count = 0
    for gap in vessel_gaps:
        gap_start = parse_timestamp(gap["start"])
        gap_end = parse_timestamp(gap["end"])
        if gap_start <= end and gap_end >= start:
            count += 1
    return count
