# SOS seven-miss multiscale regression — 4 November 2026

Participants: Rachit and Codex. Source: user requested only tile-to-source mapping and authorized fixing the seven known misses first.

User question: why resize to 256? Clarification: released tiles are already 256×256; no new shrinking of supplied tiles was performed. Approximately 416-pixel source footprints are inferred from alignments, not a documented creator recipe.

Implemented `Tools/sos-mapping/multiscale.py`. All seven missed cases had insufficient descriptor matches in the native index. Multi-scale views plus exact descriptor matching recovered all seven candidate reference locations, while retaining the five earlier native candidates. Searched 14 PALSAR scenes at two pyramid levels for 12 real patches and two controls, 392 queries, about 24.3 seconds. Native source validation gates unchanged. Both simple negatives rejected; all seven evidence panels visually inspected.

Results: regression report (mapping outputs retired). No automatic ancestry assignments, no independent accuracy estimate, no full-corpus rerun. Original results retained. Next recommendation: a varied regression batch outside these tuning cases, including Sentinel and harder negatives.
