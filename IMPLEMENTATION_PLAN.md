# OCEANTRACE Phase 1 Implementation Plan

## 1. Objective

Build a reliable internal-college-phase prototype for SIH26143 that demonstrates this complete workflow:

```text
Satellite image
      ↓
Possible slick detected
      ↓
Look-alikes and uncertainty exposed
      ↓
Probable source region reconstructed
      ↓
AIS vessel trajectories correlated
      ↓
Investigative leads ranked with reasons
```

The prototype must be deterministic, explainable, and demoable from local files. It must not depend on a live API during judging.

## 2. Definition of success

The prototype is complete when a reviewer can:

1. Open the application.
2. Select one preloaded case.
3. View the SAR scene and candidate slick.
4. Run or replay source reconstruction.
5. See an uncertainty-aware source heatmap.
6. View at least three vessel trajectories.
7. See a ranked candidate list.
8. Open a candidate and understand why it ranked there.
9. See data-quality warnings and model limitations.
10. Re-run the same case and receive the same result.

The target is a persuasive 5–7 minute demo, not production readiness.

## 3. Scope decisions

### Must build

- One end-to-end controlled case.
- Candidate slick polygon and SAR image overlay.
- Particle-based source reconstruction.
- Source-region heatmap.
- Three AIS-like vessel tracks.
- Transparent ranking score.
- Evidence explanations.
- Uncertainty and data-quality labels.
- Local offline fallback.
- Basic evaluation and golden-case tests.

### Build if the core path is stable

- A second detection-only case from DARTIS or CSIRO.
- A real archived wind/current snapshot.
- Forward validation from candidate vessel routes.
- Look-alike filtering.
- Non-vessel source markers such as ports, platforms, or pipelines.
- Optional OpenDrift adapter.

### Defer

- Live global AIS.
- Real-time Sentinel-1 ingestion.
- Dark-vessel deep-learning detection.
- Chemical fingerprinting.
- Full oil-weathering chemistry.
- Neural trajectory prediction.
- Large transformer segmentation.
- Cloud deployment and production authentication.

## 4. Data strategy

### Case A: end-to-end golden case

Use a controlled Indian-coast or Arabian Sea scenario:

- SAR image or SAR-derived raster.
- Observation timestamp.
- Spill polygon.
- Archived or controlled wind field.
- Archived or controlled current field.
- Three vessel tracks.
- Known simulated source vessel.
- Expected source region and expected top candidate.

The case manifest must state which assets are real and which are simulated.

Example metadata:

```json
{
  "id": "arabian-sea-demo-01",
  "region": "Arabian Sea",
  "scenario_type": "controlled_demo",
  "observation_time": "2026-01-14T12:00:00Z",
  "ais_type": "simulated",
  "forcing_type": "archived_snapshot",
  "coordinate_reference_system": "EPSG:4326",
  "random_seed": 26143
}
```

### Case B: detection validation

Use a public labelled image for detector validation. Prefer an asset that can be downloaded individually and whose licence is compatible with the project.

For DARTIS, object annotations may need to be converted into an approximate polygon. Treat that as a prototype approximation and do not describe it as a perfect segmentation mask.

### Data fallback order

If a dependency fails:

1. Use an archived local forcing snapshot.
2. Use a controlled synthetic vector field.
3. Use locally generated vessel tracks.
4. Use a precomputed analysis result for the presentation.

The fallback must be visible in the case metadata.

## 5. System architecture

```text
┌──────────────────────────────────────────┐
│ React dashboard                          │
│ case selection · map · timeline · scores │
└──────────────────┬───────────────────────┘
                   │ JSON/GeoJSON API
┌──────────────────▼───────────────────────┐
│ FastAPI case runner                       │
│ validation · orchestration · run metadata │
└───────┬──────────────┬──────────────┬─────┘
        ▼              ▼              ▼
   SAR detector    Drift engine    AIS engine
        └──────────────┬──────────────┘
                       ▼
              Evidence/ranking engine
                       ▼
             AnalysisResult JSON/GeoJSON
```

### Storage approach

Keep Phase 1 storage simple:

- Case inputs in `data/cases/<case-id>/`.
- Generated outputs in a local generated-results directory.
- SQLite only if run history is required.
- No remote database requirement.

## 6. Data contracts

### Required case inputs

```text
case.json
sar.png or sar.tif
spill_polygon.geojson
wind.json or wind.nc
currents.json or currents.nc
ais.csv
```

### AIS schema

```text
vessel_id
name
mmsi
timestamp
latitude
longitude
speed_over_ground
course_over_ground
vessel_type
```

### Analysis result schema

```json
{
  "run_id": "fixed-seed-run-001",
  "detector": {
    "candidate_polygon": {},
    "candidate_score": 0.81,
    "method": "baseline_threshold"
  },
  "release_window": {
    "start": "2026-01-14T03:00:00Z",
    "end": "2026-01-14T09:00:00Z",
    "confidence_band": "moderate"
  },
  "source_region": {},
  "particles": {},
  "vessels": [],
  "warnings": []
}
```

Use a fixed random seed in the golden case. Every result should include method names, timestamps, data provenance, and warnings.

## 7. Module implementation details

### 7.1 SAR candidate detector

Implement the baseline in this order:

1. Read the raster.
2. Normalize intensity using robust percentiles.
3. Apply median or Gaussian smoothing.
4. Mask land, borders, and invalid pixels.
5. Detect dark candidate regions using an adaptive threshold.
6. Extract connected components.
7. Remove regions that are too small, too narrow, border-connected, or geometrically implausible.
8. Compute area, perimeter, elongation, orientation, mean intensity, and texture.
9. Return a candidate polygon and heuristic score.

The baseline should produce a useful result on the golden case even if a learned model is not ready.

Do not call the heuristic score a calibrated probability.

### 7.2 Drift engine

Inputs:

- Observed slick polygon.
- Observation timestamp.
- Wind field.
- Current field.
- Release-time search interval.
- Windage range.
- Diffusion/uncertainty settings.

Algorithm:

1. Expand the observed slick polygon by a search buffer.
2. Generate source hypotheses on a spatial grid.
3. Generate release-time hypotheses, initially up to 12 hours before observation.
4. Seed particles at each hypothesis.
5. Forward-simulate particles to the observation time.
6. Perturb wind, current, and windage for an ensemble.
7. Compare each simulated slick with the observed slick.
8. Retain and aggregate the strongest hypotheses.
9. Convert hypothesis weights into a source heatmap.
10. Run a future forecast from the highest-ranked source region if time allows.

Initial parameters:

```text
time step: 15–30 minutes
particles per hypothesis: 50–100
hypotheses: 100–300
maximum backtrack duration: 12 hours
fixed random seed: yes
```

Use an overlap-and-distance score rather than trusting a single reverse path:

```text
forward consistency =
    0.45 × polygon overlap
  + 0.25 × centroid proximity
  + 0.20 × shape/direction similarity
  + 0.10 × ensemble coverage
```

The implementation may begin with a local vector field. OpenDrift should be integrated only through an adapter so it can be replaced without changing the API.

### 7.3 AIS engine

Implement:

1. Coordinate and timestamp validation.
2. Vessel/time sorting.
3. Impossible-speed filtering.
4. Duplicate removal.
5. Short-gap interpolation.
6. Long-gap detection.
7. Track buffering and source-region intersection.
8. Release-window compatibility calculation.
9. Track direction and heading features.
10. AIS-quality scoring.

Only interpolate short gaps. Long gaps should remain visible as warnings and reduce data quality.

### 7.4 Evidence and ranking engine

Normalize each evidence component to `[0, 1]`:

```text
origin_region_overlap: 0.35
release_time_match:    0.20
drift_consistency:     0.25
trajectory_heading:    0.10
ais_data_quality:      0.10
```

The engine must return both the numerical components and human-readable reasons. Example:

```json
{
  "vessel_id": "vessel-a",
  "lead_score": 0.84,
  "components": {
    "origin_region_overlap": 0.91,
    "release_time_match": 0.87,
    "drift_consistency": 0.82,
    "trajectory_heading": 0.90,
    "ais_data_quality": 0.76
  },
  "reasons": [
    "Track intersects the high-probability source region",
    "Present during the estimated release window",
    "Forward drift reproduces the observed slick direction"
  ],
  "warnings": [
    "AIS gap overlaps part of the release window"
  ]
}
```

## 8. API surface

Implement the smallest useful API:

```text
GET  /api/health
GET  /api/cases
GET  /api/cases/{case_id}
POST /api/cases/{case_id}/run
GET  /api/cases/{case_id}/results/{run_id}
```

`POST /run` should accept optional settings such as:

```json
{
  "mode": "full",
  "seed": 26143,
  "use_cached_result": false
}
```

For the demo, the API may return a cached deterministic result after verifying that the case is valid.

## 9. Frontend implementation

Create one investigation workspace.

### Main layout

- Left panel: workflow steps and case metadata.
- Center: map and layer controls.
- Right panel: ranked candidates and evidence.
- Bottom: observation/release timeline.

### Map layers

- SAR image.
- Detected slick polygon.
- Source probability heatmap.
- Particle paths.
- AIS trajectories.
- Ports/platforms/coastline.
- Optional future forecast.

### Required interactions

- Select a case.
- Run analysis.
- Toggle layers.
- Scrub the timeline.
- Select a vessel.
- View score breakdown.
- Reset/replay the case.

The SAR raster must be usable as a local base layer so the core demo still works without map tiles or internet access.

## 10. Ten-day schedule

### Day 1: Dependency gate

Complete:

```text
one accessible SAR/oil annotation
→ one spill polygon
→ one wind/current input
→ one drift simulation
→ three vessel trajectories
→ one candidate ranking
```

Exit criteria:

- Runs locally.
- Writes JSON/GeoJSON output.
- Produces a stable top candidate.
- Does not require a live API.

If this fails, use local forcing and synthetic tracks immediately.

### Days 2–3: Backend and drift

- Create Python environment.
- Add FastAPI skeleton.
- Define Pydantic schemas.
- Implement case loader.
- Implement particle movement.
- Implement source-hypothesis search.
- Export source heatmap and particle paths.

### Days 3–4: AIS and ranking

- Implement AIS cleaning.
- Add interpolation and gap flags.
- Calculate region/time/trajectory features.
- Implement weighted ranking.
- Generate explanations and warnings.

### Days 5–6: Frontend shell

- Create React/Vite app.
- Add case selection.
- Add Leaflet map.
- Add local raster and GeoJSON layers.
- Add candidate list and evidence panel.

### Days 6–7: Detection baseline

- Implement image normalization.
- Add dark-region detector.
- Add look-alike filtering.
- Evaluate against the validation case.
- Store a precomputed fallback result.

### Days 8–9: Integration and hardening

- Connect the Run Analysis button.
- Add loading and error states.
- Add fixed-seed reproducibility.
- Add golden-case tests.
- Verify offline replay.
- Capture screenshots and a backup demo recording.

### Day 10: Freeze and rehearse

- Freeze input data and dependencies.
- Run the complete demo repeatedly.
- Prepare architecture, data, limitation, and roadmap slides.
- Assign presenter and backup presenter.

## 11. Team ownership

### Geospatial/backend owner

- FastAPI.
- Case schemas.
- Drift simulation.
- Source reconstruction.
- GeoJSON output.

### Data/ML owner

- SAR preprocessing.
- Dataset provenance.
- Detection baseline.
- Detection evaluation.

### Frontend owner

- Map workspace.
- Timeline.
- Layer controls.
- Candidate evidence UI.

### Integration/presentation owner

- Golden case.
- End-to-end testing.
- Demo script.
- Slides and judge questions.
- Backup recording.

## 12. Testing plan

### Unit tests

Test:

- Coordinate validation.
- Geodesic distance.
- Polygon overlap.
- Particle advection.
- AIS interpolation.
- AIS gap detection.
- Score calculation.
- Explanation generation.

### Golden-case test

With the same input and seed, verify:

- The source region contains the expected source.
- The expected release window is recovered within tolerance.
- The expected vessel is ranked in the top three.
- The true vessel outranks the nearest distractor.
- The same run produces the same result.

### Acceptance thresholds for the internal demo

These are prototype quality gates, not scientific benchmarks:

- End-to-end run completes in under 30 seconds using cached/local inputs.
- Top candidate is stable across five repeated runs.
- True source falls inside the displayed high/medium source region.
- True simulated vessel ranks first or second.
- At least one deliberately introduced AIS gap is displayed as a warning.
- The UI remains usable without live API access.

## 13. Risk register and responses

| Risk | Response |
|---|---|
| Indian historical AIS is unavailable | Use simulated AIS for the controlled case and label it clearly |
| Live Sentinel download fails | Preload the complete case and keep ingestion optional |
| OpenDrift setup takes too long | Use the local particle simulator behind the same interface |
| Backtracking is too broad | Show a region and confidence band; reduce the search window |
| Dark SAR region is a look-alike | Show a look-alike validation case and environmental warnings |
| Timestamp mismatch | Use explicit tolerance windows and report them |
| AIS gap is misinterpreted | Show a data-quality warning, never a guilt claim |
| Demo network fails | Use local raster and cached JSON/GeoJSON results |
| Metrics overfit one scene | Split evaluation by scene or region where possible |
| Dataset licence is unclear | Do not redistribute the asset until the licence is confirmed |

## 14. Demo script

### Opening

“A dark patch in a satellite image is not enough to identify a polluter. OCEANTRACE connects the observed slick to environmental drift and vessel history, while showing uncertainty at every step.”

### Walkthrough

1. Select the controlled case.
2. Show the SAR image and detected candidate.
3. Run the analysis.
4. Show the estimated source region and release-time window.
5. Toggle on the three vessel tracks.
6. Show that the closest vessel is not the top lead.
7. Open the top candidate's evidence breakdown.
8. Point out an AIS-quality warning.
9. Show the limitation banner.
10. Close with the future authorised-data integration plan.

### Key message

> OCEANTRACE does not declare guilt. It turns uncertain satellite and maritime data into a reproducible, explainable investigation workflow.

## 15. Expected judge questions

### “What is novel?”

The underlying SAR, AIS, and drift techniques already exist. The prototype's contribution is their uncertainty-aware, explainable, reproducible integration for an India-focused investigation workflow.

### “Is the AIS data real?”

The Phase 1 controlled case uses labelled simulated AIS because unrestricted historical Indian AIS is not assumed to be publicly available. The architecture supports authorised AIS integration later.

### “Can this prove which ship caused the spill?”

No. It ranks investigative leads. Legal attribution requires additional evidence such as inspections, onboard records, or chemical fingerprinting.

### “What happens when the slick is not oil?”

The detector treats dark regions as candidates, includes look-alike filtering, and exposes uncertainty rather than treating darkness as proof of oil.

### “Why not use a large AI model?”

The first priority is a functioning, explainable end-to-end pipeline. A larger segmentation model can be evaluated after the data flow and ground-truth evaluation are stable.

## 16. Post-Phase 1 roadmap

1. Add more public annotated SAR scenes.
2. Train and cross-region-test a segmentation model.
3. Integrate real archived wind and current products.
4. Add forward validation from candidate vessel routes.
5. Add authorised Indian AIS integration.
6. Add platform, pipeline, port, and natural-seep source types.
7. Add calibrated uncertainty and verified historical cases.
8. Add live or semi-live Sentinel-1 ingestion.

## 17. Immediate next action

Create the first golden case and run the dependency gate before training any sophisticated model. The first successful output should be a local `AnalysisResult` containing:

- One candidate slick polygon.
- One source heatmap.
- Three vessel tracks.
- One ranked lead list.
- Human-readable reasons and warnings.
