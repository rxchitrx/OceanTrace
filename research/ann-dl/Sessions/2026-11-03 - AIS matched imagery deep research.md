# 2026-11-03 — AIS matched imagery deep research

**Date:** 2026-11-03
**Participants:** User (task owner); research sub-agent (GLM 5.3, max effort, no further delegation)
**Source:** User-requested exhaustive internet research for usable AIS data matched to OceanTrace imagery.
**Scope:** Individual-vessel timestamped AIS positions (MMSI, timestamp, lat/lon, SOG/COG) suitable for LSTM missing-track reconstruction, ideally time/location-matched to our SAR cases: SOS PALSAR Gulf of Mexico May–Aug 2010, SOS Sentinel Persian Gulf Aug 5–14 2017, Cantarell Jan–Sep 2020, DARTIS Eastern Mediterranean 2019, Zenodo Parts I–III.
**Constraints honored:** No account creation, no purchases, no author/agency contact, no agreement acceptance, no bulk/annual archive downloads. Largest fetches this session: DARTIS PANGAEA data table (2.4 MB), IncidentNews `incidents.csv` (3.2 MB), RUS Copernicus tutorial PDF (1.9 MB), NOAA FAQ/data-dictionary PDFs, and HTTP range-reads of ≤512 KB against public NOAA/SJTU ZIPs to inspect headers/central directories. No secret exposure.

Related: [[2026-11-03 - SOS provenance deep search]] · [[2026-11-03 - Original SOS share inspection]] · [[2026-11-03 - Additional datasets deep search]]

---

## Qualification after parent review — 2026-11-03

**DWH is a candidate pairing, not yet a verified per-vessel SAR–AIS match.** Exact scene footprints/times and matching month/zone archives were identified; schemas and archive access were checked. No empirical AIS point counts or continuous tracks within the scene footprints/time windows were extracted. Thus “confirmed matched,” “genuinely co-located,” and “fully open real case” below refer only to a promising catalogue/archive overlap and overstate usable row-level evidence. Coverage density, temporal continuity and track quality still need validation. Anonymous SOS chip-to-scene membership is also still unresolved.

No accessible raw AIS was found for the other regions in this search. This does not prove that open AIS does not exist or that matching is impossible. Account-gated access is an access step, not inherently unusable; the user has since demonstrated willingness to create research accounts for SAR access. Claims that scene/time metadata definitely exists inside Parts I–III TIFFs are unverified without archive inspection. “Dataset/images in hand” in the research table means source records identified, not downloaded imagery; current downloads are tracked separately.

DWH is a stationary-well spill. Nearby AIS tracks could test data alignment, gap reconstruction and rejection of spurious vessel associations; they do not provide positive ground truth for vessel-caused oil release. Earlier candidate-vessel ranking suggestions must retain that distinction.

## Executive finding (ranked practical verdict)

1. **CONFIRMED matched real case — Deepwater Horizon 2010 (SOS PALSAR subset + NOAA Marine Cadastre 2010 AIS).** This is the only fully open, genuinely co-located SAR↔AIS pairing found. The 14 SOS PALSAR scenes are DWH-spill-window acquisitions over the northern Gulf of Mexico (2010-05-21 → 2010-08-09; all 14 scene IDs now verified in NASA CMR with exact UTC acquisition times and footprints). NOAA's 2010 AIS archive for the matching months/zones is live, free, and downloadable without an account (verified by HTTP HEAD + range-read schema extraction). Caveats: 2010 data is ESRI file-geodatabase format (needs GDAL), MMSIs are scrambled 2009–2014 (official unscramble tool exists), and the DWH wellhead sits ~40–50 mi offshore at the edge of nominal terrestrial receiver range — local density must be verified after a bounded download. DWH's source was a known stationary well blowout, so this case validates the SAR→drift→AIS pipeline geolocation, **not** vessel-attribution.
2. **PARTIAL match — Kuwait, August 2017 (SOS Sentinel subset).** The SOS Persian Gulf scenes are the documented Al Khiran (Ras Al-Zour) Kuwait spill of 2017-08-10. The RUS Copernicus training tutorial uses the *exact* SOS scene `S1A_IW_GRDH_1SDV_20170810T024714_..._017855_01DEF7_F48C`, and SkyTruth's contemporaneous analysis places named suspect pipelay vessel **DLB 1600 (MMSI 370129000, IMO 9681651)** at the north end of the slick on Aug 10 and again on Aug 14 (both SOS scene dates), with an AIS-derived eastward track since Aug 5. **No open AIS archive covers the Persian Gulf 2017** → raw tracks cannot be reconstructed under our constraints. Use as a documented case study with citations, not as an AIS data source. SkyTruth explicitly states the spill's source/cause was uncertain; SAR coincidence does not prove the culprit.
3. **BLOCKED — Cantarell 2020 (Bay of Campeche, Mexican EEZ).** NOAA AIS is land-based USCG NAIS only, explicitly unavailable for foreign waters, with no satellite AIS. No open individual-vessel AIS exists for Mexican waters. Cantarell stays a segmentation-only dataset (acquisition mapping is with the separate agent).
4. **BLOCKED — DARTIS 2019 Eastern Mediterranean.** The PANGAEA table (verified) carries perfect join keys (full Sentinel-1 product ID + start/stop UTC + patch corner coordinates per patch), but no open individual-vessel AIS covers the E. Med in 2019: the Piraeus dataset is Saronic-Gulf-only and lies **outside** DARTIS's geographic extent (verified), EMODnet vessel density is aggregate rasters (verified), GFW needs an account and is aggregated.
5. **NOT pre-matched — Zenodo Sentinel-1 Parts I–III.** The public records expose no scene IDs or acquisition dates; those live inside the ~96.5 GB georeferenced TIFFs. US-origin scenes could in principle be joined to Marine Cadastre AIS (2015+) after per-image inspection, but this is not a practical matched source this sprint.
6. **LSTM benchmark (separate from matching):** rank NOAA slices (2020 daily national CSVs are the easiest — pure CSV, verified schema; or the same 2010 GoM slice for dual use) > Piraeus 2019 (large/dense, anonymized IDs, license discrepancy) > EnvShip-Voyage (ready-made gap masks; license still undeclared) > Danish DMA (known-good, license unclear).

**Bottom line:** no public dataset pairs oil-slick SAR with co-located AIS tracks out of the box. The DWH 2010 window is the best feasible real case and is now fully pinned at scene level (exact times + footprints + AIS file URLs). The Kuwait 2017 case supplies a documented suspect-vessel identity but no accessible track. Recommend: build the matched demo on DWH, tell the Kuwait story with citations, and benchmark the LSTM on NOAA AIS separately.

---

## New hard evidence produced this session

### A. Exact acquisition windows for all 21 SOS source scenes (NASA CMR, open API)

All 14 PALSAR scenes resolved via CMR (`short_name=ALOS_PSR_L1.5`, producer_granule_id search); all 7 Sentinel-1A scenes resolved via CMR (`short_name=SENTINEL-1A_DP_GRD_HIGH`, name-pattern search). Dong et al. (2023) Table 1's dates all match CMR exactly. **One typo found and corrected:** the table's `017921_01EOED DB39` is actually `017921_01E0ED_DB39` (letter O vs digit 0).

These times are precise AIS query windows (scene start ±1–3 h, filtered to the footprint).

| Scene ID | Acquisition start (UTC) | Footprint bbox (lat min–max, lon min–max) | UTM zone(s) for AIS |
|---|---|---|---|
| ALPSRP230200560 | 2010-05-21T04:35:38Z | 28.42–29.03, −91.11 to −90.34 | 15/16 |
| ALPSRP231220540 | 2010-05-28T04:24:33Z | 27.43–28.04, −88.22 to −87.46 | 16 |
| ALPSRP231220560 | 2010-05-28T04:24:50Z | 28.42–29.03, −88.42 to −87.66 | 16 |
| ALPSRP231220580 | 2010-05-28T04:25:06Z | 29.41–30.02, −88.63 to −87.86 | 16 |
| ALPSRP232970570 | 2010-06-09T04:20:33Z | 28.89–29.50, −87.45 to −86.68 | 16 |
| ALPSRP232970580 | 2010-06-09T04:20:41Z | 29.39–30.00, −87.55 to −86.78 | 16 |
| ALPSRS233043050 (ScanSAR) | 2010-06-09T16:25:09Z | 26.23–29.91, −90.41 to −86.21 | 15/16 |
| ALPSRP235450560 | 2010-06-26T04:22:24Z | 28.42–29.03, −87.89 to −87.12 | 16 |
| ALPSRP237930550 | 2010-07-13T04:24:14Z | 27.92–28.53, −88.32 to −87.56 | 16 |
| ALPSRP237930560 | 2010-07-13T04:24:22Z | 28.42–29.03, −88.42 to −87.66 | 16 |
| ALPSRP238660500 | 2010-07-18T04:29:55Z | 25.44–26.06, −89.42 to −88.67 | 16 |
| ALPSRP238660550 | 2010-07-18T04:30:36Z | 27.92–28.53, −89.93 to −89.16 | 16 |
| ALPSRS239753100 (ScanSAR) | 2010-07-25T16:25:21Z | 23.73–27.41, −90.90 to −86.79 | 15/16 |
| ALPSRP241870520 | 2010-08-09T04:38:31Z | 26.42–27.04, −91.76 to −91.01 | 15 |
| S1A_IW_GRDH_1SDV_20170805T023921_..._017782_01DCBB_DE28 | 2017-08-05T02:39:21Z | 26.31–28.16, 48.07–50.91 | (n/a — Persian Gulf) |
| S1A_IW_GRDH_1SDV_20170809T144148_..._017848_01DEC1_EC32 | 2017-08-09T14:41:48Z | 26.99–28.91, 48.99–51.89 | (n/a) |
| S1A_IW_GRDH_1SDV_20170809T144213_..._017848_01DEC1_C09A | 2017-08-09T14:42:13Z | 28.50–30.42, 48.66–51.60 | (n/a) |
| S1A_IW_GRDH_1SDV_20170810T024714_..._017855_01DEF7_F48C | 2017-08-10T02:47:14Z | 27.60–29.44, 46.25–49.13 | (n/a) — **the Kuwait spill scene** |
| S1A_IW_GRDH_1SDV_20170812T023055_..._017884_01DFD8_8F93 | 2017-08-12T02:30:55Z | 27.01–28.94, 50.26–53.12 | (n/a) |
| S1A_IW_GRDH_1SDV_20170812T023120_..._017884_01DFD8_6CAE | 2017-08-12T02:31:20Z | 25.51–27.43, 49.97–52.81 | (n/a) |
| S1A_IW_GRDH_1SDV_20170814T145006_..._017921_01E0ED_DB39 | 2017-08-14T14:50:06Z | 27.20–29.12, 46.89–49.79 | (n/a) — Kuwait slick remnants |

PALSAR scenes are ~04:20–04:39 UTC passes (plus two ~16:25 UTC broad ScanSAR frames). Note: the scene inventory still does not map individual SOS chips to scenes (see [[2026-11-03 - SOS provenance deep search]]); the match here is at **dataset/scene level** (region + date), which is sufficient for AIS windowing of the DWH case.

### B. NOAA Marine Cadastre AIS — 2010 DWH window, access and schema verified

- **2010 layout: monthly ZIPs per UTM zone** at `https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2010/MM_Month_2010/ZoneNN_2010_MM.zip` (the index page misleadingly says "CSV files" — the 2010 archives are **ESRI file geodatabases**). Verified sizes via HTTP HEAD (all 200 OK):
  - Zone 16 (90°W–84°W; contains the DWH wellhead at 28.74N/88.39W and 11–12 of the 14 scenes): May 564,296,634 B · Jun 720,163,638 B · Jul 945,901,080 B · Aug 1,034,857,680 B → **~3.27 GB compressed for the four months**.
  - Zone 15 (96°W–90°W; needed only for the 2–3 western scenes): May 1,923,227,224 B · Jun 1,772,643,732 B · Jul 1,847,897,654 B · Aug 2,077,002,060 B → ~7.62 GB compressed.
- **2010 schema (extracted by range-reading the ZIP central directory and the gdb table headers of `Zone16_2010_05.zip`; no bulk download):**
  - Broadcast table (`a0000000c.gdbtable`, 1,306,474,187 B uncompressed): `OID, Shape (WGS84 point), SOG, COG, Heading, BaseDateTime, Status, VoyageID, MMSI, ReceiverType, ReceiverID`. **LAT/LON are in the point geometry, not columns.** Estimated ~13M broadcast points for the month (from the 103 MB `.gdbtablx` index; estimate, not a count).
  - Voyage table: `VoyageID, Destination`. Vessel table: `MMSI, IMO, CallSign, VesselType, Length, Width, DimensionComponents` (population of name/callsign values in 2010 unverified without a full download).
  - Reading requires GDAL/OGR (OpenFileGDB) or equivalent; e.g. `ogrinfo`/`geopandas.read_file(..., layer=...)`.
- **2020 layout (Cantarell check + easiest LSTM benchmark): daily national CSV ZIPs** `AIS_2020_MM_DD.zip` (~320 MB compressed → ~880 MB CSV). Verified live header sample (range-read + zlib):
  `MMSI,BaseDateTime,LAT,LON,SOG,COG,Heading,VesselName,IMO,CallSign,VesselType,Status,Length,Width,Draft,Cargo,TransceiverClass` — exactly the contract fields our LSTM needs.
- **Coverage limits (official NOAA AIS FAQ, verified this session):** data are from land-based USCG NAIS (~200 stations); "Coverage is currently unavailable for remote Pacific territories, **foreign waters**, or waters extending more than 40 to 50 miles from the coast"; **no satellite AIS** is included. Signals far offshore can occur via tropospheric ducting.
- **Identity caveat:** "Can I unscramble encrypted MMSI values present in 2009–2014 data? Yes, a brief user guide and standalone .exe tool for Windows are available in the MMSI Scrambler Tool ZIP file." So 2010 MMSIs are scrambled but deterministic per vessel (usable as a stable grouping key for tracks/splits; joining to named registries requires the unscramble tool). Voyage fields were phased out in 2015 (they exist in the 2010 gdb).
- **Terms (FAQ):** derived products may be released/redistributed with citation; historical AIS is treated by USCG NAVCEN as "Level C (Historical Data)" (generally public domain framework); data are "intended for coastal and ocean planning purposes only" — our decision-support research framing must not claim enforcement/regulatory use.
- **DWH site coverage risk (honest):** the wellhead is ~41 mi SE of the Mississippi Delta — at the edge of the nominal 40–50 mi terrestrial range. Heavy response traffic plus ducting make usable coverage likely, but this must be verified empirically after a bounded download (filter May–Aug 2010 Zone 16 to a scene bbox ± time window and count distinct vessels). The two broad ScanSAR scenes reaching 23.7–26.2N are largely deep-offshore and will be sparse.

### C. Deepwater Horizon incident anchor (NOAA IncidentNews, verified)

`incidents.csv` (4,952 incidents, 3.2 MB, public download) → record **id 8220, "Deepwater Horizon; Gulf of Mexico", open_date 2010-04-21, lat 28.7367, lon −88.3872, threat Oil, commodity Diesel/crude oil, max potential 205,000,000 gallons**, description citing the Barbier ruling (3.19M barrels released). The spill window (Apr 20 – mid-Sep 2010) fully spans the 14 SOS PALSAR scene dates (May 21 – Aug 9, 2010), and the scene footprints (25.4–30.0N, 86.7–91.8W) cover the spill-affected northern GoM around the well site.

### D. Kuwait, August 2017 — event and suspect vessel documented; no open AIS

- The original SOS README references the 2010 Deepwater Horizon and August 2017 Kuwait incidents as source locations (per [[2026-11-03 - Original SOS share inspection]]).
- **RUS Copernicus training kit "OCEA03 Oil Spill Mapping, August 2017, Kuwait"** (Serco Italia, 2018; ESA EO4Society PDF, downloaded and text-verified) uses the exact product `S1A_IW_GRDH_1SDV_20170810T024714_20170810T024738_017855_01DEF7_F48C.zip` — the same scene as SOS/Dong Table 1 — for the spill "in the south of Kuwait, near the Al Khiran area." This confirms the SOS Sentinel subset's key scene is this documented incident.
- **SkyTruth blog, 2017-08-15, "Satellite Imagery Reveals Scope of Last Week's Oil Spill in Kuwait" (John Amos)**: slick 131 km² on the Aug 10 Sentinel-1 image; ≥34,590 gallons at 1 µm assumption; oil ashore near Ras Al-Zour on Aug 11 (Sentinel-2); remnants drifting north on Aug 14 (Sentinel-1). **Pipelay vessel DLB 1600 (MarineTraffic shipid 457955, MMSI 370129000, IMO 9681651) visible on the Sentinel-1 image near the north end of the slick on Aug 10**, AIS showing slow eastward movement since Aug 5 (probably installing pipeline), within 9 km of the Al Khafji field by Aug 14. SkyTruth explicitly says the source/cause is **uncertain** (tanker, Al Khafji infrastructure, or pipelay/anchor damage hypotheses) — a suspect lead, not attribution.
- PlanetScope study corroborates the event (oil spill near Ras Al-Zour, Kuwait, 2017-08-10, ANN detection on optical imagery with sunglint).
- **Open AIS for the Persian Gulf 2017: not found.** Searches across Zenodo/PANGAEA/HuggingFace APIs, Kaggle, and the web found no real individual-vessel AIS archive covering the northern Persian Gulf in Aug 2017. The Mendeley "Persian Gulf AIS-like Dataset" is **synthetic** (30,000 simulated records with GPS noise) — not real AIS; flagged and rejected for our purpose. GFW requires an account + API token (not permitted here) and its public products are aggregated; MarineTraffic/exactEarth/Lloyd's are commercial. The DLB 1600's actual track is therefore not accessible under current constraints — only the qualitative positions/dates in the SkyTruth reporting.

### E. DARTIS 2019 — join keys verified; open E. Med AIS does not exist

- The PANGAEA data table (2.4 MB textfile, downloaded) confirms per-patch: full Sentinel-1 SAFE product ID, acquisition start/end UTC, patch corner coordinates (WGS84), object boxes, and `patch_name` like `S1_20190101_034235_034350_VV_1`. Example row: `S1B_IW_GRDH_1SDV_20190101T034300_20190101T034325_014295_01A97E_39B8.SAFE`, 2019-01-01T03:42:35–03:43:50, patch ~33.0–33.3E/33.1–33.3N. These are exactly the keys an AIS join would need.
- **Geographic extent (from the record itself):** oil slicks within 30–36E / 31–34.7N; look-alikes/no-oil extend to 27.12–36.09E / 29.30–36.37N (Levantine basin, Egyptian/Israeli/Lebanese/Cypriot/Turkish waters).
- **Piraeus AIS dataset (Zenodo 10.5281/zenodo.6323416; Data in Brief, Tritsarolis et al. 2022):** 244M records, May 9, 2017 – Dec 26, 2019 (includes the DARTIS year), Saronic Gulf/Piraeus receiver coverage (~37.9N/23.7E, ~10,000 km²). CSV schema `timestamp, vessel_id (anonymized), lon, lat, heading, course, speed` + static type/country. Files verified: `unipi_ais_dynamic_2017.zip` 854 MB, `_2018.zip` 1.66 GB, `_2019.zip` 1.65 GB, synopses 580 MB. **But its coverage (≈23.2–24.3E) lies entirely west of DARTIS's 27.12E western edge — no co-location is possible.** License discrepancy: Zenodo record metadata says CC BY 4.0 (API-verified) while the article's specifications table says CC BY-NC-SA 4.0; treat the more restrictive (NC-SA) as governing until clarified.
- **EMODnet Human Activities "Vessel/Route Density"** = monthly raster grids (routes per km²) — aggregated, not individual positions. Confirmed from the official portal.
- Conclusion: DARTIS cannot be paired with open per-vessel AIS for 2019. (Commercial or account-gated sources — MarineTraffic, exactEarth, GFW — are out of scope.)

### F. Cantarell 2020 — AIS match impossible from open sources

Cantarell (Bay of Campeche, ~19.5N/90.5–92.3W, Mexican EEZ, Jan–Sep 2020) falls under NOAA's explicit "foreign waters" exclusion; the archive is terrestrial-only. No open source of Mexican-EEZ individual-vessel AIS was found. The 2020 NOAA daily CSVs remain useful only for US waters (LSTM benchmark). The separate acquisition-mapping agent's work does not change this AIS-side verdict.

### G. Zenodo Parts I–III — not a pre-matched AIS source

Record descriptions (API-verified again) contain no scene IDs or acquisition dates; the linked paper is Trujillo-Acatitla et al., "Marine oil spill detection and segmentation in SAR data with two steps Deep Learning framework," Marine Pollution Bulletin (DOI 10.1016/j.marpolbul.2024.116549). Scene/time metadata exists only inside the ~96.5 GB of georeferenced TIFFs. US-origin scenes could in principle be joined to Marine Cadastre AIS (2015+) after per-image inspection, but this is a heavy, secondary effort — not recommended this sprint.

### H. Other datasets checked this session (access verified)

- **OpenSARShip (SJTU OpenSAR platform):** direct, login-free downloads verified (HTTP 200): `OpenSARShip_1.zip` 915,975,292 B, `OpenSARShip_uint8.zip` 33,710,624 B at `https://opensar.sjtu.edu.cn/openSAR/...`. Structure (central directory read): 26,694 entries of Sentinel-1 VH/VV ship chips organized by AIS-derived vessel class (`Cargo/...`), filenames encoding AIS parameters. A real SAR-chip + AIS-metadata corpus — relevant to ship detection, not oil slicks; chips only, no scenes, no oil labels.
- **xView3-SAR (dark-vessel detection, SAR + matched vessel metadata):** challenge portal states "Register/Login to Download Data" → account-gated; not pursued under our constraints.
- **NARI Brest AIS (Zenodo 10.5281/zenodo.2563256, CC BY 4.0):** known open real AIS (Atlantic/Brest) for trajectory work; not co-located with any of our SAR cases.
- **HuggingFace:** `mark000071/Ship_trajectory_interpolation` (EnvShip-Voyage) and `EnvShip-Bench` still declare **no license** in their dataset cards (API check) — the prior session's licensing blocker stands. `andsanv/ais-tracks` (84.6M rows, 272 MB parquet) has no card, unknown provenance — do not use. `eyesofworld/AIS_Dataset` likewise unlicensed/undocumented.
- **GCOOS "Gulf AIS Monthly Vessel Traffic" ArcGIS products (2010/2017):** derived/generalized US-Gulf track layers; evidence of usable 2010 GoM coverage but generalized (not raw AIS); secondary only.
- No published DWH-specific open AIS re-release surfaced in Crossref/web searches; the primary path is the NOAA 2010 archive itself.

---

## Confirmed vs uncertain matches

| Case | SAR in hand | AIS source | Match status |
|---|---|---|---|
| **DWH 2010 (SOS PALSAR)** | 14 scenes, IDs/times/footprints verified in CMR; chips already in SOS release | NOAA MarineCadastre 2010 Zone 16 (+15) monthly gdb files; verified live, free, no account | **Confirmed at scene level** (region + date + hour). Per-chip scene membership still unknown (prior session's gap). AIS density at the wellhead edge-of-range pending empirical check. |
| **Kuwait 2017 (SOS Sentinel)** | 7 scenes; the 2017-08-10 scene is the documented spill scene (RUS tutorial uses the identical product ID); 2017-08-14 = slick remnants | None open (Persian Gulf). GFW account-gated/aggregated; commercial options excluded | **Confirmed event + named suspect vessel (DLB 1600, MMSI 370129000) with documented positions on two scene dates.** No accessible track. Not an attribution claim. |
| **Cantarell 2020** | Dataset in hand (CC BY 4.0); scene mapping with separate agent | NOAA excludes foreign waters; no open Mexican-EEZ AIS | **Blocked — no match possible from open sources.** |
| **DARTIS 2019 E. Med** | Patches + product IDs/times/coords verified | None open covering 27–36E/29–36N in 2019 (Piraeus is outside; EMODnet aggregate) | **Blocked — join keys exist, AIS side missing.** |
| **Parts I–III (global)** | Images in hand; no scene/date metadata public | Would require per-TIFF extraction; US scenes could join MarineCadastre 2015+ | **Not pre-matched; impractical this sprint.** |

---

## Download proofs (reproducible access checks actually executed)

1. **NOAA 2010 monthly zone files exist** (HTTP HEAD, all 200):
   `curl -sSI "https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2010/05_May_2010/Zone16_2010_05.zip"` → `content-length: 564296634` (Jun 720163638 · Jul 945901080 · Aug 1034857680; Zone 15: 1923227224/1772643732/1847897654/2077002060).
2. **NOAA 2020 daily CSV schema** (range-read of `.../2020/AIS_2020_07_01.zip`, 320,722,074 B; first entry `AIS_2020_07_01.csv`, deflate; decompressed header + rows):
   `MMSI,BaseDateTime,LAT,LON,SOG,COG,Heading,VesselName,IMO,CallSign,VesselType,Status,Length,Width,Draft,Cargo,TransceiverClass`
   `368112080,2020-07-01T00:00:06,30.22393,-93.26474,0.0,202.2,200.0,,,,,12,,,,,A`
3. **NOAA 2010 gdb structure** (central directory of `Zone16_2010_05.zip`: 63 entries, `.gdb` files; `a0000000c.gdbtable` = 1,306,474,187 B uncompressed Broadcast table; field names extracted: `OID, Shape, SOG, COG, Heading, BaseDateTime, Status, VoyageID, MMSI, ReceiverType, ReceiverID`; Voyage `VoyageID, Destination`; Vessel `MMSI, IMO, CallSign, VesselType, Length, Width, DimensionComponents`).
4. **CMR scene resolution** (example):
   `curl "https://cmr.earthdata.nasa.gov/search/granules.json?short_name=ALOS_PSR_L1.5&version=1&producer_granule_id[]=ALPSRP230200560"` → `2010-05-21T04:35:38.000Z` + polygon.
   `curl "https://cmr.earthdata.nasa.gov/search/granules.json?short_name=SENTINEL-1A_DP_GRD_HIGH&readable_granule_name[]=*017855_01DEF7_F48C*&options[readable_granule_name][pattern]=true"` → `2017-08-10T02:47:14.000Z` + polygon.
5. **DARTIS PANGAEA table** (2.4 MB):
   `curl -L "https://doi.pangaea.de/10.1594/PANGAEA.980773?format=textfile"` → per-patch product IDs/times/coordinates (sample rows in §E).
6. **IncidentNews** (3.2 MB): `curl -L "https://incidentnews.noaa.gov/raw/incidents.csv"` → DWH record id 8220 (§C).
7. **Piraeus Zenodo**: `curl "https://zenodo.org/api/records/6323416"` → file list with sizes (§E); DOI 10.5281/zenodo.5562629 resolves to this record.
8. **OpenSARShip**: `curl -sSI "https://opensar.sjtu.edu.cn/openSAR/OpenSARShip_1.zip"` → 200, 915,975,292 B; central directory of the uint8 zip listed (26,694 entries).
9. **Kuwait event documentation**: SkyTruth blog (quoted in §D) and RUS PDF `https://eo4society.esa.int/wp-content/uploads/2022/01/OCEA03_OilSpill_Kuwait.pdf` (downloaded; product ID string verified).
10. **NOAA FAQ/data dictionary PDFs**: `https://coast.noaa.gov/data/marinecadastre/ais/faq.pdf`, `.../data-dictionary.pdf` (downloaded; coverage/foreign-waters/satellite/MMSI-scrambler/redistribution statements quoted in §B).

---

## Recommended matched window (concrete, for the demo)

**Case: DWH / PALSAR 2010-05-28 scenes (densest cluster, includes the wellhead-adjacent frames).**

1. Download `Zone16_2010_05.zip` (564 MB) — optionally `Zone15_2010_05.zip` for the western scene only.
2. Read the Broadcast layer with GDAL; convert to CSV/Parquet with columns `MMSI(scrambled), BaseDateTime, LAT, LON, SOG, COG, Heading, Status`.
3. Filter predicate (example, scene ALPSRP231220560):
   `BaseDateTime BETWEEN '2010-05-28T02:25:00Z' AND '2010-05-28T06:25:00Z' AND LAT BETWEEN 28.42 AND 29.03 AND LON BETWEEN -88.42 AND -87.66` (scene time 04:24:50Z ±2 h).
4. Verify vessel counts per scene box; also run the count for the wellhead box (28.6–28.9N, −88.6 to −88.1W) to quantify the receiver-range caveat before committing the demo to it.
5. Suspect-ranking demo narrative: slick polygons from SOS chips (region/date-level match), back-drift with ERA5/CMEMS, candidate vessels = AIS tracks intersecting the uncertainty cone; **state plainly that the DWH source was a known stationary well blowout** — ranking serves as pipeline validation, and "coincidence ≠ culprit" applies to every listed vessel (most will be response vessels).
6. LSTM benchmark from the same slice: select tracks with ≥ N points in the window/month, mask synthetic 15/30/60-min blocks, split by scrambled-MMSI and by non-overlapping time windows; compare against dead-reckoning/constant-velocity/Kalman baselines per the spec.

**Story case (no AIS needed): Kuwait 2017** — present the SOS Sentinel chips for the 2017-08-10 scene, cite SkyTruth's DLB 1600 identification (MMSI 370129000) and the RUS tutorial, and note the open-source question ("source and cause uncertain"). Do not imply proof.

---

## Blockers and open items

- **No open AIS for Persian Gulf (2017), Bay of Campeche (2020), or E. Mediterranean (2019).** Gated alternatives: GFW (account, CC BY-NC, aggregated), xView3 (registration), MarineTraffic/exactEarth/Lloyd's (commercial). Breaking any of these requires an explicit user decision to accept account/terms friction.
- **2010 MMSI scrambling** (Windows-only official unscramble tool). Grouping/splits unaffected; named-vessel joins need the tool or a reimplementation.
- **2010 gdb format friction** (GDAL required; 1.3 GB Broadcast table per month-zone).
- **DWH-site AIS density at edge of receiver range** — empirical count pending bounded download (step 4 above).
- **EnvShip-Voyage/Bench and `andsanv/ais-tracks`** remain license-undocumented; Piraeus license discrepancy (CC BY 4.0 on Zenodo vs CC BY-NC-SA 4.0 in the article) needs author clarification before redistribution.
- **SOS chip→scene crosswalk still missing** (prior session); scene-level matching used here does not require it, but chip-level claims would.
- **DARTIS image archive byte size** still not stated by PANGAEA (single-file downloads are open; the one-go ZIP/TAR requires a PANGAEA account — not created).

## What I inspected vs did not

Inspected: NOAA 2010/2020 archive indexes, file headers/central directories and schemas (range reads ≤512 KB); NASA CMR granule metadata for all 21 SOS scenes; NOAA AIS FAQ + data dictionary PDFs; IncidentNews CSV (DWH record); SkyTruth Kuwait blog (full text); RUS Copernicus Kuwait tutorial PDF; DARTIS PANGAEA record + full 2.4 MB data table; Zenodo APIs for Parts I–III, Piraeus, and trajectory search results; HuggingFace dataset APIs; OpenSAR platform listing + archive headers; xView3 portal text; EMODnet Human Activities portal; Mendeley synthetic Persian Gulf listing; Crossref searches for DWH-AIS publications. Not done: any account creation, any full dataset download, Baidu/AI Studio access, Copernicus/ESA product downloads, or contacting any author or agency. Absence of open Persian Gulf/Mexican-EEZ/E-Med AIS is a finding of the searched public sources, not proof that none exists anywhere.

## Sources

- NOAA Marine Cadastre AIS: index pages https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2010/index.html · https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/index.html · FAQ https://coast.noaa.gov/data/marinecadastre/ais/faq.pdf · data dictionary https://coast.noaa.gov/data/marinecadastre/ais/data-dictionary.pdf
- NASA CMR granule search API: https://cmr.earthdata.nasa.gov/search/granules.json (ALOS_PSR_L1.5; SENTINEL-1A_DP_GRD_HIGH)
- Dong et al. 2023 scene inventory (cross-check): https://doi.org/10.3390/jmse11081552
- IncidentNews: https://incidentnews.noaa.gov/raw/incidents.csv (DWH id 8220)
- SkyTruth Kuwait analysis (2017-08-15): https://skytruth.org/blog/satellite-imagery-reveals-scope-of-last-weeks-massive-oil-spill-in-kuwait
- RUS Copernicus tutorial (uses the SOS Kuwait scene): https://eo4society.esa.int/wp-content/uploads/2022/01/OCEA03_OilSpill_Kuwait.pdf
- PlanetScope Kuwait study: "Oil Spill Detection from PlanetScope Satellite Image: Application to Oil Spill Accident near Ras Al Zour Area, Kuwait in August 2017" (JSTOR/ResearchGate records)
- DARTIS: PANGAEA table https://doi.pangaea.de/10.1594/PANGAEA.980773?format=textfile · ESSD paper https://doi.org/10.5194/essd-17-6807-2025
- Piraeus AIS: Zenodo https://doi.org/10.5281/zenodo.5562629 (record 6323416) · article https://pmc.ncbi.nlm.nih.gov/articles/PMC8749179/ · corrigendum https://pmc.ncbi.nlm.nih.gov/articles/PMC8857556/
- Zenodo Parts I–III: https://zenodo.org/records/8346860 · https://zenodo.org/records/8253899 · https://zenodo.org/records/13761290 · paper DOI 10.1016/j.marpolbul.2024.116549
- OpenSARShip: https://opensar.sjtu.edu.cn/ (Data & Codes) · filter tool README (structure): https://github.com/luckight/OpenSARShipFilter
- xView3: https://iuu.xview.us/ ("Register/Login to Download Data") · reference code https://github.com/DIUx-xView/xview3-reference
- EMODnet Human Activities (vessel density = aggregate rasters): https://emodnet.ec.europa.eu/en/human-activities
- Mendeley synthetic Persian Gulf AIS-like data (rejected): https://data.mendeley.com/datasets/dbwfcf3bzm/1
- NARI Brest AIS: https://doi.org/10.5281/zenodo.2563256
- HuggingFace APIs for EnvShip-Voyage/EnvShip-Bench/andsanv-ais-tracks/eyesofworld-AIS_Dataset (license fields absent)
- Prior vault context: [[2026-11-03 - Additional datasets deep search]] · [[2026-11-03 - SOS provenance deep search]] · [[2026-11-03 - Original SOS share inspection]] · `Wayfinding/Assets/Dataset Profile - OceanTrace.md` · `Wayfinding/OceanTrace - ANN-DL implementation spec.md`

## Outcome

A genuinely matched, fully open SAR↔AIS real case exists for OceanTrace: **SOS's DWH-period PALSAR scenes + NOAA Marine Cadastre 2010 Zone 16/15 monthly AIS**, now pinned to exact scene times/footprints and verified file-level access. The Kuwait 2017 case adds a documented suspect-vessel identity (MMSI known, positions at two scene dates) without an accessible track. Cantarell, DARTIS, and Parts I–III cannot be AIS-matched from open sources. Recommendation: DWH-matched demo + Kuwait narrative + NOAA-based LSTM benchmark (2020 daily CSVs or the same 2010 slice), with the MMSI-scrambling, receiver-range, and "coincidence ≠ culprit" caveats carried into any write-up. These are research recommendations, not adopted decisions; no project overview or ticket was edited.
