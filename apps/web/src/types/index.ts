export type GeoJsonGeometry = {
  type: string;
  coordinates: unknown;
};

export type GeoJsonFeature = {
  type: "Feature";
  properties?: Record<string, unknown>;
  geometry: GeoJsonGeometry;
};

export type Vessel = {
  vessel_id: string;
  name: string;
  lead_score: number;
  warnings: string[];
  reasons: string[];
  nearest_distance_km: number;
  components: Record<string, number>;
  vessel_type: string;
  mmsi: string;
};

export type SourceRegion = {
  centroid: { latitude: number; longitude: number };
  high_probability: GeoJsonGeometry;
  medium_probability: GeoJsonGeometry;
  low_probability: GeoJsonGeometry;
  heatmap_points: Array<{
    latitude: number;
    longitude: number;
    weight: number;
    release_time: string;
  }>;
};

export type AnalysisResult = {
  run_id: string;
  analysis_mode: "full" | "detection_only";
  warnings: string[];
  detector: {
    polygon: GeoJsonGeometry;
    score: number;
    method: string;
    features: Record<string, number>;
  };
  detector_evaluation: {
    annotation_format: string;
    reference_object_count: number;
    best_bbox_iou: number;
    matched_at_iou_0_25: boolean;
    matched_at_iou_0_50: boolean;
  } | null;
  source_region: SourceRegion | null;
  particles: Array<{
    vessel_id: string;
    points: Array<{ timestamp: string; latitude: number; longitude: number }>;
  }>;
  release_window: {
    start: string;
    end: string;
    confidence_band: "low" | "moderate" | "high";
  } | null;
  vessels: Vessel[];
  metadata: {
    case_id: string;
    seed: number;
    observation_time: string;
    scenario_type: string;
    data_sources?: Array<Record<string, string>>;
    drift_diagnostics?: Record<string, number>;
  };
};

export type CaseSummary = {
  id: string;
  region: string;
  scenario_type: string;
  observation_time: string;
  analysis_mode: "full" | "detection_only";
};

export type AisPoint = {
  vessel_id: string;
  name: string;
  mmsi: string;
  timestamp: string;
  latitude: number;
  longitude: number;
  speed_over_ground: number;
  course_over_ground: number;
  vessel_type: string;
};

export type CasePayload = {
  manifest: {
    id: string;
    region: string;
    scenario_type: string;
    notes: string[];
    observation_time: string;
    ais_type: string;
    forcing_type: string;
    data_sources: Array<Record<string, string>>;
  };
  spill_polygon: GeoJsonFeature;
  expected_result: Record<string, unknown>;
  available_layers: string[];
  ais_tracks: Record<string, AisPoint[]>;
};

export type SarBounds = {
  south: number;
  west: number;
  north: number;
  east: number;
};
