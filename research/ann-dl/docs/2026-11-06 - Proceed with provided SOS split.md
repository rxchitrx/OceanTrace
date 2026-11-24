# Proceed with the provided SOS split

- **Date:** 2026-11-06
- **Participants:** Rachit; Codex
- **Decision:** Stop further source-scene mapping for train/validation/test grouping. Proceed using the split distributed with the SOS patches; accept that source-scene overlap may remain.

## Evidence and caveat

Local preprocessing records 6,455 patches in `train/` and 1,615 in `val/` (`Research/Preprocessing README.md`). The CBD-Net authors' repository describes 6,455 training patches and 1,615 test patches. The counts align, but exact sample membership between the local refined release and the original repository split was not checked. Refer to the local split by its supplied folder name (`train`/`val`) unless membership equivalence is confirmed.

Scene-disjointness is not established. Leakage is possible, not proven. Any evaluation using this split is patch-split evaluation and must not be described as generalization to unseen source scenes. The user is willing to proceed despite that limitation.

## Next step

If training proceeds, preserve the supplied split. Avoid tuning against the held-out 1,615 patches; if a tuning validation set is needed, decide how to derive it from the training portion before training begins. No model training was started in this decision session.

## Related evidence

- [Preprocessing summary](Preprocessing%20README.md)
- [CBD-Net authors' repository and split description](https://github.com/CUG-URS/Marine-Oil-Spill-Detection-Network-CBDNet/blob/master/README.md)
- 50-tile matcher diagnostic (outputs retired)
