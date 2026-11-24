# OceanTrace — Georeferenced Matches & Leak-Free Scene-Disjoint Split Summary

- **Total verified georeferenced patches:** **3605 / 8,070 (44.7%)** (`2,882` from v2 ZNCC + `4` strict-verified `sigma=1.2 >= 0.90` from v3 + `719` cross-sensor mislabeled `sentinel_1381..3353` -> PALSAR from v4)
- **Geolocated scenes:** **20 / 21** archived SAR scenes (all 7 Sentinel-1 + 13 PALSAR)
- **PALSAR center-coordinate validation:** Max discrepancy between KML 4-corner bilinear center and JAXA `workreport` scene center = `0.00766°` (~< 1 km across 70 km swath)
- **Sentinel-1 geolocation:** Exact bilinear interpolation on official ESA `geolocationGridPointList` (`line, pixel -> WGS84 lat, lon`)

## Leak-Free Scene-Disjoint Split (`scene_disjoint_split.csv`)
- **Shared scenes between train and val:** **0** (vs. **19 / 20** shared scenes in the official SOS split!)
- **PALSAR (true matched sensor):** `1479` train (10 scenes) / `377` val (3 scenes — `20.3%`)
- **Sentinel-1 (true matched sensor):** `1398` train (5 scenes) / `351` val (2 scenes — `20.1%`)
- **Total:** `2877` train / `728` val (`20.2%`)

## Matched Scenes Inventory (with UTC Acquisition Time & Geographic Center)
| Scene | Sensor | Matched Patches | UTC Acquisition Time | Center (Lat, Lon) | Disjoint Split |
|---|---|---:|---|---|---|
| `IW_GRDH_1SDV_017782_01DCBB_DE28` | Sentinel-1 | 697 | `2017-08-05T02:39:21.777410` | `27.239, 49.481` | train |
| `IW_GRDH_1SDV_017848_01DEC1_EC32` | Sentinel-1 | 436 | `2017-08-09T14:41:48.542488` | `27.956, 50.450` | train |
| `ALPSRP232970570` | PALSAR | 366 | `2010-06-09T04:20:38Z` | `29.223, -87.056` | **VAL (held-out)** |
| `ALPSRP241870520` | PALSAR | 358 | `2010-08-09T04:38:35Z` | `26.749, -91.371` | train |
| `IW_GRDH_1SDV_017848_01DEC1_C09A` | Sentinel-1 | 260 | `2017-08-09T14:42:13.542389` | `29.463, 50.136` | **VAL (held-out)** |
| `ALPSRP235450560` | PALSAR | 212 | `2010-06-26T04:22:28Z` | `28.727, -87.488` | train |
| `IW_GRDH_1SDV_017855_01DEF7_F48C` | Sentinel-1 | 205 | `2017-08-10T02:47:14.363446` | `28.526, 47.687` | train |
| `ALPSRP231220560` | PALSAR | 185 | `2010-05-28T04:24:54Z` | `28.727, -88.026` | train |
| `ALPSRP237930550` | PALSAR | 182 | `2010-07-13T04:24:18Z` | `28.233, -87.926` | train |
| `ALPSRP231220580` | PALSAR | 153 | `2010-05-28T04:25:10Z` | `29.723, -88.229` | train |
| `ALPSRP232970580` | PALSAR | 140 | `2010-06-09T04:20:46Z` | `29.721, -87.155` | train |
| `ALPSRP237930560` | PALSAR | 124 | `2010-07-13T04:24:26Z` | `28.728, -88.024` | train |
| `IW_GRDH_1SDV_017884_01DFD8_8F93` | Sentinel-1 | 91 | `2017-08-12T02:30:55.404598` | `27.983, 51.684` | **VAL (held-out)** |
| `ALPSRP231220540` | PALSAR | 65 | `2010-05-28T04:24:38Z` | `27.738, -87.821` | train |
| `ALPSRP230200560` | PALSAR | 58 | `2010-05-21T04:35:42Z` | `28.734, -90.707` | train |
| `IW_GRDH_1SDV_017884_01DFD8_6CAE` | Sentinel-1 | 30 | `2017-08-12T02:31:20.405174` | `26.474, 51.384` | train |
| `IW_GRDH_1SDV_017921_01EOED_DB39` | Sentinel-1 | 30 | `2017-08-14T14:50:06.047956` | `28.167, 48.349` | train |
| `ALPSRP238660500` | PALSAR | 9 | `2010-07-18T04:30:00Z` | `25.758, -89.029` | **VAL (held-out)** |
| `ALPSRS233043050` | PALSAR | 2 | `2010-06-09T16:25:30Z` | `28.389, -88.302` | **VAL (held-out)** |
| `ALPSRS239753100` | PALSAR | 2 | `2010-07-25T16:25:45Z` | `25.711, -88.870` | train |
