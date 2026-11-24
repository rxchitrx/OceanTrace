# DVC and GitHub publication — 4 November 2026

Participants: Rachit and Codex. Source: authorized implementation in the OceanTrace project thread.

## Confirmed choices

- User requested DVC setup, commit and push of the project.
- Destination: user fork `rxchitrx/OceanTrace`, main branch.
- Data storage: a new folder at the root of the connected APFS SSD, `/Volumes/APFS/OceanTrace-DVC`.
- Git root of the vault is `/Volumes/APFS/Vault/Projects`, with unrelated work and no remote. Publication uses a clean clone at `/Volumes/APFS/Scratch/oceantrace-publish` and preserves research under `research/ann-dl/`, alongside the existing application.

## Implementation

- DVC 3.67.1 initialized as a subdirectory in the original research folder.
- Default local remote: `/Volumes/APFS/OceanTrace-DVC/store`; local cache: `/Volumes/APFS/OceanTrace-DVC/cache`, using reflink/copy.
- `Data.dvc`: 26,337 files, 30,605,442,113 bytes; manifest hash `dbc4279c3658a64b655a08af9d0359bc.dir`.
- `data_samples.dvc`: 10 files, 28,339,870 bytes; manifest hash `4bbbf4e4aa4271b8e3879a5403d5615c.dir`.
- Git carries code, notes, presentation, illustration, supplied PPT, DVC configuration and dataset manifests. Dataset binaries are DVC objects. Virtual environments, Python caches, machine files, nested Git metadata and unfinished download fragments are excluded.
- No credentials copied or committed. Source-text scan found no token/private-key patterns or private T3 credential-file references.
- Restore and update commands are documented in the research README.

## Storage boundary

The cache and remote are on the same SSD as the original data. This is versioned local storage, not an independent backup or a cloud upload. A Git clone needs access to the SSD to restore datasets. The vault and existing app checkout remain in place.

## Verification

- DVC add completed for both manifests.
- `dvc push -j 8` completed: 25,868 content-addressed objects pushed (deduplication reduces the object count).
- The clean publication checkout restored all 26,347 tracked data files with `dvc pull`.
- `dvc status`: data and pipelines are up to date.
- `dvc status --cloud`: cache and SSD remote are in sync.
- Code/document publication scan passed; no oversized Git files or token/private-key patterns found. Machine-specific `config.local` remains ignored.
- Existing application and fork start from the same `cadfe15` baseline. Publication includes only the research addition and a root README link. Git publication is recorded in the fork commit history.
