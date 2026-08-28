from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def load_ais_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def validate_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    cleaned: List[Dict[str, str]] = []
    for row in rows:
        latitude = float(row["latitude"])
        longitude = float(row["longitude"])
        sog = float(row["speed_over_ground"])
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            continue
        if sog < 0 or sog > 45:
            continue
        datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
        cleaned.append(row)
    cleaned.sort(key=lambda row: (row["vessel_id"], row["timestamp"]))
    return cleaned
