import json, pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
ends={}; splits=[]
for l in open('all.jsonl'):
    r=json.loads(l)
    if r['t']=='end' and r['status']=='finished' and not r.get('exception') and r['recorded']==r['engine_result']: ends[r['gid']]=r
    elif r['t']=='split': splits.append(r)
sk=pd.read_pickle('skill.pkl').set_index(['gid','pid']).skill
rows=[]
for s in splits:
    e=ends.get(s['gid']); 
    if not e: continue
    fin=e['engine_result']; tot=sum(fin.values()); n=len(fin)
    vals={p['id']:p['value'] for p in s['players_before']}; vt=sum(vals.values())
    after={p['id']:p for p in s['players_after']}
    par=s['parent_before']['id']
    for p in s['players_before']:
        if p['id']==s['pid']: continue
        rows.append(dict(gid=s['gid'],pid=p['id'],held=p['hold'].get(par,0),n=n,rel_now=vals[p['id']]/vt*n,
            rel_final=fin[p['id']]/tot*n,dval=after[p['id']]['value']-p['value'],phase=s['phase'],
            skill=sk.get((s['gid'],p['id']),1.0)))
O=pd.DataFrame(rows)
print('opponents at splits:',len(O)); print(O.groupby('held').agg(N=('gid','size'),dval=('dval','median'),rel_final=('rel_final','mean'),rel_now=('rel_now','mean')).round(3))
m=smf.ols('rel_final ~ I(held/10) + rel_now + skill + C(phase) + C(n)',data=O).fit(cov_type='cluster',cov_kwds={'groups':O.gid})
print('effect per 10% of parent held by an opponent at the split:', round(m.params['I(held / 10)'],4), 'se', round(m.bse['I(held / 10)'],4))
