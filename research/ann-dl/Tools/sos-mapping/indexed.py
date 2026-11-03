"""Native tiled SIFT index: one scene in memory; all 8070 patches queried.

Indexes cover every source tile. Approximate descriptor retrieval is followed by
source-pixel geometry/alignment checks. Unknowns are never forced into a scene.
"""
import argparse, collections, csv, gc, hashlib, json, time
from pathlib import Path
import cv2
import numpy as np
import rasterio
from rasterio.windows import Window

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'Data/SOS'
O = D / 'full_mapping'
O.mkdir(exist_ok=True)
cv2.setNumThreads(2)
SIFT = cv2.SIFT_create(nfeatures=1800, contrastThreshold=.015)

def save(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False))
    tmp.replace(path)

def norm(a):
    x = np.nan_to_num(np.asarray(a, np.float32))
    valid = x > 0
    if not valid.any(): return np.zeros(x.shape, np.uint8)
    x = np.log1p(np.maximum(x, 0))
    lo, hi = np.percentile(x[valid], [1, 99])
    return np.clip((x-lo)*255/max(hi-lo, 1e-6), 0, 255).astype('uint8')

def source_index(scene, ds):
    cache = O / 'cache' / (scene + '-native-v1.npz')
    cache.parent.mkdir(exist_ok=True)
    if cache.exists():
        with np.load(cache) as a:
            return a['xy'].copy(), a['des'].copy(), json.loads(str(a['meta']))
    coords, descriptions = [], []
    count, retained = 0, 0
    # Overlapping support, but each keypoint has a unique owner tile to avoid
    # zero-distance duplicate descriptors invalidating nearest-neighbour ratios.
    step, side = 896, 1024
    for y in range(0, ds.height, step):
        for x in range(0, ds.width, step):
            h, w = min(side, ds.height-y), min(side, ds.width-x)
            if h < 32 or w < 32: continue
            image = norm(ds.read(1, window=Window(x,y,w,h), masked=True).filled(0))
            keys, desc = SIFT.detectAndCompute(image, None)
            count += 1
            if desc is not None:
                keep = [i for i,k in enumerate(keys) if (k.pt[0] < step or x+side >= ds.width) and (k.pt[1] < step or y+side >= ds.height)]
                if keep:
                    descriptions.append(desc[keep])
                    coords.append(np.float32([[keys[i].pt[0]+x,keys[i].pt[1]+y] for i in keep]))
                    retained += len(keep)
            if count % 30 == 0:
                save(O/'progress.json', dict(phase='indexing_native_source',scene=scene,tiles_processed=count,descriptors=retained,attempted_patches=0))
                print(scene, 'indexed tiles', count, 'descriptors',retained,flush=True)
    xy = np.concatenate(coords) if coords else np.empty((0,2),np.float32)
    des = np.concatenate(descriptions) if descriptions else np.empty((0,128),np.float32)
    meta = dict(scene=scene,width=ds.width,height=ds.height,tiles=count,features=len(des),native_resolution=True,step=step,tile_size=side,feature_cap_per_tile=1800)
    np.savez(cache,xy=xy,des=des,meta=json.dumps(meta))
    return xy,des,meta

def validate(patch, src, dst, ds):
    if len(src) < 8: return None
    M, flags = cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=3,maxIters=2500,confidence=.995)
    if M is None: return None
    keep = flags.ravel().astype(bool)
    if keep.sum() < 6: return None
    h,w = patch.shape
    corners = np.float32([[[0,0],[w,0],[w,h],[0,h]]])
    mapped = cv2.transform(corners,M)[0]
    x0,y0 = np.floor(mapped.min(axis=0)-3).astype(int)
    x1,y1 = np.ceil(mapped.max(axis=0)+3).astype(int)
    if x0 < 0 or y0 < 0 or x1 > ds.width or y1 > ds.height: return None
    if x1-x0 > 4096 or y1-y0 > 4096 or x1 <= x0 or y1 <= y0: return None
    crop = norm(ds.read(1,window=Window(int(x0),int(y0),int(x1-x0),int(y1-y0)),masked=True).filled(0))
    local = M.copy();local[:,2] -= [x0,y0]
    aligned = cv2.warpAffine(crop,local,(w,h),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP)
    if patch.std() < 1 or aligned.std() < 1: return None
    corr = float(np.corrcoef(patch.ravel(),aligned.ravel())[0,1])
    if not np.isfinite(corr): return None
    err = np.linalg.norm(cv2.transform(src[None],M)[0]-dst,axis=1)
    coverage = float(cv2.contourArea(cv2.convexHull(src[keep])) / patch.size)
    out = dict(correlation=corr,inliers=int(keep.sum()),feature_matches=len(src),inlier_ratio=float(keep.mean()),coverage=coverage,reprojection_p90=float(np.percentile(err[keep],90)),affine=M.tolist(),source_pixel_corners=mapped.tolist())
    out['passes_checks'] = bool(out['inliers']>=12 and out['inlier_ratio']>=.6 and coverage>=.15 and corr>=.75 and out['reprojection_p90']<=3)
    return out,aligned

def query(patch, matcher, xy, ds):
    keys, desc = SIFT.detectAndCompute(patch,None)
    if desc is None or len(keys)<8: return None,'insufficient_patch_features'
    pairs = matcher.knnMatch(desc,k=2)
    good = [a for pair in pairs if len(pair)==2 for a,b in [pair] if a.distance < .72*b.distance]
    if len(good)<8: return None,'insufficient_descriptor_matches'
    source = np.float32([keys[m.queryIdx].pt for m in good])
    target = xy[[m.trainIdx for m in good]]
    # RANSAC on the complete retrieval plus the strongest spatial neighbourhoods.
    cells = np.floor(target/1024).astype(int)
    counts = collections.Counter(map(tuple,cells))
    subsets = [np.arange(len(good))]
    for cell,_ in counts.most_common(4):
        indices = np.flatnonzero(np.max(np.abs(cells-np.array(cell)),axis=1)<=1)
        if len(indices)>=8: subsets.append(indices)
    best = None
    for ids in subsets:
        found = validate(patch,source[ids],target[ids],ds)
        if found and (best is None or found[0]['correlation'] > best[0]['correlation']): best=found
    return best,'geometry_or_pixel_checks_failed' if best is None else 'candidate_evaluated'

def run(controls_only=False):
    inventory=json.loads((D/'metadata/patches.json').read_text())
    for p in inventory: p['key']=p['split']+'/'+p['id']
    assert len(inventory)==8070 and len({p['key'] for p in inventory})==8070
    assert collections.Counter(p['sensor'] for p in inventory)=={'palsar':3877,'sentinel':4193}
    scenes=json.loads((D/'metadata/scenes.json').read_text())
    if controls_only: scenes=[scenes[0],scenes[17]]
    control_rows=[]
    for scene in scenes:
        name=scene['published_id'];sensor='palsar' if scene['sensor']=='PALSAR' else 'sentinel'
        result_file=O/(name.replace(' ','_')+'-patches.jsonl')
        if result_file.exists() and not controls_only:
            done={json.loads(line)['patch_key'] for line in result_file.read_text().splitlines() if line.strip()}
        else: done=set()
        subset=[p for p in inventory if p['sensor']==sensor]
        if len(done)==len(subset) and not controls_only: continue
        with rasterio.open(D/'scenes'/(name.replace(' ','_')+'.tif')) as ds:
            xy,des,meta=source_index(name.replace(' ','_'),ds)
            save(O/(name.replace(' ','_')+'-index.json'),meta)
            matcher=cv2.FlannBasedMatcher(dict(algorithm=1,trees=2),dict(checks=80))
            matcher.add([des]);matcher.train()
            if controls_only:
                for i,(xf,yf) in enumerate([(.35,.35),(.55,.55),(.75,.65)]):
                    x,y=int(ds.width*xf),int(ds.height*yf)
                    tile=norm(ds.read(1,window=Window(x-384,y-384,1024,1024)))
                    patch=tile[384:640,384:640].copy()
                    for rotation in (0,1):
                        test=np.rot90(patch,rotation).copy()
                        candidate,reason=query(test,matcher,xy,ds)
                        error=None
                        if candidate:
                            box=np.asarray(candidate[0]['source_pixel_corners'])
                            error=float(np.linalg.norm(box.mean(axis=0)-[x+128,y+128]))
                        control_rows.append(dict(scene=name,crop=i,rotation_degrees=rotation*90,location_error_pixels=error,result=candidate[0] if candidate else None,reason=reason,known_location=[x,y]))
                for kind,test in [('blank',np.zeros((256,256),np.uint8)),('unrelated_noise',np.random.default_rng(17).integers(0,256,(256,256),dtype=np.uint8))]:
                    candidate,reason=query(test,matcher,xy,ds)
                    control_rows.append(dict(scene=name,negative=kind,result=candidate[0] if candidate else None,reason=reason))
                save(O/'native_controls.json',control_rows)
            else:
                with result_file.open('a',buffering=1) as output:
                    for i,p in enumerate(subset):
                        if p['key'] in done: continue
                        image=cv2.imread(str(D/p['file']),cv2.IMREAD_GRAYSCALE)
                        candidate,reason=query(image,matcher,xy,ds)
                        record=dict(patch=p['id'],patch_key=p['key'],split=p['split'],scene=name,sensor=sensor,reason=reason,candidate=candidate[0] if candidate else None)
                        if candidate and candidate[0]['passes_checks']:
                            evidence=O/'evidence';evidence.mkdir(exist_ok=True)
                            path=evidence/(p['split']+'--'+p['id']+'--'+name.replace(' ','_')+'.png')
                            cv2.imwrite(str(path),np.hstack([image,candidate[1],cv2.absdiff(image,candidate[1])]))
                            record['evidence_file']=str(path.relative_to(D))
                        output.write(json.dumps(record,allow_nan=False)+'\n')
                        if i%100==0:
                            save(O/'progress.json',dict(phase='querying_native_scene',scene=name,scene_patch_index=i+1,scene_patch_total=len(subset),all_patch_total=8070,scope='native-tile feature index, approximate retrieval; no exhaustive pixel search'))
                            print(name,i+1,'/',len(subset),flush=True)
            del matcher,des,xy
        gc.collect()
    if not controls_only: aggregate(inventory,scenes)

def aggregate(inventory,scenes):
    rows={p['key']:dict(patch=p['id'],patch_key=p['key'],sensor=p['sensor'],split=p['split'],attempted_scenes=0,candidates=[]) for p in inventory}
    for path in O.glob('*-patches.jsonl'):
        for line in path.read_text().splitlines():
            item=json.loads(line);r=rows[item['patch_key']];r['attempted_scenes']+=1
            if item['candidate']:
                r['candidates'].append(dict(scene=item['scene'],evidence_file=item.get('evidence_file'),**item['candidate']))
    for r in rows.values():
        r['candidates'].sort(key=lambda c:c['correlation'],reverse=True)
        best=r['candidates'][0] if r['candidates'] else None
        margin=best['correlation']-r['candidates'][1]['correlation'] if len(r['candidates'])>1 else None
        r['status']='candidate_needs_review' if best and best['passes_checks'] and (margin is None or margin>=.1) else 'unknown_or_ambiguous'
        r['correlation_margin']=margin;r['candidates']=r['candidates'][:3]
    result=list(rows.values());save(O/'results.json',result)
    with (O/'results.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['patch_key','patch','sensor','split','status','attempted_scenes','best_scene','correlation'])
        for r in result:
            b=r['candidates'][0] if r['candidates'] else {}
            writer.writerow([r['patch_key'],r['patch'],r['sensor'],r['split'],r['status'],r['attempted_scenes'],b.get('scene',''),b.get('correlation','')])
    summary=dict(status='completed',total_patches=8070,patches_with_search_attempt=sum(r['attempted_scenes']>0 for r in result),all_compatible_scenes_searched=all(r['attempted_scenes']==(14 if r['sensor']=='palsar' else 7) for r in result),counts=dict(collections.Counter(r['status'] for r in result)),auto_assigned=0,method='Native tiled SIFT with approximate descriptor retrieval, geometric and independent pixel checks. Candidate review required; accuracy unmeasured.')
    save(O/'summary.json',summary);save(O/'progress.json',summary)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--controls',action='store_true');a=parser.parse_args()
    run(a.controls)
