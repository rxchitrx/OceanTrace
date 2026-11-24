# OceanTrace v2 Scene Matching Summary (Full 8,070 SOS Dataset)

- **Total runtime:** 3064.9 s (`device=mps`, `mode=conv2d`)
- **Positive controls:** 4/4 passed (within 16 px)
- **Negative controls:** 4/4 rejected (0 false accepts)

## Recovery Rates
- **Total high-confidence:** **2882 / 8070 (35.7%)** (+ 53 review candidates)
- **PALSAR:** **1137 / 3877 (29.3%)** (+ 34 review)
- **Sentinel-1:** **1745 / 4193 (41.6%)** (+ 19 review)

## Train / Val Scene Overlap Audit (19/20 matched scenes appear in BOTH train and val)
| Scene | Train Matched | Val Matched | Shared? |
|---|---:|---:|:---:|
| `IW_GRDH_1SDV_017782_01DCBB_DE28` | 435 | 261 | YES |
| `IW_GRDH_1SDV_017848_01DEC1_EC32` | 278 | 155 | YES |
| `IW_GRDH_1SDV_017848_01DEC1_C09A` | 169 | 91 | YES |
| `ALPSRP241870520` | 185 | 44 | YES |
| `ALPSRP232970570` | 177 | 29 | YES |
| `IW_GRDH_1SDV_017855_01DEF7_F48C` | 133 | 72 | YES |
| `ALPSRP235450560` | 108 | 24 | YES |
| `ALPSRP231220560` | 95 | 20 | YES |
| `ALPSRP237930550` | 92 | 18 | YES |
| `IW_GRDH_1SDV_017884_01DFD8_8F93` | 58 | 33 | YES |
| `ALPSRP237930560` | 69 | 18 | YES |
| `ALPSRP231220580` | 68 | 4 | YES |
| `ALPSRP231220540` | 45 | 20 | YES |
| `ALPSRP232970580` | 56 | 0 | no |
| `ALPSRP230200560` | 38 | 14 | YES |
| `IW_GRDH_1SDV_017884_01DFD8_6CAE` | 19 | 11 | YES |
| `IW_GRDH_1SDV_017921_01EOED_DB39` | 19 | 11 | YES |
| `ALPSRP238660500` | 6 | 3 | YES |
| `ALPSRS233043050` | 1 | 1 | YES |
| `ALPSRS239753100` | 1 | 1 | YES |
