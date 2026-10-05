import json, pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
NUM={'So':1,'A':2,'MS':3,'MR':4,'S':5,'Gt':6,'C':7}
rows=[]
for l in open('all.jsonl'):
    r=json.loads(l)
    if r['t']=='sr' and r['type']=='par':
        pc=f"P{NUM.get(r['corp'])}"
        own=[p['id'] for p in r['players'] if pc in p['companies']]
        rows.append(dict(gid=r['gid'],turn=r['turn'],pid=r['pid'],peir_owner=('self' if r['pid'] in own else ('opponent' if own else 'none'))))
X=pd.DataFrame(rows).drop_duplicates(['gid','turn','pid'])
d=pd.read_pickle('d_ss.pkl')
d=d.merge(X,on=['gid','turn','pid'],how='left')
d.loc[d.split==1,'peir_owner']='(split)'
print(d.peir_owner.value_counts())
d['grp']=d.peir_owner.fillna('none')
m=smf.ols('rel_final ~ C(grp,Treatment("(split)")) + rel_now + skill + C(ph) + C(n)',data=d).fit(cov_type='cluster',cov_kwds={'groups':d.gid})
for k in m.params.index:
    if 'grp' in k: print(f'start with PEIR share held by {k.split("T.")[1][:-1]:9s} vs split: {m.params[k]:+.3f} ({m.bse[k]:.3f})')
