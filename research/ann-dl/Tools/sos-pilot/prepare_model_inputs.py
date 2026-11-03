"""Prepare a reviewable binary-segmentation baseline; keep all original files.

Source split names are preserved, not claimed to be acquisition-disjoint.
Mask threshold is an explicit baseline choice (128), not recovered physical truth.
"""
import csv,hashlib,json,zipfile
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'Data/Preprocessing';OUT=D/'sos-prepared'

def load_pair(image_path,mask_path):
    image=np.asarray(Image.open(image_path).convert('L'),dtype=np.float32)[None]/255.0
    mask=np.asarray(Image.open(mask_path).convert('L'))
    if not np.isin(mask,[0,255]).all():raise ValueError('Prepared mask must be binary')
    target=(mask>0).astype(np.float32)[None]
    assert image.shape==target.shape==(1,256,256)
    assert np.isfinite(image).all() and 0<=image.min()<=image.max()<=1
    return image,target

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    records=[]
    with zipfile.ZipFile(ROOT/'data_samples/masks.zip') as z:
        masks={(Path(n).parent.name,Path(n).name):n for n in z.namelist() if n.endswith('.png') and '__MACOSX' not in n}
        for i,p in enumerate(sorted((ROOT/'Data/SOS/patches').rglob('*.png')),1):
            split=p.parent.name;key=split+'/'+p.stem
            with Image.open(p) as raw:
                a=np.asarray(raw)
                assert a.shape==(256,256,3) and (a[:,:,0]==a[:,:,1]).all() and (a[:,:,0]==a[:,:,2]).all()
                gray=Image.fromarray(a[:,:,0])
            member=masks[split,p.name]
            with Image.open(z.open(member)) as mask:
                label=np.asarray(mask.convert('L'))
            assert label.shape==(256,256)
            binary=np.where(label>=128,255,0).astype(np.uint8)
            image_out=OUT/split/'images'/p.name;mask_out=OUT/split/'masks'/p.name
            image_out.parent.mkdir(parents=True,exist_ok=True);mask_out.parent.mkdir(parents=True,exist_ok=True)
            if not image_out.exists():gray.save(image_out,compress_level=3)
            if not mask_out.exists():Image.fromarray(binary).save(mask_out,compress_level=3)
            x,y=load_pair(image_out,mask_out)
            # Verify saved image conversion is lossless against its source channel.
            assert np.array_equal(np.asarray(Image.open(image_out)),a[:,:,0])
            records.append(dict(patch_key=key,split=split,sensor=p.stem.split('_')[0],
                                raw_image=str(p.relative_to(ROOT)),raw_mask_zip_member=member,
                                raw_image_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                                prepared_image=str(image_out.relative_to(ROOT)),prepared_mask=str(mask_out.relative_to(ROOT)),
                                image_tensor_shape='1x256x256',image_tensor_dtype='float32',image_normalization='uint8/255',
                                stored_mask_values='0,255',target_tensor_values='0,1',mask_threshold=128,
                                original_intermediate_mask_pixels=int(((label>0)&(label<255)).sum()),
                                foreground_fraction=float(y.mean()),scene_id='',mapping_status='unverified_do_not_infer_from_filename'))
            if i%1000==0:print('Prepared and verified',i,'pairs',flush=True)
    assert len(records)==len({r['patch_key'] for r in records})==8070
    with (D/'sos-prepared-manifest.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    report=dict(status='prepared_and_verified',pairs=len(records),image_channels=1,input_tensor_shape=[1,256,256],input_dtype='float32',image_scaling='uint8/255 applied at load time',mask_disk_values=[0,255],mask_tensor_values=[0,1],threshold=128,all_saved_images_pixel_equal_to_source_channel=True,all_pairs_loaded_and_checked=True,unique_id='split/filename',source_split_preserved=True,scene_disjointness_verified=False,original_files_modified=False,training_started=False,limitations=['128 is an explicit baseline label-conversion choice; label quality is not independently verified','Original masks retained; gray-valued masks, empty masks and full masks remain flagged for review','No augmentations, radiometric recalibration, train-statistic fitting or source-scene reassignment applied','Current provided split is a benchmark split, not a verified scene-held-out split'])
    (D/'sos-prepared-summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
