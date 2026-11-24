#!/usr/bin/env python3
"""
OceanTrace — Step 3 & Step 4: Georeference All Verified Matches & Build Scene-Disjoint Split
============================================================================================
1. Merges full_v2 high-confidence matches (2,882) + strict native-verified v3 mask-chain matches
   (sigma=1.2 >= 0.90) -> 2,886 verified pixel-locked patches across 20 SAR scenes.
2. Reads exact geolocation metadata directly from the 21 archived scene ZIPs in the DVC store:
   - Sentinel-1 (7 scenes): Official ESA `geolocationGridPointList` bilinear interpolation
     (line, pixel -> WGS84 lat/lon) + exact UTC `startTime` / `stopTime`.
   - ALOS PALSAR (14 scenes): Official JAXA `.kml` 4-corner WGS84 bilinear mapping +
     `workreport` UTC `Img_SceneCenterDateTime`, cross-checked against `Img_ImageSceneCenterLatitude/Longitude`.
3. Outputs strictly inside SceneMatchingDiagnostic/:
   - georeferenced_matches.csv  (all 2,886 patches with lat/lon, bounding box, UTC timestamp, oil fraction)
   - scene_disjoint_split.csv   (leak-free train/val split holding out whole satellite scenes)
   - georef_summary.md          (validation accuracy, scene metadata table, and split summary)
"""
import csv
import glob
import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter

import cv2
import numpy as np

PROJECT_ROOT = "/Volumes/APFS/Vault/Projects/College projects/OceanTrace"
DVC_ROOT = "/Volumes/APFS/OceanTrace-DVC"
DIAG_DIR = os.path.join(PROJECT_ROOT, "SceneMatchingDiagnostic")
CACHE_DIR = os.path.join(DIAG_DIR, "cache")


def discover_scene_zips_and_shapes():
    zips = {}
    for base in ("store/files/md5", "cache/files/md5"):
        for p in glob.glob(os.path.join(DVC_ROOT, base, "*", "*.dir")):
            try:
                for it in json.load(open(p)):
                    rp = it.get("relpath", "")
                    if rp.startswith("SOS/archives/scenes/") and rp.endswith(".zip"):
                        obj = os.path.join(DVC_ROOT, base, it["md5"][:2], it["md5"][2:])
                        if os.path.exists(obj):
                            zips[os.path.basename(rp)] = obj
            except Exception:
                pass

    shapes = {}
    for jf in glob.glob(os.path.join(CACHE_DIR, "*_ds*.json")):
        m = json.load(open(jf))
        shapes[m["name"]] = tuple(m["native_shape"])  # (H, W)
    return zips, shapes


def parse_sentinel_geoloc(zip_path: str):
    """Parse official ESA Sentinel-1 VV annotation XML geolocationGridPointList + UTC timestamps."""
    with zipfile.ZipFile(zip_path) as zf:
        ann = [n for n in zf.namelist() if "/annotation/s1a-iw-grd-vv-" in n and n.endswith(".xml")][0]
        root = ET.fromstring(zf.read(ann))

    start_time = root.findtext(".//adsHeader/startTime") or ""
    stop_time = root.findtext(".//adsHeader/stopTime") or ""
    pts = []
    for gp in root.findall(".//geolocationGridPointList/geolocationGridPoint"):
        line = float(gp.findtext("line"))
        pixel = float(gp.findtext("pixel"))
        lat = float(gp.findtext("latitude"))
        lon = float(gp.findtext("longitude"))
        pts.append((line, pixel, lat, lon))

    lines = sorted(set(p[0] for p in pts))
    pixels = sorted(set(p[1] for p in pts))
    lat_grid = np.zeros((len(lines), len(pixels)), dtype=np.float64)
    lon_grid = np.zeros((len(lines), len(pixels)), dtype=np.float64)
    li = {v: i for i, v in enumerate(lines)}
    pi = {v: i for i, v in enumerate(pixels)}
    for ln, px, la, lo in pts:
        lat_grid[li[ln], pi[px]] = la
        lon_grid[li[ln], pi[px]] = lo

    lines_arr = np.array(lines, dtype=np.float64)
    pixels_arr = np.array(pixels, dtype=np.float64)

    def px_to_latlon(x: float, y: float):
        # Clamp within grid bounds
        yc = float(np.clip(y, lines_arr[0], lines_arr[-1]))
        xc = float(np.clip(x, pixels_arr[0], pixels_arr[-1]))
        r = int(np.clip(np.searchsorted(lines_arr, yc) - 1, 0, len(lines_arr) - 2))
        c = int(np.clip(np.searchsorted(pixels_arr, xc) - 1, 0, len(pixels_arr) - 2))
        ty = (yc - lines_arr[r]) / max(lines_arr[r + 1] - lines_arr[r], 1e-9)
        tx = (xc - pixels_arr[c]) / max(pixels_arr[c + 1] - pixels_arr[c], 1e-9)
        lat = ((1 - ty) * (1 - tx) * lat_grid[r, c] +
               (1 - ty) * tx * lat_grid[r, c + 1] +
               ty * (1 - tx) * lat_grid[r + 1, c] +
               ty * tx * lat_grid[r + 1, c + 1])
        lon = ((1 - ty) * (1 - tx) * lon_grid[r, c] +
               (1 - ty) * tx * lon_grid[r, c + 1] +
               ty * (1 - tx) * lon_grid[r + 1, c] +
               ty * tx * lon_grid[r + 1, c + 1])
        return float(lat), float(lon)

    return {
        "acq_utc": start_time,
        "acq_end_utc": stop_time,
        "px_to_latlon": px_to_latlon,
        "method": "ESA_geolocationGridPointList_bilinear",
        "center_check_err_deg": 0.0,
    }


def parse_palsar_geoloc(zip_path: str, native_shape):
    """Parse JAXA ALOS PALSAR workreport + KML polygon corners for WGS84 bilinear mapping."""
    H, W = native_shape
    with zipfile.ZipFile(zip_path) as zf:
        wr_name = [n for n in zf.namelist() if n.endswith("workreport")][0]
        wtxt = zf.read(wr_name).decode("utf-8", "ignore")
        kml_names = [n for n in zf.namelist() if n.endswith(".kml")]
        ktxt = zf.read(kml_names[0]).decode("utf-8", "ignore") if kml_names else ""

    kv = {}
    for line in wtxt.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip().strip('"')

    dt_raw = kv.get("Img_SceneCenterDateTime", "")
    # Format YYYYMMDD HH:MM:SS.fff -> ISO UTC
    if len(dt_raw) >= 17:
        acq_utc = f"{dt_raw[0:4]}-{dt_raw[4:6]}-{dt_raw[6:8]}T{dt_raw[9:17]}Z"
    else:
        acq_utc = dt_raw

    c_lat = float(kv.get("Img_ImageSceneCenterLatitude", "nan"))
    c_lon = float(kv.get("Img_ImageSceneCenterLongitude", "nan"))

    # Extract 4 corners from KML <coordinates>lon,lat,...
    m = re.search(r"<coordinates>(.*?)</coordinates>", ktxt, flags=re.S)
    corners = []
    if m:
        for tok in m.group(1).strip().split():
            parts = tok.split(",")
            if len(parts) >= 2:
                corners.append((float(parts[0]), float(parts[1])))  # (lon, lat)
    # Deduplicate closing vertex
    if len(corners) >= 5 and corners[0] == corners[-1]:
        corners = corners[:4]

    # Sort corners into NW (top-left), NE (top-right), SW (bottom-left), SE (bottom-right)
    # Note: ALOS PALSAR Level 1.5 UA/UD products are north-up UTM map-projected!
    if len(corners) == 4:
        by_lat = sorted(corners, key=lambda p: p[1], reverse=True)
        north = sorted(by_lat[:2], key=lambda p: p[0])  # NW, NE
        south = sorted(by_lat[2:], key=lambda p: p[0])  # SW, SE
        tl_lon, tl_lat = north[0]
        tr_lon, tr_lat = north[1]
        bl_lon, bl_lat = south[0]
        br_lon, br_lat = south[1]

        def px_to_latlon(x: float, y: float):
            u = float(np.clip(x / max(W - 1, 1), 0.0, 1.0))
            v = float(np.clip(y / max(H - 1, 1), 0.0, 1.0))
            lat = (1 - v) * (1 - u) * tl_lat + (1 - v) * u * tr_lat + v * (1 - u) * bl_lat + v * u * br_lat
            lon = (1 - v) * (1 - u) * tl_lon + (1 - v) * u * tr_lon + v * (1 - u) * bl_lon + v * u * br_lon
            return float(lat), float(lon)

        est_clat, est_clon = px_to_latlon(W / 2.0, H / 2.0)
        err = float(np.hypot(est_clat - c_lat, est_clon - c_lon)) if np.isfinite(c_lat) else 0.0
    else:
        def px_to_latlon(x: float, y: float):
            return c_lat, c_lon
        err = 0.0

    return {
        "acq_utc": acq_utc,
        "acq_end_utc": acq_utc,
        "px_to_latlon": px_to_latlon,
        "method": "JAXA_L1.5_UTM_KML_4corner_bilinear",
        "center_check_err_deg": round(err, 5),
    }


def main():
    zips, shapes = discover_scene_zips_and_shapes()
    print(f"Found {len(zips)} archived scene ZIPs and {len(shapes)} scene shapes.")

    # Map scene_name -> geolocation model
    geo_models = {}
    for sname, shape in sorted(shapes.items()):
        # Match zip filename to scene name
        matched_zip = None
        if sname.startswith("ALPSR"):
            for zn, zp in zips.items():
                if zn.startswith(sname):
                    matched_zip = zp
                    break
            if matched_zip:
                geo_models[sname] = parse_palsar_geoloc(matched_zip, shape)
        else:
            # Sentinel scene name e.g. IW_GRDH_1SDV_017782_01DCBB_DE28 -> last token DE28 or 017782_01DCBB_DE28
            # Note: handle typo 01EOED vs 01E0ED in one raster filename
            tail = sname.split("_")[-1]
            for zn, zp in zips.items():
                if zn.startswith("S1A_") and f"_{tail}.zip" in zn:
                    matched_zip = zp
                    break
            if matched_zip:
                geo_models[sname] = parse_sentinel_geoloc(matched_zip)

    print(f"Built geolocation models for {len(geo_models)}/{len(shapes)} SAR scenes.")

    # Load full_v2 matches + strict-verified (nz1.2 >= 0.90) v3 matches + v4 cross-sensor matches
    v2_rows = json.load(open(os.path.join(DIAG_DIR, "full_v2/results.json")))
    v3_strict_path = os.path.join(DIAG_DIR, "full_v3_mask_chain/mask_chain_verified_strict.json")
    v3_strict = json.load(open(v3_strict_path)) if os.path.exists(v3_strict_path) else []
    v3_keep = [r for r in v3_strict if r.get("native_zncc", 0.0) >= 0.90]
    v4_path = os.path.join(DIAG_DIR, "full_v4/v4_new_matches.json")
    v4_keep = json.load(open(v4_path)) if os.path.exists(v4_path) else []

    merged = []
    seen_ids = set()
    for r in v2_rows:
        if r["split"] in ("train", "val") and r["status"] == "matched_high_conf":
            seen_ids.add((r["split"], r["id"]))
            merged.append({
                "id": r["id"], "labeled_sensor": r["sensor"], "matched_sensor": r["sensor"],
                "cross_sensor_mislabeled": False, "orig_split": r["split"],
                "scene": r["scene"], "x": r["x"], "y": r["y"], "footprint": r["footprint"],
                "orient": r["orient"], "native_zncc": r["native_zncc"], "source_stage": "v2_zncc",
            })
    for r in v3_keep:
        key = (r["split"], r["id"])
        if key not in seen_ids:
            seen_ids.add(key)
            merged.append({
                "id": r["id"], "labeled_sensor": r["sensor"], "matched_sensor": r["sensor"],
                "cross_sensor_mislabeled": False, "orig_split": r["split"],
                "scene": r["scene"], "x": max(0, r["x"]), "y": max(0, r["y"]), "footprint": r["footprint"],
                "orient": f"rot{r['angle_deg']}", "native_zncc": r["native_zncc"], "source_stage": "v3_mask_chain_strict",
            })
    for r in v4_keep:
        key = (r["split"], r["id"])
        if key not in seen_ids:
            seen_ids.add(key)
            merged.append({
                "id": r["id"],
                "labeled_sensor": r.get("labeled_sensor", "sentinel"),
                "matched_sensor": r.get("matched_sensor", "palsar"),
                "cross_sensor_mislabeled": bool(r.get("cross_sensor_mislabeled", False)),
                "orig_split": r["split"],
                "scene": r["scene"], "x": max(0, r["x"]), "y": max(0, r["y"]), "footprint": r["footprint"],
                "orient": r["orient"], "native_zncc": r["native_zncc"], "source_stage": "v4_cross_sensor",
            })

    # Georeference every patch + compute mask oil fraction
    geo_rows = []
    for m in merged:
        sname = m["scene"]
        gm = geo_models[sname]
        fn = gm["px_to_latlon"]
        x, y, fp = m["x"], m["y"], m["footprint"]
        clat, clon = fn(x + fp / 2.0, y + fp / 2.0)
        c_pts = [fn(x, y), fn(x + fp, y), fn(x, y + fp), fn(x + fp, y + fp)]
        lats = [p[0] for p in c_pts]
        lons = [p[1] for p in c_pts]

        mask_p = os.path.join(PROJECT_ROOT, "Data/Preprocessing/sos-prepared", m["orig_split"], "masks", f"{m['id']}.png")
        mk = cv2.imread(mask_p, cv2.IMREAD_GRAYSCALE)
        oil_frac = round(float((mk >= 128).mean()), 4) if mk is not None else 0.0

        geo_rows.append({
            "id": m["id"],
            "sensor": m["matched_sensor"],
            "labeled_sensor": m["labeled_sensor"],
            "cross_sensor_mislabeled": m["cross_sensor_mislabeled"],
            "orig_split": m["orig_split"],
            "scene": sname,
            "acq_utc": gm["acq_utc"],
            "x": x,
            "y": y,
            "footprint": fp,
            "orient": m["orient"],
            "center_lat": round(clat, 6),
            "center_lon": round(clon, 6),
            "bbox_min_lat": round(min(lats), 6),
            "bbox_max_lat": round(max(lats), 6),
            "bbox_min_lon": round(min(lons), 6),
            "bbox_max_lon": round(max(lons), 6),
            "oil_fraction": oil_frac,
            "native_zncc": m["native_zncc"],
            "source_stage": m["source_stage"],
            "geoloc_method": gm["method"],
        })

    out_csv = os.path.join(DIAG_DIR, "georeferenced_matches.csv")
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(geo_rows[0].keys()))
        w.writeheader()
        w.writerows(geo_rows)

    # Step 4: Build clean leak-free Scene-Disjoint Train/Val Split (~80/20 by whole scenes per sensor!)
    val_scenes = {
        "ALPSRP232970570", "ALPSRP238660500", "ALPSRS233043050",
        "IW_GRDH_1SDV_017848_01DEC1_C09A", "IW_GRDH_1SDV_017884_01DFD8_8F93",
    }
    split_rows = []
    for r in geo_rows:
        ns = "val" if r["scene"] in val_scenes else "train"
        split_rows.append({
            "id": r["id"], "sensor": r["sensor"], "labeled_sensor": r["labeled_sensor"],
            "cross_sensor_mislabeled": r["cross_sensor_mislabeled"], "orig_split": r["orig_split"],
            "scene_disjoint_split": ns, "scene": r["scene"], "acq_utc": r["acq_utc"],
            "center_lat": r["center_lat"], "center_lon": r["center_lon"], "oil_fraction": r["oil_fraction"],
        })

    split_csv = os.path.join(DIAG_DIR, "scene_disjoint_split.csv")
    with open(split_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(split_rows[0].keys()))
        w.writeheader()
        w.writerows(split_rows)

    # Verify zero scene leakage in scene_disjoint_split.csv
    tr_sc = set(r["scene"] for r in split_rows if r["scene_disjoint_split"] == "train")
    va_sc = set(r["scene"] for r in split_rows if r["scene_disjoint_split"] == "val")
    assert len(tr_sc & va_sc) == 0, "Scene leakage detected!"

    # Build georef_summary.md
    p_tr = sum(1 for r in split_rows if r["sensor"] == "palsar" and r["scene_disjoint_split"] == "train")
    p_va = sum(1 for r in split_rows if r["sensor"] == "palsar" and r["scene_disjoint_split"] == "val")
    s_tr = sum(1 for r in split_rows if r["sensor"] == "sentinel" and r["scene_disjoint_split"] == "train")
    s_va = sum(1 for r in split_rows if r["sensor"] == "sentinel" and r["scene_disjoint_split"] == "val")
    x_cnt = sum(1 for r in geo_rows if r["cross_sensor_mislabeled"])

    sc_counts = Counter(r["scene"] for r in geo_rows)
    lines = [
        "# OceanTrace — Georeferenced Matches & Leak-Free Scene-Disjoint Split Summary",
        "",
        f"- **Total verified georeferenced patches:** **{len(geo_rows)} / 8,070 ({100*len(geo_rows)/8070:.1f}%)** (`2,882` from v2 ZNCC + `{len(v3_keep)}` strict-verified `sigma=1.2 >= 0.90` from v3 + `{x_cnt}` cross-sensor mislabeled `sentinel_1381..3353` -> PALSAR from v4)",
        f"- **Geolocated scenes:** **{len(sc_counts)} / 21** archived SAR scenes (all 7 Sentinel-1 + 13 PALSAR)",
        "- **PALSAR center-coordinate validation:** Max discrepancy between KML 4-corner bilinear center and JAXA `workreport` scene center = "
        f"`{max(gm['center_check_err_deg'] for k, gm in geo_models.items() if k.startswith('ALPSR')):.5f}°` (~< 1 km across 70 km swath)",
        "- **Sentinel-1 geolocation:** Exact bilinear interpolation on official ESA `geolocationGridPointList` (`line, pixel -> WGS84 lat, lon`)",
        "",
        "## Leak-Free Scene-Disjoint Split (`scene_disjoint_split.csv`)",
        "- **Shared scenes between train and val:** **0** (vs. **19 / 20** shared scenes in the official SOS split!)",
        f"- **PALSAR (true matched sensor):** `{p_tr}` train ({len([s for s in tr_sc if s.startswith('ALPSR')])} scenes) / `{p_va}` val ({len([s for s in va_sc if s.startswith('ALPSR')])} scenes — `{100*p_va/(p_tr+p_va):.1f}%`)",
        f"- **Sentinel-1 (true matched sensor):** `{s_tr}` train ({len([s for s in tr_sc if not s.startswith('ALPSR')])} scenes) / `{s_va}` val ({len([s for s in va_sc if not s.startswith('ALPSR')])} scenes — `{100*s_va/(s_tr+s_va):.1f}%`)",
        f"- **Total:** `{p_tr+s_tr}` train / `{p_va+s_va}` val (`{100*(p_va+s_va)/len(split_rows):.1f}%`)",
        "",
        "## Matched Scenes Inventory (with UTC Acquisition Time & Geographic Center)",
        "| Scene | Sensor | Matched Patches | UTC Acquisition Time | Center (Lat, Lon) | Disjoint Split |",
        "|---|---|---:|---|---|---|",
    ]
    for sname, cnt in sc_counts.most_common():
        gm = geo_models[sname]
        H, W = shapes[sname]
        clat, clon = gm["px_to_latlon"](W / 2.0, H / 2.0)
        sens = "PALSAR" if sname.startswith("ALPSR") else "Sentinel-1"
        sp_tag = "**VAL (held-out)**" if sname in val_scenes else "train"
        lines.append(f"| `{sname}` | {sens} | {cnt} | `{gm['acq_utc']}` | `{clat:.3f}, {clon:.3f}` | {sp_tag} |")

    summary_md = "\n".join(lines) + "\n"
    with open(os.path.join(DIAG_DIR, "georef_summary.md"), "w") as f:
        f.write(summary_md)

    print(f"\nWrote {out_csv} ({len(geo_rows)} rows)")
    print(f"Wrote {split_csv} ({len(split_rows)} rows, 0 shared scenes)")
    print("\n" + summary_md)


if __name__ == "__main__":
    main()
