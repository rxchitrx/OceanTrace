# AIS preprocessing quality audit — 4 November 2026

Participants: Rachit and Codex. Source: user asked to start AIS preprocessing while SOS mapping runs. Scope remains preprocessing, without model training. User wants hands-on understanding.

Completed a low-memory read-only audit with `Tools/sos-pilot/quality_ais.py`. All 2,228,788 regional reports /3,359 MMSI groups reconciled. Identified unavailable field encodings and 642 short-interval edges above a provisional 60-knot review threshold. Kept valid zero speeds distinct from missing observations. No records changed or removed. Checks and their limitations are in [the quality record](AIS%20quality-audit%20README.md).

Next agreed scope is not a new cleaning policy: agent recommends inspecting one flagged jump together before selecting rules. No resampling, interpolation, normalization, vessel split or training performed in this pass. Mapping continues separately.

## Hands-on jump inspection

User asked to inspect one flagged jump. Extracted 14 reports for MMSI367590950 from22:58–23:14UTC on2020-07-01 into Data/AIS/quality-audit/jump-example.json. Interactive distance-from-initial-position plot saved as jump-example.html and rendered in chat.

At23:04:55 positionA; at23:06:51 positionB21.822km away (116seconds, implied365.68kn, reported17.6kn); at23:07:55 positionC~2.2metres fromA (64seconds fromB, implied662.86kn). Surrounding positions cluster nearA. This supports flagging the isolated report for investigation, not proof of its exact cause or the vessel's true route. One suspect point contributes two flagged edges. No rows deleted or interpolated; a cleaning rule has not yet been adopted.
