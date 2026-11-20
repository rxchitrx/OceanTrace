# SOS 50-patch matching pilot — results

Date: 2026-11-03

Paths below are relative to `Data/SOS/`.

## Actual execution
- 21/21 source raster exports exist; all source archives verified with ZIP CRC checks.
- 8,070/8,070 refined image patches extracted after Zenodo ZIP MD5 verification.
- Exactly 50 fixed real patches processed: 25 PALSAR and 25 Sentinel (40 train, 10 val).
- 12 candidate matches; 38 unknown; zero automatic scene assignments.
- Candidates are all PALSAR: 12/25; Sentinel: 0/25 candidates under this first method.
- Six synthetic software controls passed. These are not real-data accuracy measurements.

## Visual inspection
Parent inspected palsar_2396, palsar_1375 and palsar_280 image/source/difference panels. Their dark-region boundaries are visually consistent after alignment; brightness differs because of preprocessing. This supports these as plausible ancestry candidates, not a verified author-provided crosswalk. palsar_2396 has pixel correlation about 0.982; palsar_1375 about 0.878. Correlation is an image similarity statistic, not probability or mapping accuracy.

## Interpretation
The pilot gives evidence that automatic source recovery is feasible for at least some PALSAR chips. It has not established accuracy, broad coverage, Sentinel recovery, or scene-disjointness of the released splits. The 38 unknowns are unresolved, not proven absent from the scene inventory. Different sensor preprocessing/polarization, weak features, and filtering thresholds are possible causes; none has been demonstrated as the cause here.

No full-dataset matching was run. No training or broader preprocessing was performed.

## Files
- Browse.html: all 8,070 patches plus 21 source raster previews and TIFF links.
- pilot/results.json and results.csv: diagnostics and candidate pixel coordinates for all 50.
- pilot/*-candidate-comparison.png: patch, aligned source crop, absolute difference (left to right).
- metadata/raster_lineage.json: archived source member → raster export, band and shape.

## Next step
Review representative candidates with the user, then decide whether to improve the 50-patch method for Sentinel before any larger run. Source pixel coordinates still need geospatial validation before patch-level AIS joins; some exports have no CRS in their raster header, so source metadata/geolocation must be checked separately.

## Follow-up diagnostic — 2026-11-03
Three known-location 256×256 crops from Sentinel source IW_GRDH_1SDV_017855_01DEF7_F48C were tested against local 1024×1024 native tiles and the current 8192-wide whole-scene representation. All three native-tile controls registered with correlation 1.0; none registered against the shrunken whole scene. Source dimensions: 15842×25671; searched representation: 5055×8192; retained global SIFT keypoints: 25000 (the configured cap). This demonstrates a search-pipeline limitation on these controls. Resolution loss and global feature-budget/local-area differences are confounded, so neither is established as the sole cause of the real Sentinel failures. These controls are not new SOS patches, and the real pilot remains 12 candidates / 38 unknown. Native-tile searching within the same fixed pilot is the next proposed change; it has not been implemented or rerun yet. Diagnostic data: sentinel_scale_diagnostic.json.
