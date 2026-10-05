import json, collections, pandas as pd, numpy as np
pd.set_option('display.width',200)
games=collections.defaultdict(list)
for l in open('all.jsonl'):
    r=json.loads(l)
    if r['t'] in ('split','round','end'): games[r['gid']].append(r)
X=pd.read_pickle('ctrl.pkl'); SP=pd.read_pickle('SP2.pkl')
rows=[]
for gid,rs in games.items():
    e=rs[-1]
    if e['t']!='end' or e['status']!='finished' or e.get('exception') or e['recorded']!=e['engine_result']: continue
    for i,s in enumerate(rs):
        if s['t']!='split': continue
        me=s['pid']; par=s['parent_before']['id']; br=(s['branch_after'] or {}).get('id')
        for which,cid in (('parent',par),('branch',br)):
            prev_pct=None; ev=None
            for r in rs[i+1:]:
                if r['t']=='round' and r['kind']=='Stock':
                    c={x['id']:x for x in r['corps']}
                    if cid not in c or c[cid]['closed']: break
                    mine=c[cid]['holders'].get(me,0)
                    if c[cid]['owner'] not in (me,'-1'):
                        ev='dumped' if prev_pct is not None and mine<prev_pct else 'taken over'
                        break
                    prev_pct=mine
            rows.append(dict(gid=gid,turn=s['turn'],parent=par,which=which,event=ev or 'kept'))
E=pd.DataFrame(rows).merge(X[['gid','turn','parent','ofb']],on=['gid','turn','parent'])
print(pd.crosstab([E.which,E.ofb],E.event,normalize='index').round(3))
print(pd.crosstab([E.which,E.ofb],E.event))
