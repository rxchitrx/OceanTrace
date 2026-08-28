from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ForcingPaths(BaseModel):
    wind_path: str
    current_path: str


class CaseManifest(BaseModel):
    id: str
    region: str
    observation_time: datetime
    image_path: str
    image_bounds_path: str = "sar_bounds.json"
    spill_polygon: str
    annotation_path: Optional[str] = None
    forcing: Optional[ForcingPaths] = None
    ais_path: Optional[str] = None
    scenario_type: Literal["controlled_demo", "detection_validation"]
    ais_type: str = "not_applicable"
    forcing_type: str = "not_applicable"
    coordinate_reference_system: str = "EPSG:4326"
    random_seed: int = 26143
    release_time_prior_hours: float = 6.0
    true_source_vessel_id: Optional[str] = None
    notes: List[str] = Field(default_factory=list)
    data_sources: List[Dict[str, str]] = Field(default_factory=list)


class CandidateSlick(BaseModel):
    polygon: Dict[str, Any]
    score: float
    method: str
    features: Dict[str, float]


class ReleaseWindow(BaseModel):
    start: datetime
    end: datetime
    confidence_band: Literal["low", "moderate", "high"]


class HypothesisPoint(BaseModel):
    latitude: float
    longitude: float
    weight: float
    release_time: datetime


class SourceRegion(BaseModel):
    centroid: Dict[str, float]
    high_probability: Dict[str, Any]
    medium_probability: Dict[str, Any]
    low_probability: Dict[str, Any]
    heatmap_points: List[HypothesisPoint]


class ParticlePoint(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float


class ParticlePath(BaseModel):
    vessel_id: str
    points: List[ParticlePoint]


class VesselEvidence(BaseModel):
    vessel_id: str
    name: str
    mmsi: str
    vessel_type: str
    lead_score: float
    components: Dict[str, float]
    reasons: List[str]
    warnings: List[str]
    nearest_distance_km: float


class AnalysisResult(BaseModel):
    run_id: str
    analysis_mode: Literal["full", "detection_only"] = "full"
    detector: CandidateSlick
    detector_evaluation: Optional[Dict[str, Any]] = None
    source_region: Optional[SourceRegion] = None
    release_window: Optional[ReleaseWindow] = None
    particles: List[ParticlePath] = Field(default_factory=list)
    vessels: List[VesselEvidence] = Field(default_factory=list)
    warnings: List[str]
    metadata: Dict[str, Any]


class CaseSummary(BaseModel):
    id: str
    region: str
    scenario_type: str
    observation_time: datetime
    analysis_mode: Literal["full", "detection_only"]


class AisPoint(BaseModel):
    vessel_id: str
    name: str
    mmsi: str
    timestamp: datetime
    latitude: float
    longitude: float
    speed_over_ground: float
    course_over_ground: float
    vessel_type: str


class CasePayload(BaseModel):
    manifest: CaseManifest
    spill_polygon: Dict[str, Any]
    expected_result: Dict[str, Any] = Field(default_factory=dict)
    available_layers: List[str]
    ais_tracks: Dict[str, List[AisPoint]] = Field(default_factory=dict)


class RunRequest(BaseModel):
    mode: Literal["full", "cached"] = "full"
    seed: int = Field(default=26143, ge=0, le=2_147_483_647)
    use_cached_result: bool = False
