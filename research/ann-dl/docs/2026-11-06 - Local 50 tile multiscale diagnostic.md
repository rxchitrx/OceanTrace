# Local 50-tile multiscale diagnostic

- **Date:** 2026-11-06
- **Participants:** Rachit; Codex
- **Source:** User redirected the authorized 50-patch experiment from Colab to the laptop after repeated Colab runtime disconnects.

## Scope and execution

Ran only the selected 50 unresolved SOS patches against the 21 original source scenes. Prepared a local bundle using checked patch hashes and links to existing raw source files; 40 available HH/HV and VV/VH channel views were opened. The search covered 19,590 distinct scene/window/scale/channel keys (1x, 1.625x, 2x, 4x) with the existing acceptance gates and two-thread OpenCV cap. Independent expected-key comparison found 19,590 completed, zero missing, zero extra.

Runtime environment was Python 3.12.12, OpenCV 5.0.0, NumPy 2.5.4, Rasterio 1.5.2. This differs from the Colab partial timing environment (OpenCV 4.11.0, NumPy 2.2.6, Rasterio 1.4.3), so outputs remain separate. Throughput near the end was about 4.09 windows/s; the earlier 45-minute estimate was optimistic.

## Results

- 17/50 tiles have one candidate location passing geometric/pixel gates (5 PALSAR, 12 Sentinel); 33/50 remain unknown or ambiguous.
- No patch ancestry was automatically verified. All 17 real candidates have only one retained distinct location; no second-location margin is available. They require manual review.
- All 4 generated positive controls localized to the expected scene within 8 native pixels, but only 1/4 passed all acceptance gates. The strict `recovered` field therefore reports 1/4. One resized/rotated PALSAR control failed coverage (0.087 vs 0.15 threshold); two Sentinel controls had 11 inliers vs the 12-inlier threshold.
- All 4 generated blank/noise negative controls were rejected (zero false accepts).
- Controls are generated from these same source scenes; they do not measure independent ancestry accuracy.

## Artifacts

- Full machine results, checkpoints, configuration, evidence images, report and review page: `Data/SOS/colab50/laptop-results-v1/`
- Local linked input bundle: `Data/SOS/colab50/laptop-bundle/`
- Experiment code: `Tools/sos-mapping/colab50.py`

## Next step

Manually inspect the 17 candidate panels in `candidate-review.html`. Treat them as hypotheses. Before extending the matcher to the other unresolved tiles, improve or justify the positive-control acceptance gates and add a meaningful competing-location/uniqueness check. No training, AIS processing, or full-corpus rerun was part of this session.
