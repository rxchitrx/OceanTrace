"""Post-run structural/threshold verification and reviewer index. No accuracy claim."""
import collections,html,json,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];D=ROOT/'Data/SOS';O=D/'full_mapping'

def main():
    end=time.monotonic()+10800
    while not (O/'summary.json').exists():
        if time.monotonic()>end:raise TimeoutError('Mapping completion summary not produced')
        time.sleep(20)
    rows=json.loads((O/'results.json').read_text());summary=json.loads((O/'summary.json').read_text())
    assert len(rows)==len({r['patch_key'] for r in rows})==8070
    assert summary['all_compatible_scenes_searched'] and summary['patches_with_search_attempt']==8070
    for p in O.glob('*-patches.jsonl'):
        records=[json.loads(s) for s in p.read_text().splitlines()]
        assert len(records)==len({r['patch_key'] for r in records})
    for r in rows:
        assert r['attempted_scenes']==(14 if r['sensor']=='palsar' else 7)
        if r['status']=='candidate_needs_review':
            best=r['candidates'][0]
            assert best['passes_checks'] and best['correlation']>=.75 and best['inliers']>=12
            assert best['inlier_ratio']>=.6 and best['coverage']>=.15
            assert best['evidence_file'] and (D/best['evidence_file']).exists()
    split_lookup={p['id']:p['split'] for p in json.loads((D/'pilot/selected_50.json').read_text())}
    current={r['patch_key']:r for r in rows};baseline=[]
    for old in json.loads((D/'pilot/results.json').read_text()):
        if old['status']!='candidate_needs_review':continue
        key=split_lookup[old['patch']]+'/'+old['patch'];new=current[key]
        old_scene=old['candidates'][0]['scene']
        baseline.append(dict(patch_key=key,pilot_candidate_scene=old_scene,new_status=new['status'],pilot_scene_in_native_top3=any(c['scene']==old_scene for c in new['candidates'])))
    by_sensor={s:dict(collections.Counter(r['status'] for r in rows if r['sensor']==s)) for s in ('palsar','sentinel')}
    report=dict(structural_checks_passed=True,all_8070_unique_split_name_keys=True,all_compatible_scenes_queried=True,candidate_threshold_and_evidence_checks_passed=True,counts_by_sensor=by_sensor,pilot_regression=baseline,limitations=['These checks establish execution and conservative threshold consistency, not mapping accuracy','Approximate SIFT retrieval is not exhaustive pixel registration','Candidate evidence still needs visual review; ambiguous/unknown records remain unresolved','No scene-held-out split, geospatial AIS join or model training has been completed'])
    (O/'verification.json').write_text(json.dumps(report,indent=2))
    cards=[]
    for sensor in ('palsar','sentinel'):
        candidates=sorted([r for r in rows if r['sensor']==sensor and r['status']=='candidate_needs_review'],key=lambda r:r['candidates'][0]['correlation'],reverse=True)
        # Both strong and borderline cases; do not curate only successes.
        chosen=(candidates[:3]+candidates[-3:]) if len(candidates)>6 else candidates
        for r in chosen:
            b=r['candidates'][0];path=Path(b['evidence_file']).relative_to('full_mapping').as_posix()
            cards.append(f'<figure><figcaption>{html.escape(r["patch_key"])} → {html.escape(b["scene"])} · correlation {b["correlation"]:.3f}</figcaption><img src="{path}" alt="Original patch, aligned source crop, absolute difference"></figure>')
    page='<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>SOS source mapping review</title><style>body{font:16px system-ui;max-width:1100px;margin:24px auto;padding:0 16px}figure{margin:24px 0}img{max-width:100%;height:auto}figcaption{overflow-wrap:anywhere}</style><h1>Source mapping: review candidates</h1><p>Each panel: original patch, aligned source crop, absolute difference. Candidate matches need review; similarity is not a probability.</p>'+''.join(cards)+'</html>'
    (O/'Review.html').write_text(page)
    (O/'REPORT.md').write_text('# Full SOS mapping — execution report\n\n'+json.dumps(summary,indent=2)+'\n\n## Counts by sensor\n'+json.dumps(by_sensor,indent=2)+'\n\nStructural verification passed for 8,070 distinct split/name keys and all compatible-source queries. This is not independently measured ancestry accuracy. See verification.json for pilot regression and limitations; Review.html for representative strong and borderline candidate evidence. Parent visual inspection remains a separate check.\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
