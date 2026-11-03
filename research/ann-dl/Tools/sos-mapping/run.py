"""Resumable native resolution tile-SIFT SOS source search. Scores are diagnostics."""
import json, cv2, numpy as np, rasterio, os, csv, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; D=ROOT/'Data/SOS'; OUT=D/'full_mapping'; OUT.mkdir(exist_ok=True)
cv2.setNumThreads(2)
def norm(a):
 a=np.asarray(a,dtype=np.float32); v=np.isfinite(a)&(a>0)
 if not v.any(): return np.zeros(a.shape,np.uint8)
 a=np.log1p(np.maximum(np.nan_to_num(a),0)); lo,hi=np.percentile(a[v],[1,99]); return np.clip((a-lo)*255/max(hi-lo,1e-6),0,255).astype('uint8')
def main():
 scenes=json.load(open(D/'metadata/scenes.json')); patches=[]
 for split in ['train','val']:
  for f in sorted((D/'patches'/split).glob('*.png')): patches.append((split,f))
 print('patches',len(patches),flush=True)
 # Load tile index per compatible sensor; each 1024 native tile, overlap 128; descriptor cache on disk.
 index={}
 for s in scenes:
  sensor='palsar' if s['sensor']=='PALSAR' else 'sentinel'; path=D/'scenes'/(s['published_id'].replace(' ','_')+'.tif')
  if not path.exists(): continue
  with rasterio.open(path) as ds:
   print('index',s['published_id'],ds.shape,flush=True); tiles=[]
   step=896
   for y in range(0,ds.height,step):
    for x in range(0,ds.width,step):
     h=min(1024,ds.height-y); w=min(1024,ds.width-x)
     if h<256 or w<256: continue
     im=norm(ds.read(1,window=((y,y+h),(x,x+w)),masked=True).filled(0)); kp,de=cv2.SIFT_create(nfeatures=1800,contrastThreshold=.015).detectAndCompute(im,None)
     if de is not None and len(kp)>5: tiles.append((x,y,im,kp,de))
   index.setdefault(sensor,[]).append((s['published_id'],tiles))
 json.dump({k:[(n,len(t)) for n,t in v] for k,v in index.items()},open(OUT/'tile_index.json','w'),indent=2)
 results=[]; rf=OUT/'results.jsonl'; done={}
 if rf.exists():
  for line in rf.read_text().splitlines():
   try: done[json.loads(line)['patch']]=1
   except: pass
 for i,(split,f) in enumerate(patches):
  pid=f.stem
  if pid in done: continue
  p=cv2.imread(str(f),0); sensor='palsar' if split=='train' else 'sentinel' # corrected below metadata mapping
  # Dataset split labels are authoritative sensor directories in filenames metadata where available
  sensor='palsar' if 'palsar' in str(f).lower() else 'sentinel'
  pk,pd=cv2.SIFT_create(nfeatures=1500,contrastThreshold=.015).detectAndCompute(p,None); ranked=[]
  if pd is not None:
   for name,tiles in index.get(sensor,[]):
    best=None
    for x,y,im,kp,de in tiles:
     pairs=cv2.BFMatcher(cv2.NORM_L2).knnMatch(pd,de,k=2); good=[a for pair in pairs if len(pair)==2 for a,b in [pair] if a.distance<.72*b.distance]
     if len(good)<8: continue
     src=np.float32([pk[m.queryIdx].pt for m in good]); dst=np.float32([kp[m.trainIdx].pt for m in good]); M,ins=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=3,maxIters=1500)
     if M is None: continue
     keep=ins.ravel().astype(bool); aligned=cv2.warpAffine(im,M,(p.shape[1],p.shape[0]),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP); mask=cv2.warpAffine(np.ones(im.shape,np.uint8),M,(p.shape[1],p.shape[0]),flags=cv2.INTER_NEAREST|cv2.WARP_INVERSE_MAP)>0
     corr=float(np.corrcoef(p[mask],aligned[mask])[0,1]) if mask.mean()>.9 and p[mask].std()>1 and aligned[mask].std()>1 else -1
     c={'scene':name,'x':x,'y':y,'correlation':corr,'inliers':int(keep.sum()),'matches':len(good),'coverage':float(cv2.contourArea(cv2.convexHull(src[keep]))/p.size) if keep.sum()>2 else 0,'affine':M.tolist()}
     if best is None or (c['correlation'],c['inliers'])>(best['correlation'],best['inliers']): best=c
    if best: ranked.append(best)
  ranked.sort(key=lambda c:(c['correlation'],c['inliers']),reverse=True); row={'patch':pid,'split':split,'sensor':sensor,'status':'candidate_needs_review' if ranked and ranked[0]['inliers']>=8 else 'unknown','best':ranked[0] if ranked else None,'runnerup':ranked[1] if len(ranked)>1 else None,'attempted_scenes':len(index.get(sensor,[])),'attempted_tiles':sum(len(t) for _,t in index.get(sensor,[]))}
  with open(rf,'a') as o: o.write(json.dumps(row)+'\n')
  if i%25==0: print(i,pid,row['status'],flush=True)
if __name__=='__main__': main()
