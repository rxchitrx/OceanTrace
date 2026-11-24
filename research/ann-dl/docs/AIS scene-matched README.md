# AIS acquisition tied to the 21 SOS scenes

Data paths below are relative to `Data/AIS/scene-matched/`.

## Scope

Every source selection starts from scene-manifest.json: exact catalogue acquisition UTC start/end, original footprint polygon and source scene ID. scene-footprints.geojson contains the same footprints for inspection. This acquisition does not use the unrelated2020 benchmark.

## 2010 Gulf of Mexico: all seven source archives downloaded

Seven complete NOAA monthly zone archives were selected by intersecting each original PALSAR footprint with the published UTM-zone longitudes and matching the acquisition month. They cover the relevant parts of May–August2010: Zones15/16 for May, June and July; Zone15 for August. Full source archives are retained, including observations outside the later per-scene export, so wider time windows remain possible. They are roughly10GB compressed based on earlier source-size checks; live download records contain actual Content-Length values.

- archives/: original ZIPs, with resumable .part downloads.
- download-status/: per-file bytes, actual source length and verification state.
- acquisition.json: written after all selected archives pass ZIP CRC validation and SHA-256 calculation.
- raw/: complete extracted source geodatabases were removed on 2026-11-20; the archives and exported parts remain.
- schemas/: actual layer names, CRS, field types and sample records after extraction.
- parts/: all available reports in each source scene polygon for its entire00:00–24:00 UTC acquisition date. No interpolation, resampling, speed filter or fabricated observations.
- scene-day-positions.csv: combined full-date, exact-footprint export, written after extraction completes. Rows represent scene membership, so overlapping scenes can repeat an observation.
- coverage.json: actual per-scene observation counts, including empty scenes and unavailable sources.

Archive availability does not prove local AIS reception. NOAA data are terrestrial, with sparse offshore coverage. Original2009–2014 MMSIs may be scrambled; preserve source IDs without treating them as verified named-vessel identities. Times are interpreted as UTC according to NOAA's documentation.

## 2017 Persian Gulf: access unresolved

The seven Sentinel scenes are outside NOAA coverage. No raw matching download has yet been obtained. See [PERSIAN-GULF-ACCESS.md](AIS%20PERSIAN-GULF-ACCESS.md) for checked sources and a precise provider/academic-access request polygon. No synthetic AIS or aggregate traffic maps will be substituted as real scene-matched tracks.

## Execution and recovery

The acquisition and extraction scripts were retired after the completed run. Extraction waited for each verified archive, extracted the geodatabase, then exported the full acquisition-date positions inside exact source polygons. GDAL/OpenFileGDB support was supplied by pyogrio0.13.0. Actual source schemas and EPSG:4326 were verified on available databases. A reproduced June offset-pagination defect was repaired on 5 November: extraction now reads the complete date/bbox selection once, asserts unique source feature IDs, then applies the exact polygon. Independent polygon-mask source comparisons verified exported feature membership. The faulty June export and diagnosis were retained during the repair and removed in the 2026-11-20 cleanup.

Jobs ran independently of interactive terminal sessions through a background runner that has since been retired. A failed extraction was an error, not a zero-point scene. Existing originals and the 2020 benchmark remain intact.

Primary source archive index: https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2010/index.html . Coverage/format guidance: https://coast.noaa.gov/data/marinecadastre/ais/faq.pdf .

## Historical first-three coverage snapshot

[COVERAGE.md](AIS%20scene-matched%20COVERAGE.md) and coverage-audit.json/CSV now contain checks against the actual downloaded2010 geodatabase. First complete source: Zone16May2010, ZIPCRCverified andSHA256recorded. All three28May source footprints were exported and independently cross-checked using GDAL polygon-mask queries; sourcefeatureIDs exactly equal exportedIDs.

Coverage at acquisition differs from full-day availability: ALPSRP231220540 has no reports within±15minutes; ALPSRP231220560 has18publishedAISIDs within±15minutes and7with bracketing reports separated by≤5minutes; ALPSRP231220580 has4nearbyIDs and2brackets. These are scene-level coverage diagnostics, not confirmed vessel identities, continuous observed paths or spill-source labels. These first-three results are a historical snapshot. All seven selected source archives are now downloaded; see coverage-audit.json/CSV for rolling verified export coverage.

Extraction ran a coverage check after each verified archive so the audit advanced automatically. The first-three visual was a fixed snapshot and has been removed; coverage-audit.json/CSV are the current rolling records.

## Completed 2010 extraction and verification — 5 November 2026

All seven NOAA archives are downloaded and unpacked. All 14 PALSAR scenes passed independent source-mask checks across 16 scene/archive parts after the June pagination repair. `scene-day-positions.csv` contains 379,429 scene-membership rows; counts reconcile with coverage.json and no `(scene_id, source_archive, source_fid)` key repeats within the combined export. Overlapping scenes can still share observations.

Nine scenes have received reports within ±15 minutes of acquisition; five do not. Nine have a source ID with reports bracketing acquisition with a gap ≤5 minutes. See coverage-audit.json/CSV and [COVERAGE.md](AIS%20scene-matched%20COVERAGE.md) for per-scene results and limitations. Seven 2017 Persian Gulf scenes remain without obtained raw AIS. Verification establishes faithful source extraction, not complete vessel reception, continuous trajectories or pollution attribution.
