# OceanTrace — problem animation

Date: 23 October 2026. Participants: Rachit and Codex. Source: direct user request in T3 Code; Anatomy skill explicitly requested.

## User direction
- Show an ocean and ship sailing in the morning, continuously transmitting data.
- Fade into night, move the camera closer, and show the ship itself stopping transmission.
- Show oil and oily sludge being discharged, then the ship sailing away and resuming transmission to obscure its connection to the slick.
- Use the animation and drawing aspects of Anatomy; no machine metaphor required.

## Artifact
- [Open the standalone animation](../Animation/index.html) — 40 seconds, six scenes, pause, replay, timeline scrubbing, and chapter buttons. Works without installation or external dependencies.
- [[College projects/OceanTrace/Animation/Design|Concept, parts and timing]].
- SVG ocean and detailed tanker; day/night transition, camera move, AIS pulses, on-board switch indicator, persistent oil slick, and authority track with a missing interval.

## Agent choices and evidence boundary
- Interpreted “AIR data” as AIS identity/position broadcasts. This is an agent interpretation, not a separately confirmed user correction.
- This is a fictional, time-compressed problem illustration. The gap makes attribution harder; it does not establish that attribution is impossible or that missing AIS alone proves pollution.
- AIS terminology checked against [US Coast Guard AIS FAQ](https://navcen.uscg.gov/ais-frequently-asked-questions).
- No application implementation, model training, or actual spill-attribution result is implied.

## Verification
Browser screenshots inspected at desktop and 390-pixel phone width, including discharge close-up and ending. Checked phase boundaries, captions, AIS state, chapter jumps, scrubbing, replay, and pause. Reduced-motion mode starts paused; no horizontal overflow or console errors in the checked browser runs. This is custom SVG scene artwork, not an Anatomy kit solid model; no kit geometry audit is claimed.

## Open questions and next step
User visual review pending. No MP4, soundtrack, narration, or PPT embedding was requested or produced. Next: review the animation's pacing and illustration style before deciding whether an exported video is needed.

## Follow-up — minimal overhead version
User found the original too detailed and requested a top view with Anatomy's minimal machine-drawing style. Explicit instruction: keep the original version as well.

- Created [minimal top-view alternative](../Animation/top-view.html), a separate 30-second monochrome SVG animation. Preserved the original `index.html`; SHA-256 unchanged before/after this revision.
- Retained the requested story, including nightfall, a closer view, on-board switch-off, discharge, departure and resumed AIS. Simplified the ocean, ship and controls.
- Desktop and phone previews inspected; phone discharge and ending screenshots checked. Verified AIS phase boundaries, frozen recorded track during shutdown, replay, pause, reduced-motion initial state and no horizontal overflow. Checked browser console was clean.
- Next: user review of the simplified visual direction. No preference for this version beyond the requested style change is assumed.

## Follow-up — light morning and extended recorded track
User approved the minimal direction, then requested morning in light mode transitioning into dark mode at night, and a resumed recorded line equal in length to the first segment.

- Updated `top-view.html` to fade its full scene and controls from light to dark. Preserved `index.html` unchanged.
- Extended duration to 42 seconds, with resumed travel from 23–38 seconds and a final four-second hold. Camera pulls back to show the two recorded segments with the blank interval between them.
- Verified both finished segments measure 300.90760127446515 world units. Browser checks covered phase boundaries, light/dark background and text colours, pause, reduced-motion initial state and no horizontal overflow. Inspected desktop and phone day/end screenshots and the transition preview; console clean.
- Next: user review of the transition and extended ending.

## Follow-up — AIS indicator colours
User requested green when transmitting and red when silent. Updated both the on-board transmitter indicator and the AIS status dot in `top-view.html`. Both use the same AIS state: green before 10 seconds, red during 10–23 seconds, green after transmission resumes. Verified colours at 0, 10 and 23 seconds in browser preview. Other versions unchanged.
