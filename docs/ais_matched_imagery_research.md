# AIS-Matched SAR Imagery Reference

Summary of which SAR oil-spill datasets in OceanTrace can be paired with free, public individual-vessel AIS tracks (MMSI, timestamp, lat/lon, SOG, COG) for trajectory reconstruction and demo validation.

## Pairing Summary

| Dataset / Incident | SAR Window & Region | Public AIS Availability | Verdict |
|---|---|---|---|
| **SOS PALSAR — Deepwater Horizon (2010)** | 14 ALOS PALSAR scenes, Gulf of Mexico (2010-05-21 to 2010-08-09) | [NOAA Marine Cadastre 2010 AIS](https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2010/index.html) (Zone 16 + Zone 15 monthly geodatabases, free, no login) | **Best real matched case.** Verified 1-minute vessel tracks around satellite pass times (see `ais_track_readiness.md`). |
| **SOS Sentinel-1 — Kuwait (Aug 2017)** | 7 Sentinel-1A scenes, Persian Gulf (2017-08-05 to 2017-08-14) | No free open archive for Persian Gulf 2017 (commercial or account-gated only) | **Case study only.** [SkyTruth](https://skytruth.org/blog/satellite-imagery-reveals-scope-of-last-weeks-massive-oil-spill-in-kuwait) and the [RUS Copernicus tutorial](https://eo4society.esa.int/wp-content/uploads/2022/01/OCEA03_OilSpill_Kuwait.pdf) document the exact 2017-08-10 scene (`017855_01DEF7_F48C`) and vessel DLB 1600 (MMSI `370129000`), but raw tracks are not publicly downloadable. |
| **Cantarell (2020)** | 173 Sentinel-1 tiles, Bay of Campeche (Jan–Sep 2020) | Unavailable — NOAA NAIS covers U.S. coastal waters only and excludes foreign EEZs | **Segmentation only.** |
| **DARTIS (2019)** | 3,655 Sentinel-1 patches, Eastern Mediterranean (2019) | Unavailable — [Piraeus AIS](https://doi.org/10.5281/zenodo.5562629) lies west of DARTIS (~23.7°E vs. 27–36°E); [EMODnet](https://emodnet.ec.europa.eu/en/human-activities) provides density rasters only | **Detection / hard-negative evaluation only.** |
| **Zenodo Sentinel-1 Parts I–III** | 3,020 global Sentinel-1 GeoTIFFs | No public scene-date manifest; U.S. scenes would need to be extracted from ~96.5 GB of GeoTIFF headers first | **Not pre-matched.** |

## Key Notes for the Deepwater Horizon (2010) Matched Demo

- **Data format & fields:** NOAA 2010 archives are ESRI File Geodatabases (`.gdb`, readable with GDAL / `geopandas`) containing `Broadcast` (`Shape` WGS84 point, `BaseDateTime`, `MMSI`, `SOG`, `COG`, `Heading`, `Status`), `Voyage`, and `Vessel` tables.
- **Caveats to state clearly:**
  - **Stationary well blowout:** DWH (lat `28.7367`, lon `-88.3872`, [NOAA IncidentNews #8220](https://incidentnews.noaa.gov/raw/incidents.csv)) was a well blowout, not a vessel-discharge spill. Co-located AIS tracks validate SAR–AIS alignment, gap reconstruction, and false-lead rejection — not vessel guilt.
  - **Scrambled MMSIs (2009–2014):** NOAA scrambled MMSI numbers consistently per vessel in 2010; they still work as stable track IDs for splitting and LSTM modeling.
  - **Offshore receiver range:** NOAA terrestrial NAIS stations cover ~40–50 miles offshore ([NOAA AIS FAQ](https://coast.noaa.gov/data/marinecadastre/ais/faq.pdf)), so deep-offshore frames are sparser than coastal frames.

## Standalone AIS Sources for LSTM Training

- **[NOAA Marine Cadastre 2020+ daily CSVs](https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/index.html):** Cleanest schema (`MMSI, BaseDateTime, LAT, LON, SOG, COG, Heading, VesselName, IMO, Status, ...`), ~320 MB compressed per day.
- **[NARI Brest AIS (Zenodo, CC BY 4.0)](https://doi.org/10.5281/zenodo.2563256):** Open Atlantic vessel trajectories for standalone trajectory benchmarking.
- **[Piraeus AIS (Zenodo)](https://doi.org/10.5281/zenodo.5562629):** 244M records (2017–2019, Saronic Gulf), anonymized vessel IDs; verify CC BY 4.0 vs. CC BY-NC-SA 4.0 terms before redistribution.
