# OceanTrace — ANN status clarification

## Source
Direct user update in the vault project-by-project context check. Calendar date not recorded.

## Confirmed by user
- Only the ANN project is being pursued now; the team was not selected for SIH.
- Working prototype remains the classical detection + drift + AIS web application. No ANN model implementation/training progress was reported.
- The team has decided which models and other components to use for ANN, but has not yet provided those choices here.
- Next submission is PPT + prototype. Both are available; the existing web application will be demonstrated as the prototype. Artifacts have not been inspected in this session.

## Open questions
- Exact team-selected models and each model's task.
- Submission date.
- Location of PPT and model/architecture decision notes.

## Follow-up — supplied PPT and tentative submission
User reports submission is probably Wednesday; exact calendar date unconfirmed. Supplied file: [[College projects/OceanTrace/ANN_DL  Oil Slick (1).pptx]]. Six slides inspected via OOXML text extraction, not visual rendering or citation verification. Deck date: 30 September 2026; do not substitute this for the deadline.

Agreed direction from slides 4–5:
- U-Net CNN for pixel-wise slick masks.
- LSTM for AIS track forecasting/gaps only, compared with Kalman/constant-speed baselines.
- Physics-based drift for slick transport/source reconstruction.
- Classical threshold M0 baseline; scene-wise splits and shared metrics; refined Deep-SAR SOS; DARTIS boxes used for hard-negative tests, not segmentation truth; physics-only ranking comparison.

Earlier open questions about PPT location and model families are resolved by this follow-up. Exact configurations, training/fusion details, dataset readiness, and deadline remain unknown. No new trained models or runtime verification established.

## Next action
Continue the project-by-project context check. For this submission, label existing classical prototype versus planned ANN components explicitly.
