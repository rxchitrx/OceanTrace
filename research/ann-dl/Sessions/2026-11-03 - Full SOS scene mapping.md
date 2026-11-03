# Full SOS scene mapping

- Date: 2026-11-03
- Source: User-authorized implementation task for all 8,070 SOS patches.
- Implemented: Began resumable native-tile SIFT search in `Tools/sos-mapping/run.py`; checkpoint in `Data/SOS/full_mapping/STATUS.md`.
- Execution: Attempted using system `python3`; unavailable dependency `cv2` stopped run before any patch searches. Zero attempted; no findings.
- Open work: locate project Python environment/dependencies, correct patch sensor metadata routing, finish candidate validation/evidence/CSV and controls, then run and inspect results.

## Parent completion — 2026-11-04
The earlier delegate checkpoint below/above is historical. Parent used the existing .venv312 (OpenCV/rasterio already installed), replaced the draft brute-force search with native tiled per-scene SIFT indexes/FLANN approximate retrieval, and executed all8,070distinct split/name keys against14or7compatible scene indexes. Finalnative results:1,541candidates(557PALSAR,984Sentinel),6,529unknown/ambiguous,zeroautomaticassignments. Fulloutputs: Data/SOS/full_mapping/results.json, results.csv, summary.json, verification.json, REPORT.md and Review.html. Sourceindexescheckpointed on disk; no newsource downloads or modeltraining.
Verification:12known-location/rotation positive controls,4negativecontrols; per-recordattempt/uniqueness/threshold/evidence checks;6representative candidateimages visually inspected. Sevenof12pilot candidates were missed bynative retrieval even though directnative-coordinate recheck supports their imagesimilarity; retainpilot artifacts and reportincomplete recall. Unknowns are notproof of absent parent scenes. Scoresarenotprobabilities andnoindependentancestryaccuracy isestablished. Nofullscene-disjointSOSsplit canbeclaimedwhileunknowntrainingpatchesremain.
