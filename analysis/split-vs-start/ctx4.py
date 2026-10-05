import json, collections, pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
games=collections.defaultdict(list)
for l in open('all.jsonl'):
    r=json.loads(l)
    if r['t'] in ('split','round','end'): games[r['gid']].append(r)
SP=pd.read_pickle('SP2.pkl').set_index(['gid','turn','parent'])
rows=[]
for gid,rs in games.items():
    e=rs[-1]
    if e['t']!='end' or e['status']!='finished' or e.get('exception') or e['recorded']!=e['engine_result']: continue
    for i,s in enumerate(rs):
        if s['t']!='split': continue
        par=s['parent_before']['id']; br=(s['branch_after'] or {}).get('id'); me=s['pid']
        pa=s['parent_after']['holders']
        opp_after=max([v for k,v in pa.items() if k not in (me,'pool',par,'-1')] or [0])
        owners_p=[]; owners_b=[]
        for r in rs[i+1:]:
            if r['t']=='round' and r['kind']=='Stock':
                c={x['id']:x for x in r['corps']}
                if par in c and not c[par]['closed']: owners_p.append(c[par]['owner'])
                if br in c: owners_b.append(c[br]['owner'])
        cp={x['id']:x for x in e['corps']}
        ub_owner=None
        lost_p=any(o not in (me,'-1') for o in owners_p)
        nonme=sum(v for k,v in s['parent_before']['holders'].items() if k not in (me,par,'-1'))
        oth=sum(v for k,v in s['parent_before']['holders'].items() if k not in (me,par,'pool','-1'))
        rows.append(dict(gid=gid,turn=s['turn'],parent=par,me_after=pa.get(me,0),opp_max_after=opp_after,
            lost_parent=lost_p,lost_branch=any(o not in (me,'-1') for o in owners_b),
            othfrac=oth/nonme if nonme else 0.5,final_parent_owner_me=cp[par]['owner']==me))
X=pd.DataFrame(rows)
X['ofb']=pd.cut(X.othfrac,[-0.01,0.34,0.67,1.01],labels=['mostly market','mixed','mostly players'])
X['threat']=X.opp_max_after>=X.me_after
print(X.groupby('ofb',observed=True).agg(N=('gid','size'),my_parent_pct_after=('me_after','mean'),
   top_opp_pct_after=('opp_max_after','mean'),opp_ties_or_beats_me=('threat','mean'),lost_parent_later=('lost_parent','mean'),
   lost_branch_later=('lost_branch','mean')).round(3))
print('\nlost parent later, by whether an opponent tied/beat my parent stake right after split:')
print(X.groupby('threat').lost_parent.agg(['size','mean']).round(3))
X.to_pickle('ctrl.pkl')
