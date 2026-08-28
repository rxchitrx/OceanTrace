export type Vessel = {
  vessel_id: string;
  name: string;
  lead_score: number;
  warnings: string[];
  reasons: string[];
  nearest_distance_km: number;
  components: Record<string, number>;
  vessel_type?: string;
  mmsi?: string;
};

export type AnalysisResult = {
  run_id: string;
  warnings: string[];
  detector: {
    score: number;
    method: string;
    features: Record<string, number>;
  };
  source_region: {
    centroid: {
      latitude: number;
      longitude: number;
    };
    high_probability: any;
    medium_probability: any;
    low_probability: any;
    heatmap_points: Array<{
      latitude: number;
      longitude: number;
      weight: number;
      release_time: string;
    }>;
  };
  particles: Array<{
    vessel_id: string;
    points: Array<{
      timestamp: string;
      latitude: number;
      longitude: number;
    }>;
  }>;
  release_window: {
    start: string;
    end: string;
    confidence_band: string;
  };
  vessels: Vessel[];
};

export type CaseSummary = {
  id: string;
  region: string;
  scenario_type: string;
  observation_time: string;
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
  };
  spill_polygon: {
    geometry: {
      coordinates: number[][][];
    };
  };
  expected_result: Record<string, string>;
  available_layers: string[];
  ais_tracks: Record<string, AisPoint[]>;
};
