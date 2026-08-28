from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_forcing(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def blended_velocity(wind: Dict[str, Any], current: Dict[str, Any], windage: float) -> tuple[float, float]:
    wind_u = float(wind["u"])
    wind_v = float(wind["v"])
    current_u = float(current["u"])
    current_v = float(current["v"])
    return (
        current_u + (wind_u * windage),
        current_v + (wind_v * windage),
    )
