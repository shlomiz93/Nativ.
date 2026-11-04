# Nationwide compact timetable, built per real calendar date (the way Moovit / Google Maps use GTFS), not per weekday type.
# usage: python3 tools/build_transit.py --gtfs DIR --out DIR [--days 8] [--start YYYYMMDD]
# Writes transit_<hash>.json.gz (one per DISTINCT day, so Sun-Thu share a file) and transit_index.json = {generated, dates:{YYYYMMDD: hash}}.
import pandas as pd, numpy as np, json, gzip, sys, time, argparse, hashlib, os, datetime as dt
ap=argparse.ArgumentParser(); ap.add_argument('--gtfs',required=True); ap.add_argument('--out',required=True); ap.add_argument('--days',type=int,default=8); ap.add_argument('--start',default=None)
A=ap.parse_args(); G=A.gtfs.rstrip('/')+'/'; OUT=A.out.rstrip('/')+'/'; os.makedirs(OUT,exist_ok=True)
T0=time.time(); lg=lambda *a: print(round(time.time()-T0),*a,flush=True)
today=dt.datetime.strptime(A.start,'%Y%m%d').date() if A.start else dt.datetime.now(dt.timezone(dt.timedelta(hours=2))).date()
dates=[today+dt.timedelta(days=i) for i in range(-1,A.days-1)]   # yesterday too: trips after midnight belong to it
cal=pd.read_csv(G+'calendar.txt',encoding='utf-8-sig')
cd=pd.read_csv(G+'calendar_dates.txt',encoding='utf-8-sig') if os.path.exists(G+'calendar_dates.txt') else None
WD=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
def active(d):
    n=int(d.strftime('%Y%m%d')); c=cal[(cal[WD[d.weekday()]]==1)&(cal.start_date<=n)&(cal.end_date>=n)]; S=set(c.service_id)
    if cd is not None:
        e=cd[cd.date==n]; S|=set(e[e.exception_type==1].service_id); S-=set(e[e.exception_type==2].service_id)
    return frozenset(S)
act={d:active(d) for d in dates}
sets=sorted(set(act.values()),key=lambda s:min(d for d in act if act[d]==s)); lg('dates',len(dates),'distinct day-sets',len(sets))
if not any(len(s) for s in sets): sys.exit('no active services in the feed for the requested dates (feed expired?)')
trips=pd.read_csv(G+'trips.txt',encoding='utf-8-sig',usecols=['route_id','service_id','trip_id','trip_headsign'],dtype={'trip_id':str})
routes=pd.read_csv(G+'routes.txt',encoding='utf-8-sig',usecols=['route_id','agency_id','route_short_name','route_type'])
ag=pd.read_csv(G+'agency.txt',encoding='utf-8-sig'); AG=dict(zip(ag.agency_id,ag.agency_name))
trips=trips.merge(routes,on='route_id',how='left')
use=set()
for s in sets: use|=set(trips[trips.service_id.isin(s)].trip_id)
lg('union trips',len(use))
parts=[]
for ch in pd.read_csv(G+'stop_times.txt',encoding='utf-8-sig',usecols=['trip_id','departure_time','stop_id','stop_sequence'],dtype={'trip_id':str,'departure_time':str,'stop_id':np.int32,'stop_sequence':np.int16},chunksize=2_000_000):
    ch=ch[ch.trip_id.isin(use)]
    if len(ch):
        h=ch.departure_time.str.slice(0,2).astype(np.int32); m=ch.departure_time.str.slice(3,5).astype(np.int32); sc=ch.departure_time.str.slice(6,8).astype(np.int32)
        parts.append(ch.assign(dep=(h*3600+m*60+sc).astype(np.int32)).drop(columns='departure_time'))
st_all=pd.concat(parts,ignore_index=True); del parts
st_all['tc'],uniq=pd.factorize(st_all.trip_id); tid_of=dict(enumerate(uniq)); st_all=st_all.drop(columns='trip_id')
lg('stop_times kept',len(st_all))
tr=trips.set_index('trip_id'); stops=pd.read_csv(G+'stops.txt',encoding='utf-8-sig',usecols=['stop_id','stop_name','stop_lat','stop_lon']).set_index('stop_id')
hash_of={}; files={}
for si,sv in enumerate(sets):
    ok=set(trips[trips.service_id.isin(sv)].trip_id); okc=np.array([tid_of[i] in ok for i in range(len(uniq))])
    t=st_all[okc[st_all.tc.to_numpy()]].sort_values(['tc','stop_sequence'])
    used=sorted(t.stop_id.unique()); sidx={s:i for i,s in enumerate(used)}
    S=[[int(round(stops.loc[s].stop_lat*1e5)),int(round(stops.loc[s].stop_lon*1e5)),str(stops.loc[s].stop_name)] for s in used]
    lines=[]; lidx={}; pats={}
    for tc,g in t.groupby('tc',sort=False):
        r=tr.loc[tid_of[tc]]; sq=tuple(sidx[x] for x in g.stop_id); hs='' if pd.isna(r.trip_headsign) else str(r.trip_headsign)
        lk=(str(r.route_short_name),int(r.route_type),int(r.agency_id),hs)
        if lk not in lidx: lidx[lk]=len(lines); lines.append([lk[0],lk[1],AG.get(lk[2],''),hs])
        pats.setdefault((lidx[lk],sq),[]).append(g.dep.to_numpy())
    P=[]
    for (li,sq),L in pats.items():
        L.sort(key=lambda d:d[0]); first=[int(d[0]) for d in L]; rows={}; ix=[]
        for d in L:
            kk=tuple(int(x) for x in (d-d[0]))
            if kk not in rows: rows[kk]=len(rows)
            ix.append(rows[kk])
        P.append([li,list(sq),first,ix,[list(k) for k in rows]])
    raw=json.dumps({'v':1,'stops':S,'lines':lines,'pats':P},ensure_ascii=False,separators=(',',':')).encode()
    h=hashlib.sha1(raw).hexdigest()[:10]; gz=gzip.compress(raw,9,mtime=0); files[h]=gz
    for d in dates:
        if act[d]==sv: hash_of[d.strftime('%Y%m%d')]=h
    lg('day-set',si,'services',len(sv),'trips',sum(len(p[2]) for p in P),'stops',len(S),'gz MB',round(len(gz)/1e6,2),h)
for f in os.listdir(OUT):
    if f.startswith('transit_') and f.endswith('.json.gz') and f[8:-8] not in files: os.remove(OUT+f)
for h,gz in files.items(): open(OUT+f'transit_{h}.json.gz','wb').write(gz)
idx={'generated':dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),'feedEnd':int(cal.end_date.max()),'dates':hash_of}
open(OUT+'transit_index.json','w').write(json.dumps(idx))
lg('done',idx)
