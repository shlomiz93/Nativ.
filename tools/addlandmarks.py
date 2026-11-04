# Adds named transport hubs / junctions / malls / landmarks that the first POI whitelist dropped (airport, bus & train stations, interchanges, malls tagged as landuse...).
import osmium, json, gzip, math, collections, time
F='/home/claude/osm/israel.osm.pbf'
KX=111320*math.cos(32.0865*math.pi/180); KY=110540
S='/home/claude/nav/d/search.json.gz'
j=json.load(gzip.open(S,'rt',encoding='utf8'))
have=set((p[3],p[1]//150,p[2]//150) for p in j['poi'])
g=collections.defaultdict(list)
for p in j['poi']: g[(int(p[1]//500),int(p[2]//500))].append((p[1],p[2],p[4]))
for s in j['streets']: g[(int(s[2]//500),int(s[3]//500))].append((s[2],s[3],s[1]))
def city(x,y):
    gx,gy=int(x//500),int(y//500);best=None;bd=1e9
    for a in(-2,-1,0,1,2):
        for b in(-2,-1,0,1,2):
            for X,Y,c in g.get((gx+a,gy+b),[]):
                d=(X-x)**2+(Y-y)**2
                if d<bd: bd=d;best=c
    return best if bd<3000**2 else None
def kind(t,isnode):
    nm=t.get('name:he') or t.get('name') or ''
    if t.get('aeroway') in('aerodrome','terminal','heliport'): return 'נמל תעופה' if t.get('aeroway')!='heliport' else 'מסוק'
    if t.get('landuse')=='port' or t.get('industrial')=='port' or t.get('harbour')=='yes' or t.get('seamark:type')=='harbour': return 'נמל'
    if t.get('amenity')=='bus_station': return 'תחנה מרכזית'
    if t.get('railway') in('station','halt') and t.get('station')!='subway' or t.get('public_transport')=='station' and t.get('train')=='yes': return 'תחנת רכבת'
    if t.get('railway')=='tram_stop' and False: return None
    if t.get('highway')=='motorway_junction' or t.get('junction') in('yes',) or (isnode and (nm.startswith('צומת ') or nm.startswith('מחלף '))): return 'צומת/מחלף'
    if t.get('place') in('square',) : return 'כיכר'
    if 'קניון' in nm or t.get('shop')=='mall' : return 'קניון'
    if t.get('amenity') in('marketplace',) : return 'שוק'
    if t.get('amenity')=='courthouse': return 'בית משפט'
    if t.get('historic') in('castle','fort','monument','ruins','archaeological_site','memorial') and nm: return 'אתר היסטורי'
    if t.get('tourism') in('attraction','museum','zoo','theme_park','viewpoint','information') and nm: return 'אתר'
    if t.get('leisure') in('marina','beach_resort','stadium'): return 'מרינה/אצטדיון'
    if t.get('natural')=='beach': return 'חוף'
    if t.get('man_made') in('lighthouse','tower') and nm: return 'ציון דרך'
    if t.get('amenity') in('university','college') and nm: return 'אוניברסיטה/מכללה'
    if t.get('amenity')=='hospital' and nm: return 'בית חולים'
    if t.get('office')=='government' and nm: return 'משרד ממשלתי'
    return None
new=[];seen=set();cnt=collections.Counter()
fp=osmium.FileProcessor(F).with_locations().with_areas().with_filter(osmium.filter.KeyFilter('aeroway','amenity','railway','public_transport','highway','junction','place','shop','historic','tourism','leisure','natural','man_made','office','landuse','industrial','harbour','seamark:type','name'))
for o in fp:
    if not (o.is_node() or o.is_area()): continue
    t=o.tags; nm=t.get('name:he') or t.get('name')
    if not nm or not any('֐'<=c<='׿' for c in nm): continue
    k=kind(t,o.is_node())
    if not k: continue
    if o.is_node() and t.get('highway') and t.get('highway')!='motorway_junction' and not nm.startswith(('צומת ','מחלף ')): continue
    try:
        if o.is_node(): la,lo=o.location.lat,o.location.lon
        else:
            ring=next(o.outer_rings()); la=sum(n.lat for n in ring)/len(ring); lo=sum(n.lon for n in ring)/len(ring)
    except Exception: continue
    x=round((lo-34.815)*KX); y=round((la-32.0865)*KY)
    key=(nm,x//150,y//150)
    if key in seen or key in have: continue
    seen.add(key); c=city(x,y)
    pre={'תחנת רכבת':'תחנת רכבת','תחנה מרכזית':'תחנה מרכזית','נמל תעופה':'נמל תעופה','נמל':'נמל','קניון':'קניון'}.get(k)
    if pre and pre.split()[-1] not in nm and not (pre=='תחנת רכבת' and 'רכבת' in nm) and not (pre=='תחנה מרכזית' and 'מרכזית' in nm): nm=pre+' '+nm
    if c is None: continue
    new.append(['public',x,y,nm,c,f"{math.floor(x/4000)}_{math.floor(y/4000)}",k]); cnt[k]+=1
print(len(new),cnt.most_common())
j['poi']=j['poi']+new; j['_landmarks']=1
gzip.open(S,'wb',9).write(json.dumps(j,ensure_ascii=False,separators=(',',':')).encode('utf8'))
open('/home/claude/nav/d/ver.txt','w').write(str(int(time.time())))
print('done')
