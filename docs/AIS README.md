# NOAA AIS: downloaded and audited research subset

Source: NOAA Marine Cadastre, daily file AIS_2020_07_01.zip. Direct archive: https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/AIS_2020_07_01.zip . Coverage/terms: https://coast.noaa.gov/data/marinecadastre/ais/faq.pdf . Schema: https://coast.noaa.gov/data/marinecadastre/ais/data-dictionary.pdf . Downloaded 2026-11-03.

Files referenced below are in `Data/AIS/`.

## Actual data
- ZIP size320,722,074bytes, integrity checked with all ZIP-member CRCs.
-8,529,554national records scanned.
-Research subset: latitude27–30.5N, longitude96–88W, northern Gulf of Mexico.
-2,229,107regional records before duplicate/conflict removal;2,228,788after.
-3,359vessel IDs present in retained segments.
-253exact repeated timestamp/position records removed;66records sharing a vessel/timestamp with conflicting positions excluded.
-1,593regional records with invalid MMSI syntax excluded separately.
-78,108segments under the provisional rule: split a vessel sequence at gaps greater than5minutes.
-5,673segments last at least2hours and contain at least120reports. This is a continuity criterion, not a final training-quality label.

## Files and operations
-archives/AIS_2020_07_01.zip: untouched original archive.
-northern-gulf-2020-07-01-clean.csv: filtered valid coordinates/ID/timestamps, ordered within each vessel, duplicate/conflict handling; irregular original sampling retained.
-segments.json: continuity statistics, timestamps and vessel IDs.
-example-continuous-track-1/2/3.csv: observed examples (no interpolation/predictions). Example2has1,143reports, spans almost24hours, maximum report gap229seconds, reported speeds0–7.2knots and mean about2.90knots. Example3is mostly stationary; do not treat long duration as useful movement by itself.
-track-audit.json: exact counts, source fields and limitations.

## Preprocessing still pending
Speed/course missing-value codes and plausibility checks; position-jump detection; moving-vessel selection; resampling and interpolation policy; vessel-disjoint splits; train-only fitted scaling; synthetic15/30/60minute gap masks; LSTM sequence construction and training. None is claimed completed.

## Interpretation
This is usable real per-vessel time-series source material, replacing the99-row/98-vessel sample. It is NOT paired with our2010/2017SOS images and supplies no oil-source/culprit labels. An image/AIS join needs acquisition time, geography and verified patch/source mapping; nearby vessels are not proof of responsibility. NOAA public data are terrestrial USCG observations with coverage limits; see the official FAQ and preserve source-specific terms/citation when redistributing.

## First quality pass — 4 November 2026

[Read-only quality audit](AIS%20quality-audit%20README.md) completed for all regional reports: unavailable-field codes profiled and 642 short-interval edges flagged for review under a provisional 60-knot threshold. Original data and valid zero speeds retained. Cleaning decisions, resampling and splits remain pending.
