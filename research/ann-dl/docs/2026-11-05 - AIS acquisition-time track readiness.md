# AIS acquisition-time track readiness — 5 November 2026

Participants: Rachit and Codex. Source: user authorized inspecting verified AIS around satellite capture times to identify useful track-analysis scenes.

Read-only assessment of all 14 verified 2010 PALSAR scene-day exports completed. Agent-proposed diagnostic screen: at least 10 timestamps, 15 minutes of context on each side of acquisition, maximum 5-minute gap; split at conflicting same-ID/time positions and >60-knot edges. A separate ≥500 m movement diagnostic distinguishes moving examples from low-motion context. Thresholds are exploratory, not user-approved cleaning/training decisions.

Five scenes have moving candidates (89 scene/ID sequences); two further scenes have regular low-motion context; seven do not pass. ALPSRS233043050, 9 June afternoon, dominates with 171 regular / 81 moving sequences. Other moving candidates: ALPSRP232970580 (3), ALPSRP235450560 (1), ALPSRP237930550 (1), ALPSRP237930560 (3). Threshold sensitivity is substantial; source IDs and overlapping scenes do not establish independent vessel examples.

All 185 regular sequences were independently checked against CSV timing/conflicts; five boundary controls passed. Full-day and near-acquisition counts reconcile with coverage-audit.json; input SHA unchanged. Saved code, metrics, sensitivity and [report](AIS%20track-readiness%20README.md). No cleaning, interpolation or training. Seven 2017 scenes remain without matching raw AIS.

Next suggested action: visually inspect a moving 9 June sequence and its wider-source context. These well-source-event scenes cannot supply verified polluting-vessel labels.
