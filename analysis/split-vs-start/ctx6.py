import json, collections, pandas as pd, numpy as np
pd.set_option('display.width',200)
games=collections.defaultdict(list)
for l in open('all.jsonl'):
    r=json.loads(l)
    if r['t'] in ('split','round','end'): games[r['gid']].append(r)
X=pd.read_pickle('ctrl.pkl'); rows=[]
for gid,rs in games.items():
    e=rs[-1]
    if e['t']!='end' or e['status']!='finished' or e.get('exception') or e['recorded']!=e['engine_result']: continue
    for i,s in enumerate(rs):
        if s['t']!='split' or not s['branch_after']: continue
        me=s['pid']; br=s['branch_after']['id']; par=s['parent_before']['id']
        snap=next((r for r in rs[i+1:] if r['t']=='round' and r['kind']=='Operating'),None)
        if not snap: continue
        c={x['id']:x for x in snap['corps']}
        if br not in c: continue
        h=c[br]['holders']; hp=c[par]['holders'] if par in c else {}
        rows.append(dict(gid=gid,turn=s['turn'],parent=par,branch_cash0=s['branch_after']['cash'],
          free_to_opp=sum(v for k,v in s['branch_after']['holders'].items() if k not in (me,'pool','-1')),
          me_branch=h.get(me,0),opp_branch=sum(v for k,v in h.items() if k not in (me,'pool','-1',br)),
          pool_branch=h.get('pool',0),me_parent=hp.get(me,0),
          opp_parent=sum(v for k,v in hp.items() if k not in (me,'pool','-1',par)),treas_parent=hp.get(par,0)))
B=pd.DataFrame(rows).merge(X[['gid','turn','parent','ofb']],on=['gid','turn','parent'])
print(B.groupby('ofb',observed=True)[['branch_cash0','free_to_opp','me_branch','opp_branch','pool_branch','me_parent','opp_parent','treas_parent']].mean().round(1).T)
