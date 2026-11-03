"""Extract verified public patches, select 50 varied samples, make an offline browser."""
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Data/SOS'

def main():
    archive = DATA / 'archives/images.zip'
    assert hashlib.md5(archive.read_bytes()).hexdigest() == 'e5272875611e8b5a2a0d49972224c842'
    masks = ROOT / 'data_samples/masks.zip'
    assert hashlib.md5(masks.read_bytes()).hexdigest() == '09c8a279603c8d7b73c6dc64f91e1106'
    inventory = []
    with zipfile.ZipFile(archive) as images, zipfile.ZipFile(masks) as labels:
        mask_lookup = {(Path(n).parent.name, Path(n).name): n for n in labels.namelist()
                       if n.endswith('.png') and '__MACOSX' not in n}
        for name in sorted(images.namelist()):
            if not name.endswith('.png') or '__MACOSX' in name:
                continue
            split, filename = Path(name).parent.name, Path(name).name
            destination = DATA / 'patches' / split / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                destination.write_bytes(images.read(name))
            gray = np.asarray(Image.open(destination).convert('L'), dtype=np.float32)
            mask = np.asarray(Image.open(labels.open(mask_lookup[split, filename])).convert('L')) >= 128
            inventory.append(dict(id=filename[:-4], sensor=filename.split('_')[0], split=split,
                                  file=destination.relative_to(DATA).as_posix(),
                                  oil_fraction=float(mask.mean()),
                                  texture=float(np.abs(np.diff(gray, axis=0)).mean())))
    assert len(inventory) == 8070
    # 25 per sensor: five quantiles of foreground coverage, spread across texture.
    selected = []
    for sensor in ('palsar', 'sentinel'):
        samples = sorted((p for p in inventory if p['sensor'] == sensor),
                         key=lambda p: (p['oil_fraction'], p['id']))
        for bin_id, indexes in enumerate(np.array_split(np.arange(len(samples)), 5)):
            pool = sorted((samples[int(i)] for i in indexes), key=lambda p: (p['texture'], p['id']))
            for i in np.linspace(0, len(pool) - 1, 5, dtype=int):
                selected.append(dict(pool[i], coverage_bin=bin_id))
    previous = DATA / 'pilot/selected_50.json'
    if previous.exists():
        fixed = json.loads(previous.read_text())
        lookup = {(p['split'], p['id']): p for p in inventory}
        selected = [dict(lookup[p['split'], p['id']], coverage_bin=p['coverage_bin']) for p in fixed]
    assert len(selected) == len({p['id'] for p in selected}) == 50
    (DATA / 'metadata/patches.json').write_text(json.dumps(inventory, indent=2))
    (DATA / 'pilot/selected_50.json').write_text(json.dumps(selected, indent=2))
    with zipfile.ZipFile(masks) as labels:
        for p in selected:
            name = mask_lookup[p['split'], p['id'] + '.png']
            (DATA / 'pilot' / (p['id'] + '_mask.png')).write_bytes(labels.read(name))
    scenes = json.loads((DATA / 'metadata/scenes.json').read_text())
    for r in scenes:
        stem = r['published_id'].replace(' ', '_')
        actual = DATA / 'scenes' / (stem + '-full-raster-preview.jpg')
        if actual.exists():
            r['preview_file'] = actual.relative_to(DATA).as_posix()
    cards = ''.join(f'<figure><a href="{r.get("preview_file", "")}"><img loading="lazy" src="{r.get("preview_file", "")}" alt="{r["published_id"]}"></a><figcaption>{r["published_id"]}<br>{r["date"]} · {r["sensor"]}<br>' + (f'<a href="scenes/{r["published_id"].replace(" ", "_")}.tif">Open full raster TIFF</a>' if r['preview_file'].startswith('scenes/') else 'Catalogue preview · full raster pending') + '</figcaption></figure>' for r in scenes)
    html = '''<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>SOS hands-on image browser</title>
<style>body{font:16px system-ui;max-width:1200px;margin:32px auto;padding:0 20px;background:#f4f3ef;color:#202721}h1{font-size:28px} .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}figure{margin:0;padding:12px;background:white;border:1px solid #d5d9d3;border-radius:8px}img{width:100%;aspect-ratio:1;object-fit:contain;background:#151a17}figcaption{font-size:12px;overflow-wrap:anywhere}button,input,select{font:inherit;padding:8px;margin:4px}nav{position:sticky;top:0;background:#f4f3ef;padding:10px 0}a{color:#176343}.note{padding:14px;background:#e1e9df}#status{font-size:14px}</style>
<h1>SOS: explore the images</h1><p class="note">21 catalogue scene previews below are for visual browsing. They are reduced-resolution products, not the full source rasters. Patch collection: Refined SOS 2025; original numerical patch IDs were renamed by that release. No patch-to-scene mapping has been established.</p>
<h2>21 source-scene previews</h2><div class="grid">SCENE_CARDS</div>
<h2>8,070 image patches</h2><p>Open a patch for full size. Use “Pilot 50” for the varied selection; sensor, oil coverage and texture were used to select it. These are not 50 known scene matches.</p>
<nav><input id="search" placeholder="Search patch name"><select id="sensor"><option value="">Both sensors</option><option>palsar</option><option>sentinel</option></select><select id="split"><option value="">Both splits</option><option>train</option><option>val</option></select><label><input id="pilot" type="checkbox">Pilot 50</label><button id="prev">Previous</button><button id="next">Next</button><div id="status"></div></nav><div id="patches" class="grid"></div>
<script>const items=PATCH_DATA;const pilot=new Set(PILOT_IDS);let page=0;const $=s=>document.getElementById(s);function draw(){const list=items.filter(p=>(!$('search').value||p.id.includes($('search').value))&&(!$('sensor').value||p.sensor===$('sensor').value)&&(!$('split').value||p.split===$('split').value)&&(!$('pilot').checked||pilot.has(p.split+'/'+p.id)));page=Math.max(0,Math.min(page,Math.ceil(list.length/24)-1));$('status').textContent=`${list.length} patches · page ${page+1} of ${Math.max(1,Math.ceil(list.length/24))}`;$('patches').innerHTML=list.slice(page*24,page*24+24).map(p=>`<figure><a href="${p.file}"><img loading="lazy" src="${p.file}" alt="${p.id}"></a><figcaption>${p.id} · ${p.split}<br>Mask foreground ${(100*p.oil_fraction).toFixed(1)}%${pilot.has(p.split+'/'+p.id)?' · pilot':''}</figcaption></figure>`).join('')}for(const id of ['search','sensor','split','pilot'])$(id).oninput=()=>{page=0;draw()};$('prev').onclick=()=>{page--;draw()};$('next').onclick=()=>{page++;draw()};draw();</script></html>'''
    html = html.replace('SCENE_CARDS', cards).replace('PATCH_DATA', json.dumps(inventory)).replace('PILOT_IDS', json.dumps([p['split']+'/'+p['id'] for p in selected]))
    (DATA / 'Browse.html').write_text(html)
    print('Prepared', len(inventory), 'patches; selected', Counter(p['sensor'] for p in selected), flush=True)

if __name__ == '__main__':
    main()
