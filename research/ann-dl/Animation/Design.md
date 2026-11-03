# OceanTrace — the missing interval

Source: user-directed animation brief, 23 October 2026. Agent: Codex.

## Concept
A detailed tanker crosses a living ocean. Day fades into night; the camera closes in as the ship deliberately stops AIS broadcasts, releases oily waste, sails away, and resumes broadcasting. The oil remains while the recorded track has a gap.

## Format and motion
Anatomy Figure: standalone, self-contained SVG/HTML, no dependencies. A 40-second illustrative timeline with pause, replay, scrubbing and chapter selection. This is a fictional scenario, not a real incident or a measured AIS reporting cadence. Use AIS (Automatic Identification System), interpreting the user's “AIR.”

## Parts before geometry
- Hull: keel shadow, submerged red hull, port hull, starboard bow, sheer edge, gunwale, bow deck, stern deck, six hull plates, anchor pocket, anchor, six portholes.
- Deck: main deck, raised walkway, six cargo hatches, six hatch rims, six valve housings, three paired deck conduits, six supports, bow bollards, stern bollards, foremast.
- Bridge: accommodation block, side face, front face, bridge wing, bridge roof, eight windows, door, ladder, four rail sections, rail posts.
- Transmission: mast foot, mast, crossbar, antenna, radar pedestal, radar scanner, navigation lamps, physical status light; expanding broadcast rings.
- Machinery: funnel body, funnel cap, funnel stripes, three vents, lifeboat, lifeboat cradle, outlet mouth and discharge stream.
- World: sky, sun halo, sun, moon, stars, cloud wisps, horizon haze, ocean, distant wavelets, foreground swells, wake, reflection, persistent oil slick with iridescent ribbons.

## Narrative timing
0–7 morning sailing; 7–12 sunset; 12–17 close-up / deliberate AIS switch-off at 15; 17–23 discharge; 23–29 departure; 29–40 AIS restored and hold on the missing interval.

## Evidence boundary
AIS supplies ship identity and movement information. Missing AIS is not itself proof of pollution. This illustrative deliberate shutdown is part of the user's story. The final claim is that the gap makes attribution harder, not impossible. Source: https://navcen.uscg.gov/ais-frequently-asked-questions . OceanTrace's existing project overview defines investigation support with uncertainty, not legal proof.

## User-requested alternative — minimal top view
23 October 2026: user requested a much simpler, true overhead view with Anatomy's monochrome machine-drawing look, while explicitly retaining the original. Implemented separately in `top-view.html`; `index.html` remains unchanged.

The alternative uses flat charcoal surfaces, grey outlines, a single white transmitter switch, sparse water marks and restrained AIS rings. No perspective, coloured ocean, horizon, or dashboard. Thirty seconds: morning 0–5, nightfall 5–10, AIS off 10–13, discharge 13–18, departure 18–23, AIS restored 23–30. Pause, replay and scrub controls retained. User review of this direction is pending.

### Approved direction and second refinement
User approved the minimal top view and requested a white/light morning that turns into dark mode at night, plus a longer resumed track matching the first recorded segment. Implemented with a coordinated background, surface, ink and control palette. Duration is now 42 seconds; AIS resumes at 23 seconds, the second segment grows until 38 seconds, then the completed view holds until 42. Both visible recorded segments are 300.90760127446515 world units long, with the unreported interval left blank. Camera pulls back to retain the whole sequence. The 30-second timing above describes the prior revision.
