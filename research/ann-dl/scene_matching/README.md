# SAR Scene Matching & Georeferencing (`scene_matching/`)

Reconstructs the exact source satellite scene, pixel coordinates, WGS84 latitude/longitude bounding box, and UTC acquisition timestamp for patches in the 8,070-patch **Deep-SAR Oil Spill (SOS)** dataset (14 ALOS PALSAR + 7 Sentinel-1A scenes).

## Key Verified Results
- **Strict-verified pixel-locked matches:** **3,605 / 8,070 (44.7%)** across **20 / 21** SAR scenes (`2,882` v2 ZNCC + `4` v3 strict mask-chain + `719` v4 cross-sensor), with **0 false accepts** on all negative controls.
- **Benchmark Audit Finding #1 (Scene Leakage):** **19 / 20** matched scenes appear in *both* the official SOS `train` and `val` splits.
- **Benchmark Audit Finding #2 (Cross-Sensor Mislabeling):** **719** patches labeled `sentinel_*` (`sentinel_1381..3353`) are pixel-exact ALOS PALSAR scenes from the Gulf of Mexico (`median native ZNCC = 0.9894`).
- **Leak-Free Split (`outputs/scene_disjoint_split.csv`):** **2,877 train / 728 val (20.2%)** with **0 shared scenes** (PALSAR `1,479 / 377`; Sentinel-1 `1,398 / 351`).

## Folder Layout
- `scripts/` — All scene-matching, geolocation, and MLflow logging scripts:
  - `run_diagnostic.py` — 50-patch pilot diagnostic (Round 1 & Round 2)
  - `run_full_v2.py` — Full 8,070-patch GPU/MPS multi-sigma ZNCC matcher
  - `run_mask_chaining_v3.py` — Scene-canvas mask-chaining pass
  - `run_v4_cross_sensor_and_denoised.py` — Cross-sensor (`sentinel_1381..3353` → PALSAR) + denoised pass
  - `georeference_matches.py` — ESA/JAXA WGS84 geolocation + leak-free split generator
  - `log_oceantrace_mlflow.py` — DagsHub / MLflow experiment logger
- `outputs/` — Final verified CSVs, leak-free split, and per-stage summaries (`pilot_50/`, `v2_zncc/`, `v3_mask_chain/`, `v4_cross_sensor/`).
- `visuals/` — Spot-check difference panels (`v3_spotcheck.jpg`, `v4_spotcheck.jpg`) and forensic ID-block audits.
- `EXPERIMENT_LOG.md` — Full chronological engineering log.
