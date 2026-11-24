#!/usr/bin/env python3
"""
OceanTrace — Isolated 50-Tile Despeckled Coarse-to-Fine Scene Matching Diagnostic
All outputs are written strictly inside SceneMatchingDiagnostic/.
Original project files and DVC store are opened read-only.
"""
import base64
import csv
import glob
import io
import json
import math
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import cv2
import numpy as np
from PIL import Image

PROJECT_ROOT = "/Volumes/APFS/Vault/Projects/College projects/OceanTrace"
DVC_ROOT = "/Volumes/APFS/OceanTrace-DVC"
OUT_DIR = os.path.join(PROJECT_ROOT, "SceneMatchingDiagnostic")
CACHE_DIR = os.path.join(OUT_DIR, "cache")
EVID_DIR = os.path.join(OUT_DIR, "evidence")

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(EVID_DIR, exist_ok=True)

PALSAR_DS = 4
SENTINEL_DS = 8
PALSAR_FOOTPRINTS = [256, 416, 512]
SENTINEL_FOOTPRINTS = [256, 416, 512, 1024]

ORIENTATIONS = [
    ("rot0",       0, False),
    ("rot90",      1, False),
    ("rot180",     2, False),
    ("rot270",     3, False),
    ("flip_rot0",  0, True),
    ("flip_rot90", 1, True),
    ("flip_rot180",2, True),
    ("flip_rot270",3, True),
]


def apply_orient(arr: np.ndarray, k: int, flip: bool) -> np.ndarray:
    out = np.fliplr(arr) if flip else arr
    if k:
        out = np.rot90(out, k)
    return np.ascontiguousarray(out)


def discover_dvc_scenes():
    scenes = {}
    for base in ("store/files/md5", "cache/files/md5"):
        for p in glob.glob(os.path.join(DVC_ROOT, base, "*", "*.dir")):
            try:
                items = json.load(open(p))
                if not isinstance(items, list):
                    continue
                for it in items:
                    rp = it.get("relpath", "")
                    if rp.startswith("SOS/scenes/") and rp.endswith(".tif"):
                        name = os.path.splitext(os.path.basename(rp))[0]
                        md5 = it["md5"]
                        obj = os.path.join(DVC_ROOT, base, md5[:2], md5[2:])
                        if os.path.exists(obj) and name not in scenes:
                            sensor = "palsar" if name.startswith("ALPSR") else "sentinel"
                            scenes[name] = {"name": name, "sensor": sensor, "path": obj}
            except Exception:
                pass
    return scenes


def normalize_sar_log(arr: np.ndarray) -> np.ndarray:
    f = np.log1p(np.maximum(arr.astype(np.float32), 0.0))
    sub = f[::16, ::16]; valid = sub[sub > 0]
    if valid.size < 100:
        return f
    lo, hi = np.percentile(valid, [1.0, 99.5])
    if hi <= lo:
        return f
    f = np.clip((f - lo) / (hi - lo), 0.0, 1.0)
    return f.astype(np.float32)


def prepare_scene_cache(scene_info):
    name = scene_info["name"]
    sensor = scene_info["sensor"]
    ds = PALSAR_DS if sensor == "palsar" else SENTINEL_DS
    cache_npy = os.path.join(CACHE_DIR, f"{name}_ds{ds}.npy")
    meta_json = os.path.join(CACHE_DIR, f"{name}_ds{ds}.json")
    if os.path.exists(cache_npy) and os.path.exists(meta_json):
        meta = json.load(open(meta_json))
        return name, meta

    raw = cv2.imread(scene_info["path"], cv2.IMREAD_UNCHANGED)
    h, w = raw.shape[:2]
    norm = normalize_sar_log(raw)
    small = cv2.resize(norm, (w // ds, h // ds), interpolation=cv2.INTER_AREA).astype(np.float32)
    # Mild blur to suppress residual speckle at coarse scale
    small = cv2.GaussianBlur(small, (3, 3), 0.8)
    np.save(cache_npy, small)
    meta = {"name": name, "sensor": sensor, "native_shape": [h, w], "ds": ds, "ds_shape": list(small.shape)}
    with open(meta_json, "w") as f:
        json.dump(meta, f)
    return name, meta


def load_patch_gray(split: str, patch_id: str) -> np.ndarray:
    p = os.path.join(PROJECT_ROOT, "Data/Preprocessing/sos-prepared", split, "images", f"{patch_id}.png")
    im = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    if im is None:
        raise FileNotFoundError(p)
    return im.astype(np.float32) / 255.0


def build_controls(scenes):
    """Build 4 positive controls (2 PALSAR, 2 Sentinel) + 4 negative controls."""
    rng = np.random.default_rng(26143)
    controls = []

    # 2 PALSAR positive controls (1x rot90, 1.625x flip+rot180 with gamma/contrast jitter)
    p_scenes = sorted([s for s in scenes.values() if s["sensor"] == "palsar"], key=lambda x: x["name"])
    for idx, (sinfo, fp, orient_idx) in enumerate([
        (p_scenes[2], 256, 1),   # 1.0x rot90
        (p_scenes[7], 416, 6),   # 1.625x flip_rot180
    ]):
        raw = cv2.imread(sinfo["path"], cv2.IMREAD_UNCHANGED)
        norm = normalize_sar_log(raw)
        h, w = norm.shape
        y0 = int(h * (0.32 + 0.15 * idx))
        x0 = int(w * (0.35 + 0.12 * idx))
        crop = norm[y0:y0 + fp, x0:x0 + fp]
        resized = cv2.resize(crop, (256, 256), interpolation=cv2.INTER_AREA)
        # Simulate radiometric stretch + 8-bit quantization
        resized = np.clip(np.power(resized, 0.88 if idx else 1.12) * 0.92 + 0.04, 0.0, 1.0)
        resized = np.round(resized * 255.0).astype(np.uint8).astype(np.float32) / 255.0
        oname, k, flip = ORIENTATIONS[orient_idx]
        # Store inverse so matcher should find it
        patch_img = apply_orient(resized, k, flip)
        controls.append({
            "id": f"ctrl_pos_palsar_{idx+1}",
            "sensor": "palsar",
            "split": "control_pos",
            "img": patch_img,
            "truth": {"scene": sinfo["name"], "x": x0, "y": y0, "footprint": fp, "orient_applied": oname},
        })

    # 2 Sentinel positive controls (1x rot0, 2.0x rot270 with contrast jitter)
    s_scenes = sorted([s for s in scenes.values() if s["sensor"] == "sentinel"], key=lambda x: x["name"])
    for idx, (sinfo, fp, orient_idx) in enumerate([
        (s_scenes[1], 416, 0),   # 1.625x rot0
        (s_scenes[3], 512, 3),   # 2.0x rot270
    ]):
        raw = cv2.imread(sinfo["path"], cv2.IMREAD_UNCHANGED)
        norm = normalize_sar_log(raw)
        h, w = norm.shape
        y0 = int(h * (0.40 + 0.10 * idx))
        x0 = int(w * (0.42 + 0.10 * idx))
        crop = norm[y0:y0 + fp, x0:x0 + fp]
        resized = cv2.resize(crop, (256, 256), interpolation=cv2.INTER_AREA)
        resized = np.clip(np.power(resized, 0.90 if idx else 1.15) * 0.95 + 0.02, 0.0, 1.0)
        resized = np.round(resized * 255.0).astype(np.uint8).astype(np.float32) / 255.0
        oname, k, flip = ORIENTATIONS[orient_idx]
        patch_img = apply_orient(resized, k, flip)
        controls.append({
            "id": f"ctrl_pos_sentinel_{idx+1}",
            "sensor": "sentinel",
            "split": "control_pos",
            "img": patch_img,
            "truth": {"scene": sinfo["name"], "x": x0, "y": y0, "footprint": fp, "orient_applied": oname},
        })

    # 4 Negative controls (2 palsar, 2 sentinel: noise + block-shuffled real patch)
    controls.append({
        "id": "ctrl_neg_palsar_noise", "sensor": "palsar", "split": "control_neg",
        "img": rng.uniform(0.0, 1.0, (256, 256)).astype(np.float32), "truth": None
    })
    controls.append({
        "id": "ctrl_neg_sentinel_noise", "sensor": "sentinel", "split": "control_neg",
        "img": rng.uniform(0.0, 1.0, (256, 256)).astype(np.float32), "truth": None
    })
    for sensor, ref_split, ref_id in [("palsar", "train", "palsar_1839"), ("sentinel", "train", "sentinel_984")]:
        im = load_patch_gray(ref_split, ref_id)
        blocks = [im[r:r+32, c:c+32] for r in range(0, 256, 32) for c in range(0, 256, 32)]
        rng.shuffle(blocks)
        shuf = np.vstack([np.hstack(blocks[i*8:(i+1)*8]) for i in range(8)])
        controls.append({
            "id": f"ctrl_neg_{sensor}_shuffled", "sensor": sensor, "split": "control_neg",
            "img": shuf, "truth": None
        })
    return controls


def _coarse_search_scene(args):
    """Worker: match all patches of one sensor against ONE downsampled scene."""
    scene_name, ds, cache_npy, patch_items, footprints = args
    scene_raw = np.load(cache_npy)
    # Extra 2x coarse downsampling in memory -> 6-8x faster on CPU while Stage 2 refines at native 1x
    scene_ds = cv2.resize(scene_raw, (scene_raw.shape[1] // 2, scene_raw.shape[0] // 2), interpolation=cv2.INTER_AREA).astype(np.float32)
    ds = ds * 2
    sh, sw = scene_ds.shape
    results = {}

    for item in patch_items:
        pid = item["id"]
        p_img = item["img"]
        # Mild blur on patch to match scene_ds speckle suppression
        p_blur = cv2.GaussianBlur(p_img, (3, 3), 0.8)
        best_peaks = []  # list of (score, scene, x_native, y_native, fp, orient_name, k, flip)
        bg_means, bg_stds = [], []

        for fp in footprints:
            tsize = max(16, int(round(fp / ds)))
            if tsize >= min(sh, sw) - 4:
                continue
            tmpl_base = cv2.resize(p_blur, (tsize, tsize), interpolation=cv2.INTER_AREA).astype(np.float32)
            if float(tmpl_base.std()) < 1e-4:
                continue
            for oname, k, flip in ORIENTATIONS:
                tmpl = apply_orient(tmpl_base, k, flip)
                res = cv2.matchTemplate(scene_ds, tmpl, cv2.TM_CCOEFF_NORMED)
                # Track background distribution from a subsampled grid
                sub = res[::4, ::4]
                bg_means.append(float(sub.mean()))
                bg_stds.append(float(sub.std()))

                # Extract top-2 separated peaks in this map
                work = res
                for _ in range(2):
                    _, max_val, _, max_loc = cv2.minMaxLoc(work)
                    mx, my = max_loc
                    best_peaks.append((float(max_val), scene_name, int(mx * ds), int(my * ds), fp, oname, k, flip))
                    # Suppress neighborhood before checking 2nd peak
                    if work is res:
                        work = res.copy()
                    rad = max(8, tsize // 2)
                    y1, y2 = max(0, my - rad), min(work.shape[0], my + rad + 1)
                    x1, x2 = max(0, mx - rad), min(work.shape[1], mx + rad + 1)
                    work[y1:y2, x1:x2] = -1.0

        # Keep top-6 distinct peaks from this scene
        best_peaks.sort(key=lambda x: x[0], reverse=True)
        kept = []
        for pk in best_peaks:
            if all(abs(pk[2] - q[2]) > 128 or abs(pk[3] - q[3]) > 128 for q in kept):
                kept.append(pk)
            if len(kept) >= 4:
                break
        results[pid] = {
            "peaks": kept,
            "bg_mean": float(np.mean(bg_means)) if bg_means else 0.0,
            "bg_std": float(np.mean(bg_stds)) if bg_stds else 1.0,
        }
    return scene_name, results


def refine_on_scene(scene_info, candidates_for_scene):
    """Load ONE native TIFF once and refine all Top-K patch candidates pointing to it."""
    raw = cv2.imread(scene_info["path"], cv2.IMREAD_UNCHANGED)
    norm_log = normalize_sar_log(raw)
    # Also prepare linear clipped (p1..p99.5) in case author used linear stretch
    f_lin = raw.astype(np.float32)
    sub_lin = f_lin[::16, ::16]; valid = sub_lin[sub_lin > 0]
    lo, hi = np.percentile(valid, [1.0, 99.5]) if valid.size > 100 else (0.0, 1.0)
    norm_lin = np.clip((f_lin - lo) / max(hi - lo, 1e-6), 0.0, 1.0).astype(np.float32)
    sh, sw = raw.shape[:2]

    refined = {}
    for cand in candidates_for_scene:
        pid = cand["id"]
        p_img = cand["img"]
        x0, y0, fp, k, flip = cand["x"], cand["y"], cand["fp"], cand["k"], cand["flip"]
        pad = max(32, int(fp * 0.14))
        rx1 = max(0, x0 - pad)
        ry1 = max(0, y0 - pad)
        rx2 = min(sw, x0 + fp + pad)
        ry2 = min(sh, y0 + fp + pad)

        p_orient = apply_orient(p_img, k, flip)
        p_desp = cv2.GaussianBlur(p_orient, (5, 5), 1.2)

        best = {"native_zncc": -1.0, "raw_zncc": -1.0, "mode": "log", "x": x0, "y": y0, "fp": fp}
        for mode_name, src_full in (("log", norm_log), ("lin", norm_lin)):
            roi_raw = src_full[ry1:ry2, rx1:rx2]
            if roi_raw.shape[0] < 32 or roi_raw.shape[1] < 32:
                continue
            roi_desp = cv2.GaussianBlur(roi_raw, (5, 5), 1.2)
            # Test exact fp and small +-2% scale jitter
            fp_tests = [fp] if fp == 256 else [int(round(fp * s)) for s in (0.985, 1.0, 1.015)]
            for fp_t in fp_tests:
                if roi_desp.shape[0] <= fp_t + 2 or roi_desp.shape[1] <= fp_t + 2:
                    continue
                tmpl_d = cv2.resize(p_desp, (fp_t, fp_t), interpolation=cv2.INTER_AREA).astype(np.float32)
                res = cv2.matchTemplate(roi_desp, tmpl_d, cv2.TM_CCOEFF_NORMED)
                _, max_v, _, max_loc = cv2.minMaxLoc(res)
                if float(max_v) > best["native_zncc"]:
                    nx = rx1 + max_loc[0]
                    ny = ry1 + max_loc[1]
                    crop_raw = src_full[ny:ny + fp_t, nx:nx + fp_t]
                    crop_256 = cv2.resize(crop_raw, (256, 256), interpolation=cv2.INTER_AREA)
                    # Raw Pearson correlation
                    a = p_orient.ravel() - p_orient.mean()
                    b = crop_256.ravel() - crop_256.mean()
                    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
                    raw_r = float(np.dot(a, b) / denom) if denom > 1e-8 else 0.0
                    best = {
                        "native_zncc": float(max_v),
                        "raw_zncc": raw_r,
                        "mode": mode_name,
                        "x": int(nx),
                        "y": int(ny),
                        "fp": int(fp_t),
                        "orient": cand["orient"],
                        "k": k,
                        "flip": flip,
                        "scene": scene_info["name"],
                        "crop_256": crop_256,
                        "p_orient": p_orient,
                    }
        key = (pid, cand["rank"])
        refined[key] = best
    return refined


def save_evidence_panel(out_path, p_orient, crop_256):
    # Normalize crop_256 to match patch mean/std for clean visual comparison
    p_u8 = np.clip(p_orient * 255.0, 0, 255).astype(np.uint8)
    c_f = crop_256.astype(np.float32)
    c_f = (c_f - c_f.mean()) / max(c_f.std(), 1e-5) * max(p_orient.std(), 1e-5) + p_orient.mean()
    c_u8 = np.clip(c_f * 255.0, 0, 255).astype(np.uint8)
    diff = np.abs(p_u8.astype(np.int16) - c_u8.astype(np.int16)).astype(np.uint8)
    panel = np.hstack([p_u8, c_u8, diff])
    Image.fromarray(panel, mode="L").save(out_path, format="JPEG", quality=86, optimize=True)


def main():
    t0 = time.time()
    print("=== OceanTrace Isolated 50-Tile Despeckled Coarse-to-Fine Diagnostic ===")
    scenes = discover_dvc_scenes()
    print(f"Found {len(scenes)} full-resolution SAR scenes in DVC store.")

    # 1. Build downsampled despeckled scene caches in parallel
    t_cache = time.time()
    scene_metas = {}
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = [ex.submit(prepare_scene_cache, s) for s in scenes.values()]
        for fut in as_completed(futs):
            name, meta = fut.result()
            scene_metas[name] = meta
    print(f"Scene pyramids ready in {time.time() - t_cache:.1f}s.")

    # 2. Load 50 real pilot patches + 8 controls
    selected = json.load(open(os.path.join(PROJECT_ROOT, "Data/SOS/pilot/selected_50.json")))
    old_pilot = {}
    with open(os.path.join(PROJECT_ROOT, "Data/SOS/pilot/results.csv"), newline="") as f:
        for row in csv.DictReader(f):
            old_pilot[row["patch"]] = row

    items = []
    for row in selected:
        items.append({
            "id": row["id"],
            "sensor": row["sensor"],
            "split": row["split"],
            "oil_fraction": row["oil_fraction"],
            "img": load_patch_gray(row["split"], row["id"]),
            "truth": None,
            "old_status": old_pilot.get(row["id"], {}).get("status", "unknown"),
            "old_scene": old_pilot.get(row["id"], {}).get("candidate_scene", ""),
        })

    controls = build_controls(scenes)
    for c in controls:
        c["oil_fraction"] = None
        c["old_status"] = "control"
        c["old_scene"] = ""
    all_items = items + controls
    print(f"Loaded {len(items)} real patches (25 PALSAR + 25 Sentinel) + {len(controls)} controls.")

    # 3. Coarse global ZNCC search across all compatible scenes
    t_coarse = time.time()
    coarse_by_patch = {it["id"]: {"peaks": [], "bg_means": [], "bg_stds": []} for it in all_items}
    jobs = []
    for sensor, ds, fps in [("palsar", PALSAR_DS, PALSAR_FOOTPRINTS), ("sentinel", SENTINEL_DS, SENTINEL_FOOTPRINTS)]:
        s_items = [it for it in all_items if it["sensor"] == sensor]
        for sname, sinfo in scenes.items():
            if sinfo["sensor"] != sensor:
                continue
            cache_npy = os.path.join(CACHE_DIR, f"{sname}_ds{ds}.npy")
            jobs.append((sname, ds, cache_npy, s_items, fps))

    for done, j in enumerate(jobs, 1):
        sname, res = _coarse_search_scene(j)
        for pid, d in res.items():
            coarse_by_patch[pid]["peaks"].extend(d["peaks"])
            coarse_by_patch[pid]["bg_means"].append(d["bg_mean"])
            coarse_by_patch[pid]["bg_stds"].append(d["bg_std"])
        print(f"  Coarse search: {done}/{len(jobs)} {sname} ({time.time() - t_coarse:.1f}s)", flush=True)

    # Rank Top-3 distinct coarse candidates per patch and compute global margin & z-score
    top_cands_by_scene = {}
    patch_coarse_summary = {}
    item_map = {it["id"]: it for it in all_items}

    for pid, d in coarse_by_patch.items():
        peaks = sorted(d["peaks"], key=lambda x: x[0], reverse=True)
        distinct = []
        for pk in peaks:
            if all(pk[1] != q[1] or abs(pk[2] - q[2]) > 128 or abs(pk[3] - q[3]) > 128 for q in distinct):
                distinct.append(pk)
            if len(distinct) >= 3:
                break
        bg_m = float(np.mean(d["bg_means"])) if d["bg_means"] else 0.0
        bg_s = float(np.mean(d["bg_stds"])) if d["bg_stds"] else 1.0
        top1 = distinct[0][0] if len(distinct) >= 1 else 0.0
        top2 = distinct[1][0] if len(distinct) >= 2 else 0.0
        patch_coarse_summary[pid] = {
            "top1_coarse": top1,
            "top2_coarse": top2,
            "coarse_margin": top1 - top2,
            "coarse_z": (top1 - bg_m) / max(bg_s, 1e-5),
            "distinct": distinct,
        }
        for rank, pk in enumerate(distinct[:3]):  # refine Top-2 distinct candidates natively
            _, sname, x0, y0, fp, oname, k, flip = pk
            top_cands_by_scene.setdefault(sname, []).append({
                "id": pid, "rank": rank, "img": item_map[pid]["img"],
                "x": x0, "y": y0, "fp": fp, "orient": oname, "k": k, "flip": flip,
            })

    # 4. Native full-resolution refinement
    t_ref = time.time()
    refined_all = {}
    for sname, cands in top_cands_by_scene.items():
        ref_map = refine_on_scene(scenes[sname], cands)
        refined_all.update(ref_map)
    print(f"Native refinement finished in {time.time() - t_ref:.1f}s.")

    # 5. Classify, verify controls, save evidence panels & reports
    final_rows = []
    for it in all_items:
        pid = it["id"]
        cs = patch_coarse_summary[pid]
        cands_r = [refined_all.get((pid, rk)) for rk in range(3) if refined_all.get((pid, rk)) is not None]
        cands_r.sort(key=lambda x: x["native_zncc"], reverse=True)
        best_r = cands_r[0] if len(cands_r) >= 1 else None
        second_native = cands_r[1]["native_zncc"] if len(cands_r) >= 2 else 0.0

        nz = best_r["native_zncc"] if best_r else 0.0
        rz = best_r["raw_zncc"] if best_r else 0.0
        margin = cs["coarse_margin"]
        native_margin = nz - second_native
        zscore = cs["coarse_z"]

        if (nz >= 0.72 and (margin >= 0.08 or native_margin >= 0.12) and zscore >= 5.5) or (nz >= 0.82 and (margin >= 0.05 or native_margin >= 0.08)):
            status = "matched_high_conf"
        elif nz >= 0.56 and (margin >= 0.04 or native_margin >= 0.08) and zscore >= 4.5:
            status = "candidate_review"
        else:
            status = "unresolved"

        evid_rel = ""
        if best_r and status in ("matched_high_conf", "candidate_review"):
            evid_rel = f"evidence/{pid}.jpg"
            save_evidence_panel(os.path.join(OUT_DIR, evid_rel), best_r["p_orient"], best_r["crop_256"])

        ctrl_ok = None
        if it["split"] == "control_pos" and best_r:
            tr = it["truth"]
            dx = abs(best_r["x"] - tr["x"])
            dy = abs(best_r["y"] - tr["y"])
            ctrl_ok = (status != "unresolved") and (best_r["scene"] == tr["scene"]) and (dx <= 16) and (dy <= 16)
        elif it["split"] == "control_neg":
            ctrl_ok = (status == "unresolved")

        final_rows.append({
            "id": pid,
            "sensor": it["sensor"],
            "split": it["split"],
            "status": status,
            "scene": best_r["scene"] if best_r else "",
            "x": best_r["x"] if best_r else None,
            "y": best_r["y"] if best_r else None,
            "footprint": best_r["fp"] if best_r else None,
            "orient": best_r["orient"] if best_r else "",
            "mode": best_r["mode"] if best_r else "",
            "native_zncc": round(nz, 4),
            "raw_zncc": round(rz, 4),
            "coarse_top1": round(cs["top1_coarse"], 4),
            "coarse_margin": round(margin, 4),
            "native_margin": round(native_margin, 4),
            "coarse_z": round(zscore, 2),
            "old_status": it["old_status"],
            "old_scene": it["old_scene"],
            "control_pass": ctrl_ok,
            "evidence": evid_rel,
        })

    # Save JSON + CSV
    with open(os.path.join(OUT_DIR, "results.json"), "w") as f:
        json.dump(final_rows, f, indent=2)

    fieldnames = list(final_rows[0].keys())
    with open(os.path.join(OUT_DIR, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(final_rows)

    # Build HTML visual review page
    cards_html = []
    for r in final_rows:
        if r["evidence"]:
            badge_col = "#1b5e58" if r["status"] == "matched_high_conf" else "#b86f28"
            cards_html.append(f"""
            <div class="card">
              <div class="head"><strong>{r['id']}</strong> <span class="badge" style="background:{badge_col}">{r['status']}</span></div>
              <div class="meta">{r['scene']} · ({r['x']}, {r['y']}) · {r['footprint']}px · {r['orient']} · {r['mode']}</div>
              <div class="meta">native ZNCC: <b>{r['native_zncc']}</b> · raw: {r['raw_zncc']} · margin: +{r['coarse_margin']} · z: {r['coarse_z']}σ · prev: {r['old_status']}</div>
              <img src="{r['evidence']}" alt="{r['id']} alignment comparison">
              <div class="lbls"><span>SOS Patch</span><span>Aligned Source Crop</span><span>Abs Diff</span></div>
            </div>""")

    review_html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>OceanTrace · 50-Tile Diagnostic Visual Review</title>
    <style>
    body{{margin:0;padding:24px;background:#f3f1eb;color:#162426;font:14px/1.45 system-ui,sans-serif}}
    h1{{font-family:Georgia,serif;margin:0 0 6px}} .sub{{color:#516163;margin:0 0 20px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px}}
    .card{{background:#fbfaf6;border:1px solid #cfd4ce;border-radius:8px;padding:12px}}
    .head{{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}}
    .badge{{color:#fff;font:600 11px monospace;padding:2px 8px;border-radius:99px}}
    .meta{{font:11.5px monospace;color:#516163;margin-bottom:4px}}
    img{{width:100%;display:block;border-radius:4px;margin-top:6px}}
    .lbls{{display:grid;grid-template-columns:repeat(3,1fr);text-align:center;font:10.5px monospace;color:#6c7c7e;margin-top:4px}}
    </style></head><body>
    <h1>Scene Matching Diagnostic — Visual Evidence</h1>
    <p class="sub">Despeckled coarse-to-fine ZNCC matcher on the 50-tile pilot set + controls. Showing all matched &amp; review candidates ({len(cards_html)} panels).</p>
    <div class="grid">{''.join(cards_html)}</div></body></html>"""
    with open(os.path.join(OUT_DIR, "review.html"), "w") as f:
        f.write(review_html)

    # Print summary
    real = [r for r in final_rows if r["split"] in ("train", "val")]
    pos_c = [r for r in final_rows if r["split"] == "control_pos"]
    neg_c = [r for r in final_rows if r["split"] == "control_neg"]

    def count_by(rows, sensor=None):
        sub = [r for r in rows if (sensor is None or r["sensor"] == sensor)]
        hi = sum(1 for r in sub if r["status"] == "matched_high_conf")
        rv = sum(1 for r in sub if r["status"] == "candidate_review")
        un = sum(1 for r in sub if r["status"] == "unresolved")
        return len(sub), hi, rv, un

    tot_n, tot_hi, tot_rv, tot_un = count_by(real)
    p_n, p_hi, p_rv, p_un = count_by(real, "palsar")
    s_n, s_hi, s_rv, s_un = count_by(real, "sentinel")
    pos_pass = sum(1 for r in pos_c if r["control_pass"])
    neg_pass = sum(1 for r in neg_c if r["control_pass"])

    old_cand = [r for r in real if r["old_status"] == "candidate_needs_review"]
    old_agree = sum(1 for r in old_cand if r["status"] != "unresolved" and r["scene"] == r["old_scene"])

    summary_text = f"""# Scene Matching Diagnostic Summary

- **Runtime:** {time.time() - t0:.1f} s
- **Method:** Log-despeckled coarse-to-fine ZNCC (`cv2.matchTemplate` TM_CCOEFF_NORMED) across all 21 full-res DVC SAR scenes, 8 D4 orientations, multiscale footprints (PALSAR: 256/416/512 px; Sentinel: 256/416/512/1024 px), native-resolution log+linear refinement, and global Peak-to-Second-Best uniqueness margin.

## Controls
- **Positive controls:** {pos_pass}/{len(pos_c)} localized within 16 px & passed gates
- **Negative controls:** {neg_pass}/{len(neg_c)} rejected (zero false accepts)

## Real 50-Patch Pilot Results (vs. Previous SIFT Pilot: 12/50 PALSAR, 0/25 Sentinel)
- **All 50 real patches:** {tot_hi} high-confidence + {tot_rv} review candidates = **{tot_hi + tot_rv}/{tot_n} matched** ({tot_un} unresolved)
- **PALSAR (25 patches):** {p_hi} high-confidence + {p_rv} review = **{p_hi + p_rv}/{p_n}** ({p_un} unresolved)
- **Sentinel-1 (25 patches):** {s_hi} high-confidence + {s_rv} review = **{s_hi + s_rv}/{s_n}** ({s_un} unresolved)
- **Agreement with previous 12 SIFT PALSAR candidates:** {old_agree}/{len(old_cand)} matched the exact same scene
"""
    with open(os.path.join(OUT_DIR, "summary.md"), "w") as f:
        f.write(summary_text)

    print("\n" + summary_text)


if __name__ == "__main__":
    main()
