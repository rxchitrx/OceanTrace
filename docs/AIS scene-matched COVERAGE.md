# NOAA 2010 coverage verification

Status: complete. 14 of14 source scenes have all required archives downloaded, exported and checked. Others are pending or partial, not zero-coverage results.

Checks: exported feature IDs equal a fresh source-geodatabase selection using the exact original polygon and full acquisition UTC date; all exported dates, coordinates and counts checked. Source-check caches are bound to the exported file SHA256.

The per-scene CSV/JSON measures report counts and source IDs within5/15/60/120minutes of acquisition, plus nearest before/after reports bracketing acquisition within5/15minutes. Window thresholds are descriptive diagnostics. Received coverage can be sparse and cannot identify an oil source by itself.

2010 identifiers may be scrambled; no real-world vessel identity claim. Complete month/zone geodatabases retain outside-polygon and wider-date context. No resampling, interpolation or cleaning was done here.
