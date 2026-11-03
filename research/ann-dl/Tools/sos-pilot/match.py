"""Conservative 50-patch registration pilot. Requires all 21 full scene rasters.

Scene files go under Data/SOS/scenes/<published_id>.tif. Input must be a
grayscale, calibrated/detected image, not complex SLC or a browse JPEG.
Scores are diagnostics, not calibrated match probabilities.
"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
import rasterio
from rasterio.enums import Resampling

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Data/SOS'

def normalize(image):
    x = np.asarray(image, dtype=np.float32)
    valid = np.isfinite(x) & (x > 0)
    if not valid.any():
        return np.zeros(x.shape, np.uint8)
    x = np.log1p(np.maximum(np.nan_to_num(x), 0))
    low, high = np.percentile(x[valid], [1, 99])
    return np.clip((x - low) * 255 / max(high - low, 1e-6), 0, 255).astype('uint8')

def features(image):
    return cv2.SIFT_create(nfeatures=25000, contrastThreshold=0.02).detectAndCompute(image, None)

def register(patch, scene, scene_features=None):
    kp, des = features(patch)
    skp, sdes = scene_features if scene_features is not None else features(scene)
    if des is None or sdes is None or len(sdes) < 2:
        return None
    pairs = cv2.BFMatcher().knnMatch(des, sdes, k=2)
    good = [a for pair in pairs if len(pair) == 2 for a, b in [pair] if a.distance < 0.7 * b.distance]
    if len(good) < 8:
        return None
    source = np.float32([kp[m.queryIdx].pt for m in good])
    target = np.float32([skp[m.trainIdx].pt for m in good])
    matrix, inliers = cv2.estimateAffinePartial2D(source, target, method=cv2.RANSAC,
                                                ransacReprojThreshold=3, maxIters=5000)
    if matrix is None:
        return None
    keep = inliers.ravel().astype(bool)
    error = np.linalg.norm(cv2.transform(source[None], matrix)[0] - target, axis=1)
    aligned = cv2.warpAffine(scene, matrix, (patch.shape[1], patch.shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
    support = cv2.warpAffine(np.ones(scene.shape, np.uint8), matrix, (patch.shape[1], patch.shape[0]), flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP) > 0
    if support.mean() < .95 or patch[support].std() < 1 or aligned[support].std() < 1:
        return None
    corr = float(np.corrcoef(patch[support], aligned[support])[0, 1])
    # Spread prevents a tiny cluster of repeated features from deciding the fit.
    hull_area = cv2.contourArea(cv2.convexHull(source[keep])) if keep.sum() >= 3 else 0
    return dict(inliers=int(keep.sum()), feature_matches=len(good), inlier_ratio=float(keep.mean()),
                correlation=corr, reprojection_p90=float(np.percentile(error[keep], 90)),
                coverage=float(hull_area / patch.size), affine=matrix.tolist())

def run():
    selected = json.loads((DATA / 'pilot/selected_50.json').read_text())
    assert len(selected) == 50, 'Pilot is restricted to exactly 50 selected patches'
    metadata = json.loads((DATA / 'metadata/scenes.json').read_text())
    paths = {s['published_id']: DATA / 'scenes' / (s['published_id'].replace(' ', '_') + '.tif') for s in metadata}
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        report = dict(status='blocked_missing_full_source_rasters', selected_patches=50,
                      attempted_real_matches=0, missing_scenes=missing,
                      note='Catalogue previews are deliberately excluded from registration.')
        (DATA / 'pilot/status.json').write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return 2
    scenes = []
    for s in metadata:
        with rasterio.open(paths[s['published_id']]) as raster:
            if raster.dtypes[0].startswith('complex'):
                raise ValueError('Complex input must be processed to detected intensity first')
            for size in (2048, 4096, 8192):
                scale = min(1, size / max(raster.shape))
                shape = tuple(max(1, round(v * scale)) for v in raster.shape)
                image = normalize(raster.read(1, out_shape=shape, resampling=Resampling.average, masked=True).filled(0))
                scenes.append((s, image, features(image), scale))
                if scale == 1:
                    break
    results = []
    for p in selected:
        patch = cv2.imread(str(DATA / p['file']), cv2.IMREAD_GRAYSCALE)
        candidates = []
        for s, scene, desc, scale in scenes:
            sensor = 'palsar' if s['sensor'] == 'PALSAR' else 'sentinel'
            if sensor != p['sensor']:
                continue
            match = register(patch, scene, desc)
            if match:
                candidates.append(dict(scene=s['published_id'], raster_scale=scale, **match))
        # Deduplicate pyramid candidates before comparing competing scenes.
        best_by_scene = {}
        for c in sorted(candidates, key=lambda c: (c['correlation'], c['inliers']), reverse=True):
            best_by_scene.setdefault(c['scene'], c)
        ranked = list(best_by_scene.values())
        best = ranked[0] if ranked else None
        strong = best and best['inliers'] >= 12 and best['inlier_ratio'] >= .6 and best['coverage'] >= .15 and best['correlation'] >= .75
        margin = best['correlation'] - ranked[1]['correlation'] if len(ranked) > 1 else None
        evidence_file = None
        if best:
            s, image, _, scale = next(item for item in scenes if item[0]['published_id'] == best['scene'] and item[3] == best['raster_scale'])
            matrix = np.asarray(best['affine'], np.float64)
            aligned = cv2.warpAffine(image, matrix, (patch.shape[1], patch.shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
            comparison = np.hstack([patch, aligned, cv2.absdiff(patch, aligned)])
            evidence_file = 'pilot/' + p['id'] + '-candidate-comparison.png'
            cv2.imwrite(str(DATA / evidence_file), comparison)
            corners = np.float32([[[0, 0], [patch.shape[1], 0], [patch.shape[1], patch.shape[0]], [0, patch.shape[0]]]])
            best['source_pixel_corners'] = (cv2.transform(corners, matrix)[0] / scale).tolist()
        # Never silently auto-assign ancestry before real positive-control calibration.
        results.append(dict(patch=p['id'], status='candidate_needs_review' if strong and (margin is None or margin >= .1) else 'unknown',
                            correlation_margin=margin, evidence_file=evidence_file, candidates=ranked[:3]))
        print(p['id'], results[-1]['status'], flush=True)
    (DATA / 'pilot/results.json').write_text(json.dumps(results, indent=2))
    (DATA / 'pilot/status.json').write_text(json.dumps(dict(status='pilot_completed', attempted_real_matches=50, auto_assigned=0), indent=2))
    return 0

def controls():
    rng = np.random.default_rng(20261103)
    scene = np.clip(rng.normal(100, 22, (1024, 1024)), 0, 255).astype('uint8')
    for _ in range(250):
        x, y = rng.integers(20, 1000, 2)
        cv2.circle(scene, (int(x), int(y)), int(rng.integers(3, 20)), int(rng.integers(20, 230)), -1)
    scene = cv2.GaussianBlur(scene, (3, 3), .5)
    checks = []
    for k in range(4):
        patch = np.rot90(scene[300:556, 400:656], k).copy()
        match = register(patch, scene)
        assert match and match['inliers'] >= 12 and match['correlation'] > .9, (k, match)
        checks.append(dict(control='synthetic_rotation_' + str(k * 90), **match))
    assert register(np.zeros((256, 256), np.uint8), scene) is None
    checks.append(dict(control='blank_patch_rejected', passed=True))
    assert register(rng.integers(0, 256, (256, 256), dtype=np.uint8), scene) is None
    checks.append(dict(control='unrelated_noise_rejected', passed=True))
    (DATA / 'pilot/software_controls.json').write_text(json.dumps(checks, indent=2))
    print('6 synthetic software controls passed. Not a real SOS matching result.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    if args.controls:
        controls()
    else:
        raise SystemExit(run())
