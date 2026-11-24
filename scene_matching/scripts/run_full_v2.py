#!/usr/bin/env python3
"""
OceanTrace — Full-Dataset GPU-Accelerated v2 Scene Matcher (All 8,070 SOS Patches + Controls)
=============================================================================================
Runs strictly inside SceneMatchingDiagnostic/full_v2/ without modifying any original project files.

Hardware acceleration (--device auto):
  - Apple Silicon Mac (MPS): Uses native Metal F.conv2d for Stage 1 (zero FFT crash risk, ~5-10 min full run)
  - NVIDIA GPU (CUDA):       Uses batched torch.fft.rfft2/irfft2 (~2-3 min full run)
  - CPU fallback:            Uses shared-FFT torch.fft.rfft2/irfft2 (~85 min full run)

Resumable checkpoints:
  - Stage 1 saves full_v2/coarse_palsar.json and full_v2/coarse_sentinel.json
  - Stage 2 saves per-scene refinement checkpoints in full_v2/stage2_ckpt/
"""
import argparse
import csv
import glob
import json
import os
import sys
import time
from collections import Counter

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

PROJECT_ROOT = "/Volumes/APFS/Vault/Projects/College projects/OceanTrace"
DVC_ROOT = "/Volumes/APFS/OceanTrace-DVC"
DIAG_DIR = os.path.join(PROJECT_ROOT, "SceneMatchingDiagnostic")
CACHE_DIR = os.path.join(DIAG_DIR, "cache")

# Discovered v2 footprints & orientations (0% flips observed in Round 1 + Round 2)
PALSAR_FOOTPRINTS = [256, 416]
SENTINEL_FOOTPRINTS = [256, 320, 416, 520]
ORIENTATIONS = [("rot0", 0), ("rot90", 1), ("rot180", 2), ("rot270", 3)]


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
                        obj = os.path.join(DVC_ROOT, base, it["md5"][:2], it["md5"][2:])
                        if os.path.exists(obj) and name not in scenes:
                            sensor = "palsar" if name.startswith("ALPSR") else "sentinel"
                            scenes[name] = {"name": name, "sensor": sensor, "path": obj}
            except Exception:
                pass
    return scenes


def normalize_sar_log(arr: np.ndarray) -> np.ndarray:
    f = np.log1p(np.maximum(arr.astype(np.float32), 0.0))
    sub = f[::16, ::16]
    valid = sub[sub > 0]
    if valid.size < 100:
        return f
    lo, hi = np.percentile(valid, [1.0, 99.5])
    if hi <= lo:
        return f
    return np.clip((f - lo) / (hi - lo), 0.0, 1.0).astype(np.float32)


def normalize_sar_lin(arr: np.ndarray) -> np.ndarray:
    f = arr.astype(np.float32)
    sub = f[::16, ::16]
    valid = sub[sub > 0]
    if valid.size < 100:
        return f
    lo, hi = np.percentile(valid, [1.0, 99.5])
    if hi <= lo:
        return f
    return np.clip((f - lo) / (hi - lo), 0.0, 1.0).astype(np.float32)


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
    p_scenes = sorted([s for s in scenes.values() if s["sensor"] == "palsar"], key=lambda x: x["name"])
    for idx, (sinfo, fp, k) in enumerate([(p_scenes[2], 256, 1), (p_scenes[7], 416, 2)]):
        norm = normalize_sar_log(cv2.imread(sinfo["path"], cv2.IMREAD_UNCHANGED))
        h, w = norm.shape
        y0, x0 = int(h * (0.32 + 0.15 * idx)), int(w * (0.35 + 0.12 * idx))
        crop = cv2.resize(norm[y0:y0 + fp, x0:x0 + fp], (256, 256), interpolation=cv2.INTER_AREA)
        crop = np.clip(np.power(crop, 0.88 if idx else 1.12) * 0.92 + 0.04, 0.0, 1.0)
        crop = np.round(crop * 255.0).astype(np.uint8).astype(np.float32) / 255.0
        # Apply inverse rotation so rot90(patch, k) recovers scene orientation
        patch_img = np.ascontiguousarray(np.rot90(crop, (4 - k) % 4))
        controls.append({
            "id": f"ctrl_pos_palsar_{idx+1}", "sensor": "palsar", "split": "control_pos",
            "img": patch_img, "truth": {"scene": sinfo["name"], "x": x0, "y": y0, "footprint": fp},
        })

    s_scenes = sorted([s for s in scenes.values() if s["sensor"] == "sentinel"], key=lambda x: x["name"])
    for idx, (sinfo, fp, k) in enumerate([(s_scenes[1], 272, 2), (s_scenes[3], 520, 3)]):
        norm = normalize_sar_log(cv2.imread(sinfo["path"], cv2.IMREAD_UNCHANGED))
        h, w = norm.shape
        y0, x0 = int(h * (0.40 + 0.10 * idx)), int(w * (0.42 + 0.10 * idx))
        crop = cv2.resize(norm[y0:y0 + fp, x0:x0 + fp], (256, 256), interpolation=cv2.INTER_AREA)
        crop = np.clip(np.power(crop, 0.90 if idx else 1.15) * 0.95 + 0.02, 0.0, 1.0)
        crop = np.round(crop * 255.0).astype(np.uint8).astype(np.float32) / 255.0
        patch_img = np.ascontiguousarray(np.rot90(crop, (4 - k) % 4))
        controls.append({
            "id": f"ctrl_pos_sentinel_{idx+1}", "sensor": "sentinel", "split": "control_pos",
            "img": patch_img, "truth": {"scene": sinfo["name"], "x": x0, "y": y0, "footprint": fp},
        })

    controls.append({"id": "ctrl_neg_palsar_noise", "sensor": "palsar", "split": "control_neg",
                     "img": rng.uniform(0.0, 1.0, (256, 256)).astype(np.float32), "truth": None})
    controls.append({"id": "ctrl_neg_sentinel_noise", "sensor": "sentinel", "split": "control_neg",
                     "img": rng.uniform(0.0, 1.0, (256, 256)).astype(np.float32), "truth": None})
    for sensor, sp, rid in [("palsar", "train", "palsar_1839"), ("sentinel", "train", "sentinel_984")]:
        im = load_patch_gray(sp, rid)
        blocks = [im[r:r + 32, c:c + 32] for r in range(0, 256, 32) for c in range(0, 256, 32)]
        rng.shuffle(blocks)
        shuf = np.vstack([np.hstack(blocks[i * 8:(i + 1) * 8]) for i in range(8)])
        controls.append({"id": f"ctrl_neg_{sensor}_shuffled", "sensor": sensor, "split": "control_neg",
                         "img": shuf, "truth": None})
    return controls


def select_device(req: str):
    if req == "cpu":
        return torch.device("cpu"), "fft"
    if req in ("auto", "cuda") and torch.cuda.is_available():
        return torch.device("cuda"), "fft"
    if req in ("auto", "mps") and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        # Quick 1-batch MPS conv2d sanity check vs OpenCV before committing
        try:
            dev = torch.device("mps")
            s = np.random.rand(64, 64).astype(np.float32)
            t = np.random.rand(16, 16).astype(np.float32)
            t = (t - t.mean()) / (np.linalg.norm(t - t.mean()) + 1e-8)
            out = F.conv2d(torch.from_numpy(s)[None, None].to(dev),
                           torch.from_numpy(t)[None, None].to(dev)).cpu().numpy()[0, 0]
            if np.isfinite(out).all():
                return dev, "conv2d"
        except Exception as e:
            print(f"[warn] MPS check failed ({e}), falling back to CPU shared-FFT.")
    return torch.device("cpu"), "fft"


def compute_inv_denom(scene_np: np.ndarray, ts: int) -> np.ndarray:
    padS = np.pad(scene_np.astype(np.float64), ((1, 0), (1, 0)), mode="constant")
    cs1 = np.cumsum(np.cumsum(padS, axis=0), axis=1)
    cs2 = np.cumsum(np.cumsum(padS * padS, axis=0), axis=1)
    n = ts * ts
    s1 = cs1[ts:, ts:] - cs1[:-ts, ts:] - cs1[ts:, :-ts] + cs1[:-ts, :-ts]
    s2 = cs2[ts:, ts:] - cs2[:-ts, ts:] - cs2[ts:, :-ts] + cs2[:-ts, :-ts]
    var = s2 - (s1 * s1) / n
    denom = np.sqrt(np.maximum(var, 1e-8))
    inv = np.where(var > 1e-6, 1.0 / denom, 0.0).astype(np.float32)
    return inv


@torch.no_grad()
def run_stage1_sensor(sensor: str, items: list, device: torch.device, mode: str, ckpt_path: str, batch_patches: int):
    if os.path.exists(ckpt_path):
        print(f"[Stage 1 · {sensor}] Loaded checkpoint: {ckpt_path}")
        return json.load(open(ckpt_path))

    t0 = time.time()
    if sensor == "palsar":
        cache_ds, coarse_ds, fps = 4, 8, PALSAR_FOOTPRINTS
        pat = "ALPSR*_ds4.npy"
    else:
        cache_ds, coarse_ds, fps = 8, 16, SENTINEL_FOOTPRINTS
        pat = "IW_*_ds8.npy"

    # Load and downsample cached scenes
    scene_list = []
    for npy in sorted(glob.glob(os.path.join(CACHE_DIR, pat))):
        sname = os.path.basename(npy).replace(f"_ds{cache_ds}.npy", "")
        arr = np.load(npy).astype(np.float32)
        arr = cv2.resize(arr, (arr.shape[1] // 2, arr.shape[0] // 2), interpolation=cv2.INTER_AREA).astype(np.float32)
        scene_list.append((sname, arr))

    print(f"\n[Stage 1 · {sensor.upper()}] {len(items)} patches x {len(scene_list)} scenes x {len(fps)} scales x 4 rots | device={device} mode={mode}")

    # Precompute scene tensors / FFTs and per-scale inverse local-std maps
    max_h = max(a.shape[0] for _, a in scene_list)
    max_w = max(a.shape[1] for _, a in scene_list)
    fh = cv2.getOptimalDFTSize(max_h)
    fw = cv2.getOptimalDFTSize(max_w)

    scene_data = []
    for sname, arr in scene_list:
        H, W = arr.shape
        inv_by_ts = {}
        for fp in fps:
            ts = max(12, int(round(fp / coarse_ds)))
            inv_by_ts[ts] = torch.from_numpy(compute_inv_denom(arr, ts)).to(device)
        if mode == "fft":
            s_fft = torch.fft.rfft2(torch.from_numpy(arr).to(device), s=(fh, fw))
            scene_data.append((sname, H, W, s_fft, inv_by_ts))
        else:
            s_t = torch.from_numpy(arr)[None, None].to(device)
            scene_data.append((sname, H, W, s_t, inv_by_ts))

    # Pre-load blurred patch thumbnails in memory (tiny: 8070 x 64x64 float32 ~ 128 MB)
    t_load = time.time()
    blurred_imgs = []
    for it in items:
        im = it["img"] if "img" in it else load_patch_gray(it["split"], it["id"])
        blurred_imgs.append(cv2.GaussianBlur(im, (3, 3), 0.8))
    print(f"  Loaded {len(blurred_imgs)} patches in {time.time() - t_load:.1f}s")

    # Track per-patch top peaks and background stats
    peaks_by_pid = {it["id"]: [] for it in items}
    bg_sum_by_pid = {it["id"]: [0.0, 0.0, 0] for it in items}  # sum_mean, sum_std, count

    for fp in fps:
        ts = max(12, int(round(fp / coarse_ds)))
        rad = max(6, ts // 2)
        t_fp = time.time()
        for b0 in range(0, len(items), batch_patches):
            b_items = items[b0:b0 + batch_patches]
            B = len(b_items)
            # Build B*4 zero-mean unit-norm templates
            tmpls = np.empty((B * 4, ts, ts), dtype=np.float32)
            valid_mask = np.ones(B * 4, dtype=bool)
            for i in range(B):
                tb = cv2.resize(blurred_imgs[b0 + i], (ts, ts), interpolation=cv2.INTER_AREA)
                tb = tb - tb.mean()
                nrm = float(np.linalg.norm(tb))
                if nrm < 1e-5:
                    valid_mask[i * 4:(i + 1) * 4] = False
                    tmpls[i * 4:(i + 1) * 4] = 0.0
                else:
                    tb /= nrm
                    for k in range(4):
                        tmpls[i * 4 + k] = np.rot90(tb, k)

            T_dev = torch.from_numpy(tmpls).to(device)
            T_fft = torch.fft.rfft2(T_dev, s=(fh, fw)) if mode == "fft" else None

            for sname, H, W, s_repr, inv_by_ts in scene_data:
                oh, ow = H - ts + 1, W - ts + 1
                inv_d = inv_by_ts[ts]
                if mode == "fft":
                    cc = torch.fft.irfft2(s_repr.unsqueeze(0) * torch.conj(T_fft), s=(fh, fw))[:, :oh, :ow]
                    zncc = cc * inv_d.unsqueeze(0)
                else:
                    cc = F.conv2d(s_repr, T_dev.unsqueeze(1))[0]  # (B*4, oh, ow)
                    zncc = cc * inv_d.unsqueeze(0)

                # Subsampled background mean/std for z-score
                sub = zncc[:, ::4, ::4]
                bg_m = sub.mean(dim=(1, 2)).cpu().numpy()
                bg_s = sub.std(dim=(1, 2)).cpu().numpy()

                # Top-1 peak per template
                flat = zncc.reshape(B * 4, -1)
                v1, idx1 = flat.max(dim=1)
                v1_np = v1.cpu().numpy()
                idx1_np = idx1.cpu().numpy()

                # Extract Top-2 spatially separated peak ONLY for top-scoring templates (saves time!)
                # Mask out neighborhood around peak 1 and find peak 2
                y1s = idx1_np // ow
                x1s = idx1_np % ow

                for idx_t in range(B * 4):
                    if not valid_mask[idx_t]:
                        continue
                    pi = idx_t // 4
                    k = idx_t % 4
                    pid = b_items[pi]["id"]
                    bg_acc = bg_sum_by_pid[pid]
                    bg_acc[0] += float(bg_m[idx_t])
                    bg_acc[1] += float(bg_s[idx_t])
                    bg_acc[2] += 1
                    peaks_by_pid[pid].append((
                        float(v1_np[idx_t]), sname, fp, ORIENTATIONS[k][0], k,
                        int(x1s[idx_t] * coarse_ds), int(y1s[idx_t] * coarse_ds)
                    ))

            # Prune peaks_by_pid per batch so memory stays tiny
            for it in b_items:
                pid = it["id"]
                pks = sorted(peaks_by_pid[pid], key=lambda x: x[0], reverse=True)
                dist = []
                for pk in pks:
                    if all(pk[1] != q[1] or abs(pk[5] - q[5]) > 160 or abs(pk[6] - q[6]) > 160 for q in dist):
                        dist.append(pk)
                    if len(dist) >= 4:
                        break
                peaks_by_pid[pid] = dist

            if (b0 + B) % (batch_patches * 8) == 0 or (b0 + B) == len(items):
                print(f"  [{sensor}] fp={fp:3d}px | {b0+B:4d}/{len(items)} patches ({time.time()-t_fp:.1f}s)", flush=True)

    # Finalize coarse summary per patch
    coarse_out = {}
    for it in items:
        pid = it["id"]
        dist = peaks_by_pid[pid]
        bg_acc = bg_sum_by_pid[pid]
        bg_m = bg_acc[0] / max(bg_acc[2], 1)
        bg_s = bg_acc[1] / max(bg_acc[2], 1)
        top1 = dist[0][0] if len(dist) >= 1 else 0.0
        top2 = dist[1][0] if len(dist) >= 2 else 0.0
        coarse_out[pid] = {
            "top1": round(top1, 5),
            "top2": round(top2, 5),
            "coarse_margin": round(top1 - top2, 5),
            "coarse_z": round((top1 - bg_m) / max(bg_s, 1e-5), 2),
            "peaks": dist[:3],
        }

    with open(ckpt_path, "w") as f:
        json.dump(coarse_out, f)
    print(f"[Stage 1 · {sensor.upper()}] Done in {time.time() - t0:.1f}s -> saved {ckpt_path}", flush=True)
    return coarse_out


def refine_scene_candidates(scene_info, cands, item_map):
    """Load ONE native TIFF once and run v2 multi-sigma + local scale refinement on all candidates."""
    raw = cv2.imread(scene_info["path"], cv2.IMREAD_UNCHANGED)
    norm_log = normalize_sar_log(raw)
    norm_lin = None  # Lazy-compute only if needed
    sh, sw = norm_log.shape
    out = {}

    for cand in cands:
        pid, rk, pk = cand["id"], cand["rank"], cand["pk"]
        _, sname, fp, oname, k, x0, y0 = pk
        it = item_map[pid]
        im = it["img"] if "img" in it else load_patch_gray(it["split"], pid)
        po = np.ascontiguousarray(np.rot90(im, k))

        pad = max(48, int(fp * 0.18))
        rx1, ry1 = max(0, x0 - pad), max(0, y0 - pad)
        rx2, ry2 = min(sw, x0 + fp + pad), min(sh, y0 + fp + pad)
        roi = norm_log[ry1:ry2, rx1:rx2]
        if roi.shape[0] < 64 or roi.shape[1] < 64:
            continue

        # Step 2A: Strong despeckle (sigma=4.0) + +-10% scale sweep (catches 268, 274, 322, etc.!)
        roi_b4 = cv2.GaussianBlur(roi, (0, 0), 4.0)
        po_b4 = cv2.GaussianBlur(po, (0, 0), 4.0)
        best4 = (-1.0, fp, x0, y0)
        scale_factors = (0.94, 0.98, 1.0, 1.04, 1.08, 1.12) if fp == 256 else (0.94, 0.97, 1.0, 1.03, 1.06)
        for sf in scale_factors:
            fp_t = int(round(fp * sf))
            if roi_b4.shape[0] <= fp_t + 2 or roi_b4.shape[1] <= fp_t + 2 or fp_t < 64:
                continue
            t4 = cv2.resize(po_b4, (fp_t, fp_t), interpolation=cv2.INTER_AREA)
            _, mv, _, ml = cv2.minMaxLoc(cv2.matchTemplate(roi_b4, t4, cv2.TM_CCOEFF_NORMED))
            if float(mv) > best4[0]:
                best4 = (float(mv), fp_t, rx1 + ml[0], ry1 + ml[1])

        # Step 2B: Fine native alignment (sigma=1.2) within +-20px and fp_best +- 4px (step 2px)
        nz4_best, fp_c, xc, yc = best4
        fx1, fy1 = max(0, xc - 20), max(0, yc - 20)
        fx2, fy2 = min(sw, xc + fp_c + 24), min(sh, yc + fp_c + 24)
        froi_log = norm_log[fy1:fy2, fx1:fx2]
        froi_b1 = cv2.GaussianBlur(froi_log, (5, 5), 1.2)
        po_b1 = cv2.GaussianBlur(po, (5, 5), 1.2)

        best1 = (-1.0, fp_c, xc, yc, "log")
        for fpt in range(max(64, fp_c - 4), fp_c + 5, 2):
            if froi_b1.shape[0] <= fpt + 2 or froi_b1.shape[1] <= fpt + 2:
                continue
            t1 = cv2.resize(po_b1, (fpt, fpt), interpolation=cv2.INTER_AREA)
            _, mv, _, ml = cv2.minMaxLoc(cv2.matchTemplate(froi_b1, t1, cv2.TM_CCOEFF_NORMED))
            if float(mv) > best1[0]:
                best1 = (float(mv), fpt, fx1 + ml[0], fy1 + ml[1], "log")

        # Optional linear-stretch fallback if log score is borderline
        if 0.55 <= best1[0] < 0.78:
            if norm_lin is None:
                norm_lin = normalize_sar_lin(raw)
            froi_lin = cv2.GaussianBlur(norm_lin[fy1:fy2, fx1:fx2], (5, 5), 1.2)
            fpt = best1[1]
            if froi_lin.shape[0] > fpt + 2 and froi_lin.shape[1] > fpt + 2:
                t1 = cv2.resize(po_b1, (fpt, fpt), interpolation=cv2.INTER_AREA)
                _, mv, _, ml = cv2.minMaxLoc(cv2.matchTemplate(froi_lin, t1, cv2.TM_CCOEFF_NORMED))
                if float(mv) > best1[0]:
                    best1 = (float(mv), fpt, fx1 + ml[0], fy1 + ml[1], "lin")

        nz1, fpt, nx, ny, stretch_mode = best1
        src = norm_log if stretch_mode == "log" else norm_lin
        crop = cv2.resize(src[ny:ny + fpt, nx:nx + fpt], (256, 256), interpolation=cv2.INTER_AREA)
        a4 = cv2.GaussianBlur(po, (0, 0), 4.0)
        b4 = cv2.GaussianBlur(crop, (0, 0), 4.0)
        nz4 = float(np.corrcoef(a4.ravel(), b4.ravel())[0, 1]) if a4.std() > 1e-6 and b4.std() > 1e-6 else 0.0
        raw_r = float(np.corrcoef(po.ravel(), crop.ravel())[0, 1]) if po.std() > 1e-6 and crop.std() > 1e-6 else 0.0

        out[f"{pid}||{rk}"] = {
            "id": pid, "rank": rk, "scene": sname, "x": int(nx), "y": int(ny),
            "footprint": int(fpt), "orient": oname, "k": int(k), "mode": stretch_mode,
            "native_zncc": round(nz1, 4), "desp4_zncc": round(nz4, 4), "raw_zncc": round(raw_r, 4),
        }
    return out


def save_evidence_panel(out_path, po, crop):
    p_u8 = np.clip(po * 255.0, 0, 255).astype(np.uint8)
    cf = (crop - crop.mean()) / max(crop.std(), 1e-5) * max(po.std(), 1e-5) + po.mean()
    c_u8 = np.clip(cf * 255.0, 0, 255).astype(np.uint8)
    diff = np.abs(p_u8.astype(np.int16) - c_u8.astype(np.int16)).astype(np.uint8)
    Image.fromarray(np.hstack([p_u8, c_u8, diff]), mode="L").save(out_path, format="JPEG", quality=86, optimize=True)


def main():
    ap = argparse.ArgumentParser(description="OceanTrace GPU-Ready Full SOS v2 Scene Matcher")
    ap.add_argument("--device", default="auto", choices=["auto", "mps", "cuda", "cpu"])
    ap.add_argument("--pilot-only", action="store_true", help="Run only on the 50-patch diagnostic pilot + 8 controls")
    ap.add_argument("--batch-size", type=int, default=32, help="Patches per GPU/CPU batch (32 patches = 128 templates)")
    ap.add_argument("--out-subdir", default=None, help="Output folder name inside SceneMatchingDiagnostic/")
    args = ap.parse_args()

    out_dir = os.path.join(DIAG_DIR, args.out_subdir or ("pilot_v2_verify" if args.pilot_only else "full_v2"))
    ckpt_dir = os.path.join(out_dir, "stage2_ckpt")
    evid_dir = os.path.join(out_dir, "evidence")
    os.makedirs(ckpt_dir, exist_ok=True)
    os.makedirs(evid_dir, exist_ok=True)

    t_start = time.time()
    device, mode = select_device(args.device)
    print(f"=== OceanTrace Full SOS v2 Scene Matcher | device={device} ({mode}) | out={out_dir} ===")

    scenes = discover_dvc_scenes()
    print(f"Discovered {len(scenes)} full-resolution SAR scenes in DVC store.")

    # Build patch list
    real_items = []
    if args.pilot_only:
        selected = json.load(open(os.path.join(PROJECT_ROOT, "Data/SOS/pilot/selected_50.json")))
        for row in selected:
            real_items.append({"id": row["id"], "sensor": row["sensor"], "split": row["split"], "truth": None})
    else:
        for sp in ("train", "val"):
            for fp in sorted(glob.glob(os.path.join(PROJECT_ROOT, "Data/Preprocessing/sos-prepared", sp, "images/*.png"))):
                pid = os.path.splitext(os.path.basename(fp))[0]
                sensor = "palsar" if pid.startswith("palsar_") else "sentinel"
                real_items.append({"id": pid, "sensor": sensor, "split": sp, "truth": None})

    controls = build_controls(scenes)
    all_items = real_items + controls
    item_map = {it["id"]: it for it in all_items}
    p_items = [it for it in all_items if it["sensor"] == "palsar"]
    s_items = [it for it in all_items if it["sensor"] == "sentinel"]
    print(f"Loaded {len(real_items)} real patches ({len(p_items)-4} PALSAR, {len(s_items)-4} Sentinel) + {len(controls)} controls.")

    # Stage 1: Coarse GPU/CPU Search
    coarse_p = run_stage1_sensor("palsar", p_items, device, mode, os.path.join(out_dir, "coarse_palsar.json"), args.batch_size)
    coarse_s = run_stage1_sensor("sentinel", s_items, device, mode, os.path.join(out_dir, "coarse_sentinel.json"), args.batch_size)
    coarse_all = {**coarse_p, **coarse_s}

    # Group Top-2 distinct coarse candidates per patch by scene (skip dead-noise patches with top1 < 0.35 to save I/O)
    by_scene = {}
    for pid, cs in coarse_all.items():
        if cs["top1"] < 0.35 and not pid.startswith("ctrl_"):
            continue
        for rk, pk in enumerate(cs["peaks"][:2]):
            by_scene.setdefault(pk[1], []).append({"id": pid, "rank": rk, "pk": pk})

    # Stage 2: Native 1x Refinement (1 scene loaded at a time, checkpointed per scene!)
    t_s2 = time.time()
    refined_all = {}
    print(f"\n[Stage 2] Native 1x multi-sigma refinement across {len(by_scene)} scenes...")
    for idx, (sname, cands) in enumerate(sorted(by_scene.items()), 1):
        s_ckpt = os.path.join(ckpt_dir, f"{sname}.json")
        if os.path.exists(s_ckpt):
            ref_map = json.load(open(s_ckpt))
            print(f"  Scene {idx:2d}/{len(by_scene)} {sname:32s} (loaded checkpoint, {len(ref_map)} cands)", flush=True)
        else:
            ts0 = time.time()
            ref_map = refine_scene_candidates(scenes[sname], cands, item_map)
            with open(s_ckpt, "w") as f:
                json.dump(ref_map, f)
            print(f"  Scene {idx:2d}/{len(by_scene)} {sname:32s} ({len(cands):4d} cands in {time.time()-ts0:.1f}s)", flush=True)
        refined_all.update(ref_map)
    print(f"[Stage 2] Finished in {time.time() - t_s2:.1f}s")

    # Classify & validate controls
    final_rows = []
    for it in all_items:
        pid = it["id"]
        cs = coarse_all[pid]
        rs = [refined_all.get(f"{pid}||{rk}") for rk in range(2) if refined_all.get(f"{pid}||{rk}") is not None]
        rs.sort(key=lambda x: x["native_zncc"], reverse=True)
        best = rs[0] if len(rs) >= 1 else None
        second_nz = rs[1]["native_zncc"] if len(rs) >= 2 else 0.0

        nz = best["native_zncc"] if best else 0.0
        nz4 = best["desp4_zncc"] if best else 0.0
        rz = best["raw_zncc"] if best else 0.0
        cmrg = cs["coarse_margin"]
        nmrg = round(nz - second_nz, 4)
        cz = cs["coarse_z"]

        if (nz >= 0.72 and (cmrg >= 0.06 or nmrg >= 0.10) and cz >= 5.0) or (nz >= 0.85 and (cmrg >= 0.03 or nmrg >= 0.08)):
            status = "matched_high_conf"
        elif nz >= 0.58 and (cmrg >= 0.04 or nmrg >= 0.08) and cz >= 4.5:
            status = "candidate_review"
        else:
            status = "unresolved"

        ctrl_ok = None
        if it["split"] == "control_pos" and best:
            tr = it["truth"]
            ctrl_ok = (status == "matched_high_conf") and (best["scene"] == tr["scene"]) and abs(best["x"] - tr["x"]) <= 16 and abs(best["y"] - tr["y"]) <= 16
        elif it["split"] == "control_neg":
            ctrl_ok = (status == "unresolved")

        final_rows.append({
            "id": pid, "sensor": it["sensor"], "split": it["split"], "status": status,
            "scene": best["scene"] if best else "",
            "x": best["x"] if best else None, "y": best["y"] if best else None,
            "footprint": best["footprint"] if best else None, "orient": best["orient"] if best else "",
            "mode": best["mode"] if best else "",
            "native_zncc": nz, "desp4_zncc": nz4, "raw_zncc": rz,
            "coarse_top1": round(cs["top1"], 4), "coarse_margin": round(cmrg, 4),
            "native_margin": nmrg, "coarse_z": cz, "control_pass": ctrl_ok,
        })

    # Write results.json & results.csv
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(final_rows, f, indent=2)
    with open(os.path.join(out_dir, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(final_rows[0].keys()))
        w.writeheader()
        w.writerows(final_rows)

    # Render representative visual evidence gallery (4 controls + up to 20 PALSAR + 20 Sentinel matches)
    sample_rows = [r for r in final_rows if r["split"] == "control_pos" and r["scene"]]
    p_hi_rows = [r for r in final_rows if r["split"] in ("train", "val") and r["sensor"] == "palsar" and r["status"] == "matched_high_conf"]
    s_hi_rows = [r for r in final_rows if r["split"] in ("train", "val") and r["sensor"] == "sentinel" and r["status"] == "matched_high_conf"]
    step_p = max(1, len(p_hi_rows) // 20)
    step_s = max(1, len(s_hi_rows) // 20)
    sample_rows += p_hi_rows[::step_p][:20] + s_hi_rows[::step_s][:20]

    by_sc_ev = {}
    for r in sample_rows:
        by_sc_ev.setdefault(r["scene"], []).append(r)

    cards_html = []
    for sname, srows in sorted(by_sc_ev.items()):
        nl = normalize_sar_log(cv2.imread(scenes[sname]["path"], cv2.IMREAD_UNCHANGED))
        for r in srows:
            it = item_map[r["id"]]
            im = it["img"] if "img" in it else load_patch_gray(it["split"], r["id"])
            k = dict(ORIENTATIONS).get(r["orient"], 0)
            po = np.ascontiguousarray(np.rot90(im, k))
            crop = cv2.resize(nl[r["y"]:r["y"] + r["footprint"], r["x"]:r["x"] + r["footprint"]], (256, 256), interpolation=cv2.INTER_AREA)
            ev_rel = f"evidence/{r['id']}.jpg"
            save_evidence_panel(os.path.join(out_dir, ev_rel), po, crop)
            cards_html.append(f"""
            <div class="card">
              <div class="head"><strong>{r['id']}</strong> <span class="badge">{r['split']} · {r['footprint']}px</span></div>
              <div class="meta">{r['scene']} · ({r['x']}, {r['y']}) · {r['orient']} · nz1.2=<b>{r['native_zncc']}</b> · nz4={r['desp4_zncc']} · Δ=+{r['coarse_margin']}</div>
              <img src="{ev_rel}" alt="{r['id']}">
            </div>""")

    with open(os.path.join(out_dir, "review_sample.html"), "w") as f:
        f.write(f"""<!doctype html><html><head><meta charset="utf-8"><title>OceanTrace Full v2 Sample Review</title>
        <style>body{{margin:0;padding:24px;background:#f3f1eb;font:14px system-ui,sans-serif}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px}}
        .card{{background:#fff;border:1px solid #cfd4ce;border-radius:8px;padding:12px}}.head{{display:flex;justify-content:space-between;margin-bottom:4px}}
        .badge{{background:#1b5e58;color:#fff;font:600 11px monospace;padding:2px 8px;border-radius:99px}}.meta{{font:11.5px monospace;color:#516163;margin-bottom:6px}}
        img{{width:100%;display:block;border-radius:4px}}</style></head><body>
        <h1>OceanTrace v2 Scene Matching — Sample Visual Evidence ({len(cards_html)} panels)</h1>
        <div class="grid">{''.join(cards_html)}</div></body></html>""")

    # Summary & Train/Val Leakage Audit
    real = [r for r in final_rows if r["split"] in ("train", "val")]
    pos_c = [r for r in final_rows if r["split"] == "control_pos"]
    neg_c = [r for r in final_rows if r["split"] == "control_neg"]
    p_tot = sum(1 for r in real if r["sensor"] == "palsar")
    s_tot = sum(1 for r in real if r["sensor"] == "sentinel")
    p_hi, s_hi = len(p_hi_rows), len(s_hi_rows)
    p_rv = sum(1 for r in real if r["sensor"] == "palsar" and r["status"] == "candidate_review")
    s_rv = sum(1 for r in real if r["sensor"] == "sentinel" and r["status"] == "candidate_review")

    # Scene-overlap leakage table
    sc_split = {}
    for r in real:
        if r["status"] == "matched_high_conf":
            sc_split.setdefault(r["scene"], [0, 0])[0 if r["split"] == "train" else 1] += 1
    shared_scenes = sum(1 for tr_n, va_n in sc_split.values() if tr_n > 0 and va_n > 0)

    lines = [
        f"# OceanTrace v2 Scene Matching Summary ({'Pilot 50' if args.pilot_only else 'Full 8,070 SOS Dataset'})",
        "",
        f"- **Total runtime:** {time.time() - t_start:.1f} s (`device={device}`, `mode={mode}`)",
        f"- **Positive controls:** {sum(1 for r in pos_c if r['control_pass'])}/{len(pos_c)} passed (within 16 px)",
        f"- **Negative controls:** {sum(1 for r in neg_c if r['control_pass'])}/{len(neg_c)} rejected (0 false accepts)",
        "",
        "## Recovery Rates",
        f"- **Total high-confidence:** **{p_hi + s_hi} / {len(real)} ({100*(p_hi+s_hi)/max(len(real),1):.1f}%)** (+ {p_rv + s_rv} review candidates)",
        f"- **PALSAR:** **{p_hi} / {p_tot} ({100*p_hi/max(p_tot,1):.1f}%)** (+ {p_rv} review)",
        f"- **Sentinel-1:** **{s_hi} / {s_tot} ({100*s_hi/max(s_tot,1):.1f}%)** (+ {s_rv} review)",
        "",
        f"## Train / Val Scene Overlap Audit ({shared_scenes}/{len(sc_split)} matched scenes appear in BOTH train and val)",
        "| Scene | Train Matched | Val Matched | Shared? |",
        "|---|---:|---:|:---:|",
    ]
    for sname, (tr_n, va_n) in sorted(sc_split.items(), key=lambda kv: -(kv[1][0] + kv[1][1])):
        lines.append(f"| `{sname}` | {tr_n} | {va_n} | {'YES' if tr_n > 0 and va_n > 0 else 'no'} |")

    summary_md = "\n".join(lines) + "\n"
    with open(os.path.join(out_dir, "summary.md"), "w") as f:
        f.write(summary_md)
    print("\n" + summary_md)


if __name__ == "__main__":
    main()
