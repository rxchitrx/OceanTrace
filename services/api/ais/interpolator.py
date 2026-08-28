from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List


def detect_gaps(rows: List[Dict[str, str]], gap_minutes: int = 150) -> Dict[str, List[dict]]:
    grouped: Dict[str, List[dict]] = {}
    for row in rows:
        grouped.setdefault(row["vessel_id"], []).append(row)
    gaps: Dict[str, List[dict]] = {}
    for vessel_id, vessel_rows in grouped.items():
        vessel_gaps: List[dict] = []
        for previous, current in zip(vessel_rows, vessel_rows[1:]):
            start = datetime.fromisoformat(previous["timestamp"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(current["timestamp"].replace("Z", "+00:00"))
            delta_minutes = (end - start).total_seconds() / 60.0
            if delta_minutes > gap_minutes:
                vessel_gaps.append(
                    {
                        "start": previous["timestamp"],
                        "end": current["timestamp"],
                        "duration_minutes": delta_minutes,
                    }
                )
        gaps[vessel_id] = vessel_gaps
    return gaps


def interpolate_short_gaps(
    tracks: Dict[str, List[Dict[str, str]]],
    max_gap_minutes: int = 150,
    interval_minutes: int = 10
) -> Dict[str, List[Dict[str, str]]]:
    interpolated_tracks: Dict[str, List[Dict[str, str]]] = {}
    for vessel_id, track in tracks.items():
        if not track:
            interpolated_tracks[vessel_id] = []
            continue
        
        new_track = [track[0]]
        for prev, curr in zip(track, track[1:]):
            t1 = datetime.fromisoformat(prev["timestamp"].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(curr["timestamp"].replace("Z", "+00:00"))
            delta = (t2 - t1).total_seconds() / 60.0
            
            # Interpolate if gap is short
            if 0 < delta <= max_gap_minutes:
                steps = int(delta // interval_minutes)
                for step in range(1, steps):
                    fraction = (step * interval_minutes) / delta
                    interp_time = t1 + timedelta(minutes=step * interval_minutes)
                    
                    lat1, lon1 = float(prev["latitude"]), float(prev["longitude"])
                    lat2, lon2 = float(curr["latitude"]), float(curr["longitude"])
                    interp_lat = lat1 + (lat2 - lat1) * fraction
                    interp_lon = lon1 + (lon2 - lon1) * fraction
                    
                    sog1 = float(prev["speed_over_ground"])
                    sog2 = float(curr["speed_over_ground"])
                    interp_sog = sog1 + (sog2 - sog1) * fraction
                    
                    cog1 = float(prev["course_over_ground"])
                    cog2 = float(curr["course_over_ground"])
                    interp_cog = cog1 + (cog2 - cog1) * fraction
                    
                    new_track.append({
                        "vessel_id": vessel_id,
                        "name": prev["name"],
                        "mmsi": prev["mmsi"],
                        "timestamp": interp_time.isoformat().replace("+00:00", "Z"),
                        "latitude": f"{interp_lat:.6f}",
                        "longitude": f"{interp_lon:.6f}",
                        "speed_over_ground": f"{interp_sog:.1f}",
                        "course_over_ground": f"{interp_cog:.0f}",
                        "vessel_type": prev["vessel_type"]
                    })
            new_track.append(curr)
        interpolated_tracks[vessel_id] = new_track
    return interpolated_tracks

