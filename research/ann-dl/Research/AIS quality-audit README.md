# AIS preprocessing — first quality pass

Completed 4 November 2026. Scope: read-only audit of the previously filtered NOAA northern-Gulf 2020-07-01 subset. One row is a retained position report for one MMSI and UTC timestamp. This does not re-audit the full national archive.

## Findings and implications

- 2,228,788 reports across 3,359 MMSI groups reconciled with the acquisition audit. Field-quality partitions reconcile to the full report count, and the per-vessel output totals reconcile independently.
- Missing-value codes: 1,175 SOG values, 108,789 COG values and 1,159,706 heading values. One additional heading is outside range. These fields need explicit unavailable-value handling before constructing inputs. Missing heading does not invalidate an otherwise valid position.
- 18 SOG values are upper-coded 102.2 knots (at least 102.2, not an exact continuous measurement). They are kept separate from unavailable 102.3.
- 642 consecutive-position edges, with positive interval at most 300 seconds, imply speeds above a provisional 60-knot inspection threshold. These are review flags, not proven invalid records, and two adjacent flags can be caused by a single bad point.
- Example: MMSI 367590950 jumps about 21.8km away between 23:04:55 and 23:06:51 UTC, then returns by 23:07:55. The first implied speed is about 366 knots. The positional pattern warrants inspection; no automatic deletion was performed.
- 1,298,881 reported speeds are exactly zero. These remain observations, not missing AIS. The <=0.5-knot count is a descriptive category, not a vessel-selection rule.
- 74,749 positive inter-report intervals exceed five minutes. This is the previously filtered regional subset; gaps may include missing reception or leaving the chosen region. No claim of deliberate AIS shutdown or exact vessel location within gaps.
- The already explored MMSI 368000510 has 1,143 reports, no unavailable SOG/COG/heading codes and no >60-knot short-edge flags in this pass. Its stops are retained.

## What changed

Only diagnostic outputs were added. The input CSV and archive were opened read-only. No rows removed, missing values filled, positions interpolated, resampling performed, scaling fitted, splits chosen, training sequences created or models trained. This is the first preprocessing stage, not a finished training dataset.

## Evidence and verification

- `Data/AIS/quality-audit/summary.json`: exact field counts, interval/speed summaries, assumptions and source links.
- `Data/AIS/quality-audit/vessel-profile.csv`: one row per MMSI group.
- `Data/AIS/quality-audit/flagged-edge-sample.csv`: all 642 flagged edges (below the configured 2,500-example cap).
- The reproducible streaming-check script was retired after this audit.
- Known one-degree spherical-distance control, zero/sentinel boundary checks, and an independent spherical-law-of-cosines recomputation for the first flagged edge passed. This verifies calculations, not true vessel trajectories.

## Source semantics

[NOAA dictionary](https://coast.noaa.gov/data/marinecadastre/ais/data-dictionary.pdf) describes the 2018–2024 columns, units and UTC timestamps. [AISHub's primary API documentation](https://www.aishub.net/api) documents human-readable unavailable codes. [ITU-R M.1371-1](https://www.itu.int/dms_pubrec/itu-r/rec/m/R-REC-M.1371-1-200108-S%21%21PDF-E.pdf) documents the upper-coded SOG convention. These conventions guide diagnostics; the downloaded file remains the evidence for actual observed values.

## Next hands-on step

Inspect a short vessel track around one flagged jump, understand the failure, then choose and document cleaning rules. Preserve a flag/reason trail before deciding how to handle any points. Resampling and train/validation/test grouping follow after that review. The 2020 AIS remains separate from the 2010/2017 SOS scenes.
