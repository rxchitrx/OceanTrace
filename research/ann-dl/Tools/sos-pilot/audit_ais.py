"""Verify the bounded NOAA daily archive and inspect continuous regional tracks.
No interpolation, synthetic gap generation, normalization or training is performed.
"""
import collections,csv,datetime,io,json,math,time,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'Data/AIS';ARCHIVE=D/'archives/AIS_2020_07_01.zip';EXPECTED=320722074

def save(name,value):
    path=D/name;tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2));tmp.replace(path)

def main():
    deadline=time.monotonic()+7200
    while not ARCHIVE.exists() or ARCHIVE.stat().st_size<EXPECTED:
        if time.monotonic()>deadline:raise TimeoutError('Daily archive has not finished downloading')
        save('track-audit-progress.json',dict(status='waiting_for_complete_archive',downloaded_bytes=ARCHIVE.stat().st_size if ARCHIVE.exists() else 0,expected_bytes=EXPECTED))
        time.sleep(15)
    assert ARCHIVE.stat().st_size==EXPECTED
    vessels=collections.defaultdict(list);counts=collections.Counter();fields=None
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None,'ZIP CRC verification failed'
        member=next(n for n in z.namelist() if n.lower().endswith('.csv'))
        with io.TextIOWrapper(z.open(member),encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f);fields=reader.fieldnames
            for r in reader:
                counts['national_records']+=1
                try:
                    lat,lon=float(r['LAT']),float(r['LON'])
                    if not (-90<=lat<=90 and -180<=lon<=180):counts['invalid_coordinates']+=1;continue
                    # Bounded US northern Gulf research subset. No claimed SAR pairing.
                    if not (27<=lat<=30.5 and -96<=lon<=-88):continue
                    t=datetime.datetime.fromisoformat(r['BaseDateTime'].replace('Z','+00:00'))
                    if t.tzinfo is None:t=t.replace(tzinfo=datetime.timezone.utc)
                    t=t.astimezone(datetime.timezone.utc)
                    mmsi=r['MMSI']
                    if not mmsi.isdigit() or len(mmsi)!=9:counts['invalid_regional_mmsi']+=1;continue
                    vessels[mmsi].append((t,lat,lon,r))
                    counts['regional_records']+=1
                except (ValueError,KeyError):counts['malformed_records']+=1
    clean_path=D/'northern-gulf-2020-07-01-clean.csv'
    names=['MMSI','BaseDateTime','LAT','LON','SOG','COG','Heading','VesselType','Status']
    examples=[];intervals=[];track_rows=[];kept=0
    with clean_path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=names);writer.writeheader()
        for mmsi,observations in vessels.items():
            observations.sort(key=lambda x:x[0]);unique=[];seen=set()
            for row in observations:
                key=(row[0],row[1],row[2])
                if key in seen:counts['exact_duplicates_removed']+=1;continue
                seen.add(key);unique.append(row)
            timestamp_counts=collections.Counter(row[0] for row in unique)
            conflicts={t for t,n in timestamp_counts.items() if n>1}
            counts['conflicting_timestamp_records_excluded']+=sum(timestamp_counts[t] for t in conflicts)
            unique=[r for r in unique if r[0] not in conflicts]
            for t,lat,lon,raw in unique:
                out={name:raw.get(name,'') for name in names};out['BaseDateTime']=t.isoformat();writer.writerow(out);kept+=1
            segments=[];segment=[]
            for row in unique:
                dt=(row[0]-segment[-1][0]).total_seconds() if segment else 0
                if segment and dt>300:segments.append(segment);segment=[]
                if dt>0:intervals.append(dt)
                segment.append(row)
            if segment:segments.append(segment)
            for i,seg in enumerate(segments):
                duration=(seg[-1][0]-seg[0][0]).total_seconds()
                gaps=[(b[0]-a[0]).total_seconds() for a,b in zip(seg,seg[1:])]
                info=dict(MMSI=mmsi,segment=i,records=len(seg),duration_minutes=duration/60,max_interval_seconds=max(gaps,default=0),start=seg[0][0].isoformat(),end=seg[-1][0].isoformat())
                track_rows.append(info)
                if duration>=7200 and len(seg)>=120:examples.append((info,seg))
    examples.sort(key=lambda x:(x[0]['duration_minutes'],x[0]['records']),reverse=True)
    for rank,(info,seg) in enumerate(examples[:3],1):
        with (D/f'example-continuous-track-{rank}.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['MMSI','BaseDateTime','LAT','LON','SOG','COG'])
            for t,lat,lon,raw in seg:w.writerow([info['MMSI'],t.isoformat(),lat,lon,raw.get('SOG',''),raw.get('COG','')])
    save('segments.json',track_rows)
    result=dict(status='verified_and_audited',source_url='https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2020/AIS_2020_07_01.zip',archive_bytes=EXPECTED,archive_crc_verified=True,fields=fields,counts=dict(counts),clean_records=kept,unique_regional_vessels=len(vessels),segments=len(track_rows),segments_at_least_2h_and_120_records=len(examples),examples=[x[0] for x in examples[:3]],bbox=dict(lat_min=27,lat_max=30.5,lon_min=-96,lon_max=-88),segment_rule='Provisional continuity audit: split on gaps greater than 5 minutes. Not yet a training contract.',limitations=['No interpolation, model training or synthetic-gap benchmark performed','No SAR image-time pairing established','Position-jump/speed plausibility and vessel-disjoint evaluation splits still need checks'])
    save('track-audit.json',result);save('track-audit-progress.json',dict(status='completed',clean_records=kept))
    acquisition=json.loads((D/'acquisition.json').read_text());acquisition['status']='downloaded_zip_crc_verified';acquisition['track_audit']='Data/AIS/track-audit.json';save('acquisition.json',acquisition)
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
