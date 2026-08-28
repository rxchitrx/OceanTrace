from __future__ import annotations

from datetime import datetime
from math import cos, radians, sqrt
from typing import Dict, List


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat_scale = 111.0
    lon_scale = 111.0 * cos(radians((lat1 + lat2) / 2.0))
    dlat = (lat2 - lat1) * lat_scale
    dlon = (lon2 - lon1) * lon_scale
    return sqrt((dlat * dlat) + (dlon * dlon))


def grouped_tracks(rows: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    tracks: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        tracks.setdefault(row["vessel_id"], []).append(row)
    return tracks


def release_window_match(track: List[Dict[str, str]], start: datetime, end: datetime) -> float:
    total = len(track)
    if total == 0:
        return 0.0
    matched = 0
    for row in track:
        timestamp = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
        if start <= timestamp <= end:
            matched += 1
    return matched / total
