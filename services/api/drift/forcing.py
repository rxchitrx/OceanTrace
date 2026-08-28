from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_forcing(path: Path) -> Dict[str, Any]:
    forcing = json.loads(path.read_text(encoding="utf-8"))
    if forcing.get("units") != "m/s":
        raise ValueError(f"Forcing file must use m/s units: {path}")
    for component in ("u", "v"):
        if component not in forcing:
            raise ValueError(f"Forcing file is missing {component}: {path}")
    forcing.setdefault("uncertainty", 0.0)
    return forcing


def blended_velocity(
    wind: Dict[str, Any],
    current: Dict[str, Any],
    windage: float,
) -> tuple[float, float]:
    return (
        float(current["u"]) + (float(wind["u"]) * windage),
        float(current["v"]) + (float(wind["v"]) * windage),
    )


def perturbed_velocity(
    wind: Dict[str, Any],
    current: Dict[str, Any],
    windage: float,
    wind_u_noise: float,
    wind_v_noise: float,
    current_u_noise: float,
    current_v_noise: float,
) -> tuple[float, float]:
    return (
        float(current["u"])
        + current_u_noise
        + ((float(wind["u"]) + wind_u_noise) * windage),
        float(current["v"])
        + current_v_noise
        + ((float(wind["v"]) + wind_v_noise) * windage),
    )
