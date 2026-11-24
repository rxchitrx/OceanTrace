# Scene Matching Diagnostic Summary (Round 2 Consolidated)

- **Method:** Log-despeckled coarse-to-fine ZNCC (`cv2.matchTemplate` TM_CCOEFF_NORMED) across all 21 full-resolution DVC SAR scenes (14 ALOS PALSAR HH, 7 Sentinel-1A VV), dense intermediate footprints (`256, 268, 274, 322, 416, 520 px`), 90°/D4 orientations, multi-sigma (`sigma=4.0` + `sigma=1.2`) native-resolution refinement with local scale sweep, and Peak-to-Second-Best uniqueness margin.

## Controls
- **Positive controls:** 4/4 localized within 16 px & passed gates
- **Negative controls:** 4/4 rejected under both Round 1 and Round 2 dense-scale grids (zero false accepts)

## Real 50-Patch Pilot Results
| Pipeline | PALSAR (25) | Sentinel-1 (25) | Total (50) | False Accepts (4 Neg Controls) |
|---|---:|---:|---:|---:|
| Prior SIFT Pilot | 12 (48%) | 0 (0%) | 12 (24%) | 0/4 |
| Round 1 Despeckled ZNCC (`256/416/512/1024 px`) | 14 (56%) | 8 (32%) | 22 (44%) | 0/4 |
| **Round 2 Dense-Scale + Multi-Sigma ZNCC** | **14 (56%)** | **13 (52%)** | **27 (54%)** | **0/4** |

## Newly Recovered Matches in Round 2 (+5 Sentinel-1, all visually verified)
- `sentinel_423` (`train`) -> `IW_GRDH_1SDV_017884_01DFD8_8F93` (`fp=268 px`, `rot270`, native ZNCC `0.9520`, raw `0.8502`)
- `sentinel_121` (`train`) -> `IW_GRDH_1SDV_017884_01DFD8_8F93` (`fp=268 px`, `rot270`, native ZNCC `0.9093`, raw `0.7496`)
- `sentinel_628` (`val`) -> `IW_GRDH_1SDV_017782_01DCBB_DE28` (`fp=274 px`, `rot180`, native ZNCC `0.9712`, raw `0.8710`)
- `sentinel_697` (`train`) -> `IW_GRDH_1SDV_017782_01DCBB_DE28` (`fp=274 px`, `rot180`, native ZNCC `0.9697`, raw `0.8967`)
- `sentinel_755` (`val`) -> `IW_GRDH_1SDV_017848_01DEC1_C09A` (`fp=322 px`, `rot180`, native ZNCC `0.9297`, raw `0.7928`)

Full experimental rationale, failed probes, and forensic findings are documented in `EXPERIMENT_LOG.md`.
