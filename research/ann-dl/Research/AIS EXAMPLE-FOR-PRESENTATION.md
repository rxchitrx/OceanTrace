# Real observed AIS speed example for the latest presentation

Files below are in `Data/AIS/`.

User explicitly requests passing this example to the existing Terra presentation agent and adding it with a polished visual. This supersedes the earlier request to omit AIS while data work was pending; add the actual observed track, not a broad new AIS workflow section.

## Files
- example-continuous-track-2.csv: all1,143observed rows, MMSI368000510,2020-07-01UTC.
- phone-track-plot.html: original full-day speed chart.
- phone-track-context.html: annotated chart highlighting04:00–06:00UTC.
- example-track-2-context.json: derived interval metrics, spatial check, source links and limits.
- nhd-stopped-position-layer-9.geojson: actual USGS canal polygon intersecting the focus positions.

## Verified meaning
Zero speed is a reported speed value, not missing AIS. From04:00:04through05:59:45UTC there are86reports, maximum interval199seconds, SOG0–0.3knots,49exact-zero reports. All86reported positions intersect USGSNHD Area-LargeScale polygonOBJECTID189374/permanentidentifier128429836, FTYPE336/FCODE33600 (CanalDitch/artificial waterway), near Matagorda,Texas. Minimum point distance to that polygon boundary is about39metres after UTM15Nprojection. Label the interval “Nearly stationary • AIS present • mapped canal/waterway”. Do not label it offshore/atsea, anchored, moored, or AISshutdown. Only the focusinterval was spatially classified; other hours remain unassessed for waterway context.

Fulltrack maximum interval229seconds: no >5min observed gap in this example. Five minutes is a provisional visualization/audit threshold, not a universal AISreporting standard. Do not invent redmissing bands. If a future realtrack has a gap, break the observed speedline and mark missing reports; do not fill speedwithzero. Locations inside an actual missing interval are unknown unless independently observed; model/interpolation locations must be labeled estimated.

Navigation status was0throughout thefocusinterval (reported “underway using engine”). This operator-entered field can lag actual activity and does not establish anchoring/berthing.

## Visual request
Use a clearfull-day speed(knots)vs UTCtimechart, observeddata only. Highlight the04–06 interval in amber; distinguish dataavailability from movementstate. Optional synchronized positioncontext/availability strip is useful. Keep source metadata compact, phone readable, and existing presentation chrome/navigation/style unchanged. No fabricated prediction or culprit story.

## Sources
- NOAA observeddata: https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/AIS_2020_07_01.zip
- USGS queriedpolygon layer: https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/9
- USGS code definitions: https://www.usgs.gov/ngp-standards-and-specifications/national-hydrography-dataset-nhd-data-dictionary-feature-domains
- USCG AIS field definitions: https://navcen.uscg.gov/ais-class-a-reports
