import type { AnalysisResult, CasePayload, CaseSummary } from "./types";

export const fallbackCases: CaseSummary[] = [
  {
    id: "arabian_sea_demo",
    region: "Arabian Sea",
    scenario_type: "controlled_demo",
    observation_time: "2026-01-14T12:00:00Z",
  },
  {
    id: "dartis_validation",
    region: "Reference Validation Scene",
    scenario_type: "detection_validation",
    observation_time: "2025-06-01T09:30:00Z",
  },
];

export const fallbackCasePayload: CasePayload = {
  manifest: {
    id: "arabian_sea_demo",
    region: "Arabian Sea",
    scenario_type: "controlled_demo",
    notes: [
      "Controlled demonstration scenario",
      "AIS tracks: simulated",
      "Output: investigative lead, not legal attribution",
    ],
    observation_time: "2026-01-14T12:00:00Z",
  },
  spill_polygon: {
    geometry: {
      coordinates: [
        [
          [68.95, 18.92],
          [69.08, 18.95],
          [69.11, 19.03],
          [68.99, 19.06],
          [68.95, 18.92],
        ],
      ],
    },
  },
  expected_result: {
    expected_top_vessel_id: "vessel_a",
    expected_release_window_start: "2026-01-14T03:00:00Z",
    expected_release_window_end: "2026-01-14T09:00:00Z",
  },
  available_layers: [
    "sar_image",
    "spill_polygon",
    "source_heatmap",
    "particle_paths",
    "ais_tracks",
  ],
  ais_tracks: {
    vessel_a: [
      { vessel_id: "vessel_a", name: "MV Ocean Star", mmsi: "419000111", timestamp: "2026-01-14T02:00:00Z", latitude: 18.77, longitude: 68.88, speed_over_ground: 11.8, course_over_ground: 42, vessel_type: "tanker" },
      { vessel_id: "vessel_a", name: "MV Ocean Star", mmsi: "419000111", timestamp: "2026-01-14T04:00:00Z", latitude: 18.80, longitude: 68.91, speed_over_ground: 12.0, course_over_ground: 44, vessel_type: "tanker" },
      { vessel_id: "vessel_a", name: "MV Ocean Star", mmsi: "419000111", timestamp: "2026-01-14T06:00:00Z", latitude: 18.83, longitude: 68.95, speed_over_ground: 12.1, course_over_ground: 45, vessel_type: "tanker" },
      { vessel_id: "vessel_a", name: "MV Ocean Star", mmsi: "419000111", timestamp: "2026-01-14T08:00:00Z", latitude: 18.87, longitude: 68.99, speed_over_ground: 12.0, course_over_ground: 47, vessel_type: "tanker" },
      { vessel_id: "vessel_a", name: "MV Ocean Star", mmsi: "419000111", timestamp: "2026-01-14T10:00:00Z", latitude: 18.90, longitude: 69.03, speed_over_ground: 11.7, course_over_ground: 48, vessel_type: "tanker" }
    ],
    vessel_b: [
      { vessel_id: "vessel_b", name: "MV Coastal Trader", mmsi: "419000222", timestamp: "2026-01-14T02:00:00Z", latitude: 18.89, longitude: 69.10, speed_over_ground: 10.2, course_over_ground: 91, vessel_type: "cargo" },
      { vessel_id: "vessel_b", name: "MV Coastal Trader", mmsi: "419000222", timestamp: "2026-01-14T04:00:00Z", latitude: 18.96, longitude: 69.11, speed_over_ground: 10.1, course_over_ground: 96, vessel_type: "cargo" },
      { vessel_id: "vessel_b", name: "MV Coastal Trader", mmsi: "419000222", timestamp: "2026-01-14T06:00:00Z", latitude: 19.04, longitude: 69.12, speed_over_ground: 9.8, course_over_ground: 101, vessel_type: "cargo" },
      { vessel_id: "vessel_b", name: "MV Coastal Trader", mmsi: "419000222", timestamp: "2026-01-14T08:00:00Z", latitude: 19.11, longitude: 69.13, speed_over_ground: 9.9, course_over_ground: 102, vessel_type: "cargo" },
      { vessel_id: "vessel_b", name: "MV Coastal Trader", mmsi: "419000222", timestamp: "2026-01-14T10:00:00Z", latitude: 19.17, longitude: 69.14, speed_over_ground: 10.0, course_over_ground: 100, vessel_type: "cargo" }
    ],
    vessel_c: [
      { vessel_id: "vessel_c", name: "MV Horizon", mmsi: "419000333", timestamp: "2026-01-13T20:00:00Z", latitude: 18.50, longitude: 68.30, speed_over_ground: 13.4, course_over_ground: 220, vessel_type: "bulk_carrier" },
      { vessel_id: "vessel_c", name: "MV Horizon", mmsi: "419000333", timestamp: "2026-01-13T22:00:00Z", latitude: 18.42, longitude: 68.22, speed_over_ground: 13.2, course_over_ground: 221, vessel_type: "bulk_carrier" },
      { vessel_id: "vessel_c", name: "MV Horizon", mmsi: "419000333", timestamp: "2026-01-14T00:00:00Z", latitude: 18.35, longitude: 68.15, speed_over_ground: 13.0, course_over_ground: 219, vessel_type: "bulk_carrier" },
      { vessel_id: "vessel_c", name: "MV Horizon", mmsi: "419000333", timestamp: "2026-01-14T10:00:00Z", latitude: 18.00, longitude: 67.80, speed_over_ground: 13.1, course_over_ground: 223, vessel_type: "bulk_carrier" }
    ]
  }
};

export const fallbackResult: AnalysisResult = {
  run_id: "arabian_sea_demo-seed-26143",
  detector: {
    score: 0.839,
    method: "baseline_threshold",
    features: {
      area_deg2: 0.01375,
      perimeter_deg: 0.48815,
      elongation: 11.636,
      orientation_deg: 36,
      mean_intensity: 0.23,
      texture: 0.41,
    },
  },
  source_region: {
    centroid: {
      latitude: 18.96528,
      longitude: 68.97106,
    },
    high_probability: {
      type: "Polygon",
      coordinates: [[[68.926, 18.920], [69.016, 18.920], [69.016, 19.010], [68.926, 19.010], [68.926, 18.920]]]
    },
    medium_probability: {
      type: "Polygon",
      coordinates: [[[68.886, 18.880], [69.056, 18.880], [69.056, 19.050], [68.886, 19.050], [68.886, 18.880]]]
    },
    low_probability: {
      type: "Polygon",
      coordinates: [[[68.841, 18.835], [69.101, 18.835], [69.101, 19.095], [68.841, 19.095], [68.841, 18.835]]]
    },
    heatmap_points: [
      { latitude: 18.98588, longitude: 69.02226, weight: 0.55, release_time: "2026-01-14T11:00:00Z" },
      { latitude: 18.97764, longitude: 69.00178, weight: 0.625, release_time: "2026-01-14T09:00:00Z" },
      { latitude: 18.96528, longitude: 68.97106, weight: 1, release_time: "2026-01-14T06:00:00Z" },
      { latitude: 18.95292, longitude: 68.94034, weight: 0.625, release_time: "2026-01-14T03:00:00Z" },
    ],
  },
  particles: [
    {
      vessel_id: "hypothesis-3h-20",
      points: [
        { timestamp: "2026-01-14T09:00:00Z", latitude: 18.97764, longitude: 69.00178 },
        { timestamp: "2026-01-14T10:30:00Z", latitude: 18.98382, longitude: 69.01714 },
        { timestamp: "2026-01-14T12:00:00Z", latitude: 18.99, longitude: 69.0325 },
      ],
    },
  ],
  release_window: {
    start: "2026-01-14T03:00:00Z",
    end: "2026-01-14T09:00:00Z",
    confidence_band: "moderate",
  },
  vessels: [
    {
      vessel_id: "vessel_a",
      name: "MV Ocean Star",
      lead_score: 70.4,
      reasons: [
        "Track intersects the high-probability source region.",
        "Vessel was present during the estimated release window.",
        "AIS coverage is adequate for this candidate.",
      ],
      warnings: [],
      nearest_distance_km: 9.53,
      components: {
        origin_region_overlap: 0.824,
        release_time_match: 0.6,
        drift_consistency: 0.471,
        trajectory_heading: 0.783,
        ais_data_quality: 1,
      },
    },
    {
      vessel_id: "vessel_b",
      name: "MV Coastal Trader",
      lead_score: 56,
      reasons: [
        "Vessel was present during the estimated release window.",
        "AIS coverage is adequate for this candidate.",
      ],
      warnings: [],
      nearest_distance_km: 14.6,
      components: {
        origin_region_overlap: 0.57,
        release_time_match: 0.6,
        drift_consistency: 0.189,
        trajectory_heading: 0.928,
        ais_data_quality: 1,
      },
    },
    {
      vessel_id: "vessel_c",
      name: "MV Horizon",
      lead_score: 14.8,
      reasons: ["AIS coverage is adequate for this candidate."],
      warnings: ["AIS gap overlaps part of the release window."],
      nearest_distance_km: 87.43,
      components: {
        origin_region_overlap: 0,
        release_time_match: 0,
        drift_consistency: 0,
        trajectory_heading: 0.731,
        ais_data_quality: 0.75,
      },
    },
  ],
  warnings: [
    "Controlled demonstration scenario.",
    "AIS tracks are simulated.",
    "Output is an investigative lead, not legal attribution.",
  ],
};
