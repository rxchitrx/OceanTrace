# OceanTrace Phase 1 Implementation Plan and Completion Record

## 1. Goal

Deliver a reliable 5–7 minute internal-college SIH demonstration for problem statement SIH26143:

```text
Satellite observation
        ↓
Candidate slick detection
        ↓
Uncertainty-aware source reconstruction
        ↓
AIS trajectory correlation
        ↓
Explainable investigative leads
```

The prototype must be deterministic, run from local case files, distinguish real and synthetic inputs, and avoid legal-attribution claims.

## 2. Phase 1 definition of done

A reviewer must be able to:

1. Start the API and dashboard locally.
2. Open one complete end-to-end controlled case.
3. View a SAR raster and candidate slick outline.
4. execute pixel-based detection.
5. Reconstruct a source region and release window.
6. View at least three AIS vessel tracks.
7. See a stable, evidence-based ranking.
8. Inspect numerical components, reasons, and warnings.
9. Run a separate real-SAR detector validation case.
10. Re-run the same seed and receive the same result.
11. Complete the automated test and production-build checks.

## 3. Scope boundary

### Included and complete

- Local controlled Arabian Sea case.
- Real Sentinel-1-derived DARTIS validation patch.
- Classical, explainable SAR dark-region detector.
- Pascal VOC bounding-box evaluation.
- Wind/current/windage particle ensemble.
- Reverse source hypotheses plus independent forward validation.
- AIS cleaning, short-gap interpolation, and long-gap warnings.
- Five-component transparent vessel ranking.
- FastAPI case/result API.
- Responsive React/Leaflet investigation console.
- Explicit provenance and legal/scientific limitations.
- Unit, integration, API, and deterministic golden-case tests.

### Explicitly deferred

- Live Sentinel-1 ingestion.
- Live or restricted Indian AIS access.
- Operational ERA5, Copernicus Marine, or INCOIS ingestion.
- Learned segmentation model training.
- Oil-weathering chemistry.
- Ports, platforms, pipelines, and natural-seep candidate sources.
- Authentication, multi-user storage, cloud deployment, and audit logging.
- Calibrated attribution probability or legal responsibility assessment.

## 4. Delivered system

```text
┌─────────────────────────────────────────────┐
│ React investigation console                 │
│ case · map layers · timeline · explanations │
└────────────────────┬────────────────────────┘
                     │ JSON / GeoJSON
┌────────────────────▼────────────────────────┐
│ FastAPI orchestration and Pydantic contracts│
└────────┬────────────────┬───────────────────┘
         ▼                ▼
  SAR detector      controlled full case
  + VOC metric       ├─ particle ensemble
                     ├─ AIS features
                     └─ evidence ranking
                              │
                              ▼
                  deterministic result JSON
```

### Storage

- Inputs: `data/cases/<case_id>/`
- Generated results: `generated/<case_id>-seed-<seed>.json`
- No database or network data service is required.

## 5. Data contracts

### Case manifest

Each `case.json` records:

- Stable case identifier and observation time.
- SAR image and geographic bounds.
- Reference polygon and optional annotation.
- Optional forcing and AIS paths.
- Scenario, AIS, and forcing types.
- CRS and fixed random seed.
- Human-readable notes and data sources.

Two modes are supported:

| Scenario type | Analysis mode | Required inputs |
|---|---|---|
| `controlled_demo` | `full` | image, bounds, polygon, wind, current, AIS |
| `detection_validation` | `detection_only` | image, bounds, polygon, annotation |

### Analysis result

Every result includes:

- `run_id`, mode, seed, case metadata, and warnings.
- Detector polygon, method, score, and pixel features.
- Optional reference-annotation evaluation.
- Optional release window, source region, particles, and vessel list.
- Input data-source metadata and drift diagnostics.

## 6. Implementation details

### 6.1 Detection

Implemented in `services/api/detection/baseline_detector.py`:

1. Convert the image to grayscale and median-filter speckle.
2. Normalize with the 1st and 99th percentiles.
3. Estimate local signal and broad background.
4. Threshold positive local darkness adaptively.
5. Remove borders and apply close/open/fill morphology.
6. Extract connected components.
7. Measure area, perimeter, fill ratio, elongation, orientation, intensity, and contrast.
8. Score and georeference the strongest coherent candidate.
9. For labelled cases, compare its pixel bbox with oil-object bboxes from Pascal VOC XML.

The heuristic confidence is not called an oil probability.

### 6.2 Drift and source search

Implemented in `services/api/drift/`:

- Forcing inputs declare `m/s` units and uncertainty.
- Advection converts metre displacement to latitude/longitude using Earth radius and latitude correction.
- The controlled case uses five release hours, three windage values, and twelve perturbations: 180 hypotheses.
- A fixed random seed makes perturbations reproducible.
- Each hypothesis starts from a reverse-advection source estimate.
- Independent forward advection measures whether it reaches the observed slick.
- Weighted hypotheses generate the centroid, covariance-based probability regions, heatmap, release band, and representative paths.

### 6.3 AIS processing

Implemented in `services/api/ais/`:

- Parse and validate timestamps, coordinates, speed, and course.
- Remove duplicate records and sort by vessel/time.
- Group tracks and interpolate only bounded short gaps.
- Preserve long gaps for evidence warnings.
- Interpolate vessel position at each candidate release time.
- Compute source distance, bearing/course compatibility, release coverage, and trajectory consistency.

### 6.4 Ranking

Implemented in `services/api/ranking/`:

```text
origin_region_overlap  0.35
release_time_match     0.20
drift_consistency      0.25
trajectory_heading     0.10
ais_data_quality       0.10
```

Forward drift begins from the vessel's actual interpolated position at a candidate release time. The scorer compares the result with the observed slick and returns a `0–100` lead score with reasons and warnings.

### 6.5 API

Implemented routes:

```text
GET  /api/health
GET  /api/cases
GET  /api/cases/{case_id}
GET  /api/cases/{case_id}/sar/image
GET  /api/cases/{case_id}/sar/bounds
POST /api/cases/{case_id}/run
GET  /api/cases/{case_id}/results/{run_id}
```

Case IDs are path-safe, request seeds are bounded, missing resources return 404, invalid cases return 422, and results can be retrieved by arbitrary seed or `latest`.

### 6.6 Frontend

Implemented in `apps/web/`:

- Case selector with full and detection-only workflows.
- Local SAR image overlay and reference/detected polygons.
- Source probability regions and representative particle paths.
- AIS routes linked to ranked candidates.
- Functional release-window scrubber.
- Weighted score breakdown, reasons, and warnings.
- Detector metric panel for the DARTIS case.
- Honest loading and failure states with no silent fake-data fallback.
- Relative API URL with an optional `VITE_API_BASE_URL` override.
- Responsive layouts and keyboard focus styling.

## 7. Verification matrix

| Acceptance criterion | Automated check | Expected evidence |
|---|---|---|
| Detector uses pixels | `tests/test_detector.py` | Changed pixels change the detected candidate |
| Real annotation comparison | `tests/test_detector.py` | DARTIS bbox IoU ≥ 0.90 |
| Correct physical units | `tests/test_drift.py` | 1 m/s produces about 3.6 km in one hour |
| Determinism | drift and golden tests | Same seed produces identical output |
| Seed sensitivity | `tests/test_drift.py` | Different seed changes perturbations |
| Correct ensemble size | `tests/test_golden_case.py` | 180 source hypotheses |
| Expected release band | `tests/test_golden_case.py` | 03:00–09:00 UTC |
| Ranking is evidence-based | `tests/test_ranking.py` | True source vessel beats nearer distractor by >20 points |
| AIS limitation visible | ranking/golden tests | Long-gap warning on Vessel C |
| API result retrieval | `tests/test_api.py` | Non-default seed returns successfully |
| Detection-only isolation | `tests/test_api.py` | No source region or vessels returned |
| Frontend compiles | `npm run build` | TypeScript and Vite production build succeed |
| Live controlled flow | browser smoke check | 94.0 / 56.8 / 9.8 ranking displayed |
| Live DARTIS flow | browser smoke check | 0.965 IoU and no attribution UI displayed |

## 8. Reference acceptance result

With seed `26143`, the controlled case must retain these stable demo properties:

```text
analysis mode:           full
ensemble hypotheses:     180
release window:          03:00–09:00 UTC
top vessel:              vessel_a / MV Ocean Star
top score:               94.0
nearest distractor:      vessel_b / MV Coastal Trader
distractor score:        56.8
long-gap vessel warning: present for vessel_c
```

The DARTIS case must retain:

```text
analysis mode:           detection_only
input asset:             DARTIS_2019 ow-0010
reference objects:       2
best bbox IoU:           0.9647
vessel ranking:          absent by design
```

## 9. Demo runbook

### Before judging

1. Install locked Python and npm dependencies.
2. Validate both case folders.
3. Run the Python tests and frontend production build.
4. Start FastAPI and Vite.
5. Run both cases once in the UI.
6. Keep `generated/` results available as a local backup.
7. Avoid dependency upgrades after the rehearsal freeze.

### Five-to-seven-minute walkthrough

1. Open the Arabian Sea case and identify all inputs as controlled.
2. Explain why the nearest vessel at observation time is not sufficient.
3. Run the analysis.
4. Show the detected slick, source probability region, 180 hypotheses, and release window.
5. Select each vessel and compare evidence components.
6. Point out Vessel C's AIS-gap warning.
7. Switch to the DARTIS case.
8. Run detection and show the real labelled SAR patch and IoU.
9. Close with the visible legal/scientific limitation.

## 10. Judge-question boundaries

### Is the AIS real?

No. The Phase 1 end-to-end case uses clearly labelled simulated AIS so ranking behavior has known ground truth. The interface and schema are ready for authorised AIS integration.

### Does the system prove responsibility?

No. It produces investigative leads. Operational attribution requires incident review and independent evidence such as inspections, logs, samples, and chemical fingerprinting.

### Is the detector an AI model?

The Phase 1 detector is a transparent classical computer-vision baseline. This makes the complete workflow reproducible and debuggable. A learned segmentation model is a Phase 2 comparison, not a hidden Phase 1 dependency.

### Is 0.9647 IoU the overall model accuracy?

No. It is the best bounding-box overlap on one bundled DARTIS patch. Dataset-wide scene-level validation remains future work.

### What is the contribution?

The underlying techniques are established. OceanTrace's prototype contribution is an uncertainty-aware, explainable integration that links a pixel-derived slick candidate to physical drift reconstruction and vessel-history evidence.

## 11. Remaining risks

| Risk | Current control | Phase 2 action |
|---|---|---|
| SAR look-alikes | Candidate wording and real labelled validation | Add multi-scene oil/look-alike benchmark |
| Simplified forcing | Units, uncertainty, and clear synthetic labels | Integrate archived gridded wind/current products |
| AIS incompleteness | Gap warnings and quality score | Test authorised terrestrial/satellite AIS feeds |
| Single controlled incident | Golden-case assertions | Add incidents and region-held-out evaluation |
| Basemap network loss | Local SAR and analysis remain available | Package optional offline coastline tiles |
| Uncalibrated lead scores | Evidence-score wording | Calibrate only after a representative incident set exists |

## 12. Phase 2 roadmap

1. Add oil and look-alike scenes with scene-level train/validation/test splits.
2. Compare the classical detector with a compact segmentation model.
3. Add archived ERA5/Copernicus Marine or approved INCOIS forcing adapters.
4. Integrate authorised AIS through a replaceable ingestion adapter.
5. Add ports, platforms, pipelines, natural seeps, and non-vessel source priors.
6. Model slick spreading and weathering over longer incidents.
7. Add run persistence, user authentication, audit trails, and report export.
8. Validate uncertainty calibration with reviewed historical incidents.

## 13. Completion statement

The scoped **SIH internal-college Phase 1 prototype is complete** when the commands in the README pass and both live case workflows match the verification matrix above. This statement does not imply production, scientific-certification, or legal-attribution readiness.
