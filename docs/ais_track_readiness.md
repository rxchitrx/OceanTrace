# Acquisition-time track readiness — 5 November 2026

## Finding

Five of 14 PALSAR scenes contain at least one moving sequence passing this provisional screen. Two more contain regularly observed sequences with less than 500 m movement from their first observation. Seven do not pass the regular-sequence screen. This is a shortlist for inspection, not validated model-training eligibility.

The strongest candidate is ALPSRS233043050 (9 June, afternoon UTC): 171 regular sequences, including 81 with movement ≥500 m. The other moving candidates are ALPSRP232970580 (3), ALPSRP235450560 (1), ALPSRP237930550 (1), and ALPSRP237930560 (3). These are 89 scene/source-ID sequences, not necessarily 89 distinct vessels or independent training examples.

## Provisional screen

Use only received observations within ±60 minutes of the scene acquisition midpoint and inside its exact footprint. A qualifying sequence has at least 10 distinct timestamps, extends at least 15 minutes before acquisition start and 15 minutes after acquisition end, and has no gap longer than 5 minutes. Break sequences at conflicting same-ID/time coordinates or consecutive inferred speed above 60 knots. Motion means a point at least 500 m from the sequence's first point. These thresholds are exploratory diagnostics, not approved cleaning, resampling or training rules.

Identical same-ID/time/position observations are collapsed only for diagnostics; different coordinates at the same timestamp are treated conservatively as conflicts without choosing one. No source CSV is changed. No assumptions about historical SOG scaling were needed. The 604 conflicting scene/ID timestamps and four short-edge speed flags are review findings, not proof of false source records. Overlapping scenes can repeat events.

## Per-scene results

| Scene | UTC date | Regular sequences | With ≥500 m movement |
|---|---|---:|---:|
| ALPSRP230200560 | 2010-05-21 | 2 | 0 |
| ALPSRP231220540 | 2010-05-28 | 0 | 0 |
| ALPSRP231220560 | 2010-05-28 | 0 | 0 |
| ALPSRP231220580 | 2010-05-28 | 1 | 0 |
| ALPSRP232970570 | 2010-06-09 | 0 | 0 |
| ALPSRP232970580 | 2010-06-09 | 3 | 3 |
| ALPSRS233043050 | 2010-06-09 | 171 | 81 |
| ALPSRP235450560 | 2010-06-26 | 1 | 1 |
| ALPSRP237930550 | 2010-07-13 | 2 | 1 |
| ALPSRP237930560 | 2010-07-13 | 5 | 3 |
| ALPSRP238660500 | 2010-07-18 | 0 | 0 |
| ALPSRP238660550 | 2010-07-18 | 0 | 0 |
| ALPSRS239753100 | 2010-07-25 | 0 | 0 |
| ALPSRP241870520 | 2010-08-09 | 0 | 0 |

## Sensitivity and limits

The broad 9 June scene has 32 regular capture-spanning sequences with a 1-minute maximum gap, 171 with a 5-minute gap and 238 with a 15-minute gap, keeping the other screen conditions. July 13 scene ALPSRP237930560 changes from 0 to 5 to 37. Suitability depends on the intended cadence; a nearby pair alone is insufficient.

Five scenes lack any reports within ±15 minutes. ALPSRP231220560 and ALPSRP232970570 have nearby reports but no sequence passing the balanced ±15-minute context screen. This is insufficient in-footprint context under this screen, not proof wider monthly sources lack usable tracks. Geometry/day clipping and the ±60-minute assessment window can truncate movement. The two low-motion scenes are ALPSRP230200560 and ALPSRP231220580; their sequences can support stationary-context analysis but are weak movement examples.

These 2010 scenes concern Deepwater Horizon, a well-source event. Nearby vessel movement does not establish pollution responsibility. Legacy source IDs may be scrambled or inconsistent. Track readiness does not establish patch-to-scene mapping, slick intersection, trajectory labels, independent train/test samples, or LSTM readiness. Seven 2017 Persian Gulf scenes still have no obtained matching raw AIS and were not scored as zero coverage.

## Verification and evidence

The complete combined source was scanned; day totals and ±15-minute counts reconcile with the independent coverage audit. All 185 qualifying regular sequences were independently re-read from CSV and checked for distinct timestamps, no conflicting positions, context on each side and maximum gaps. Five synthetic boundary controls exercised a regular moving sequence, missing interval, conflicting capture position, isolated bracket and implausible jump. Source SHA256 remained unchanged.

- Reproduce: the assessment script was retired after the run; inputs and outputs remain.
- Source: `Data/AIS/scene-matched/scene-day-positions.csv`; source SHA256 in assessment.json.
- [Full per-ID metrics and sensitivity](../../../datasets/AIS/scene-matched/track-readiness/assessment.json)
- [Scene summary](../../../datasets/AIS/scene-matched/track-readiness/scene-summary.csv)
- [Verification results](../../../datasets/AIS/scene-matched/track-readiness/verification.json)

## Next step

Visually inspect one moving sequence from the broad 9 June scene, including conflicts and wider-source context, before choosing any track-cleaning or modeling rules. Keep acquisitions grouped when designing evaluation to avoid treating overlapping-scene observations as independent examples.
