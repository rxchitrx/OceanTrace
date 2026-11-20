# Full multiscale batch execution — 4 November 2026

Source: user authorized all 8,070 SOS tiles in batches using Luna medium without fast mode. Several delegates ended without implementing or completing the task; parent implemented batches.py, completed the 50-tile mixed-sensor check, and started the full process. finalize_batches.py verifies execution and stages SSD publication after the search.

# Full SOS multiscale run

All 8,070 split/name tiles received both pyramid-level searches against every compatible source scene: 167,258 actual new queries. Results combine new blind retrieval with preserved native candidates. No supplied tile was resized; proposed alignments were checked against native source pixels.

- Candidates needing review: 1854 (native-only run: 1541).
- Unknown/ambiguous: 6216.
- Automatically verified ancestry: zero.
- Pilot-derived regression candidates retained: 12/12.
- Completed scene/scale/batch files: 686.
- Stored batch computation time: 12136.3 seconds; excludes source-index construction and finalization.
- Independent checkpoint scan confirms exact compatible scene/scale coverage with no duplicate attempts.
- Negative controls: 168 queries across blank, noise and two block-shuffled SAR texture controls; 0 passed candidate gates. These are artificial controls, not an estimate of error rates on real SAR.

## Review boundary

Representative low/middle/high correlation evidence panels for both sensors are saved in the contact sheets. Manual visual review of this full-run selection is PENDING. A successful regression and conservative pixel/geometric gates do not prove every scene assignment. The 12 reference cases are tuning data, not independent provenance truth. Do not claim a verified full crosswalk or scene-disjoint split from this report.

## Outputs

results.json and results.csv contain every tile, candidate scene, native pixel corners/affine, scores and evidence paths. Original native results remain separate. Checkpoints retain each unsuccessful search too. Manifest fixes code/settings/IDs; repeat the same batches.py command to resume. summary.json and verification.json record execution and checks.

DVC publication success is appended below after the commands complete.

## SSD publication

`dvc add Data`, `dvc push` and `dvc status --cloud` completed successfully. Source Data.dvc updated. No Git commit/push performed.
