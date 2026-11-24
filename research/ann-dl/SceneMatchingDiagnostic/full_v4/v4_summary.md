# OceanTrace v4 Cross-Sensor & Denoised PALSAR Summary

- **Runtime:** 567.3 s (`device=mps`, `mode=conv2d`)
- **Positive controls:** 3/3 passed
- **Negative controls:** 4/4 rejected (0 false accepts)

## New Verified Matches Recovered by v4
- **Total NEW verified matches:** **+719**
  - Cross-sensor (`sentinel_1381..3353` -> ALOS PALSAR): **+719** (strict=719, denoised=0)
  - Denoised PALSAR (`palsar_train` + `palsar_val`): **+0** (strict=0, denoised=0)

## Cumulative Verified Coverage (All 8,070 SOS Patches)
- **Before v4 (v2 + v3 strict):** 2911 / 8,070 (36.1%)
- **After v4:** **3630 / 8,070 (45.0%)**

## Top Matched PALSAR Scenes in v4
| Scene | New Matches |
|---|---:|
| `ALPSRP232970570` | 160 |
| `ALPSRP241870520` | 129 |
| `ALPSRP232970580` | 84 |
| `ALPSRP231220580` | 81 |
| `ALPSRP235450560` | 80 |
| `ALPSRP237930550` | 72 |
| `ALPSRP231220560` | 70 |
| `ALPSRP237930560` | 37 |
| `ALPSRP230200560` | 6 |
