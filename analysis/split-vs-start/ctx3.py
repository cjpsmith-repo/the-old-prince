import json, pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
hist={}
for l in open('all.jsonl'):
    if l.startswith('{"t":"end"'):
        r=json.loads(l)
        if r.get('hist'): hist[r['gid']]=r['hist']
d=pd.read_pickle('d_ss.pkl')
d['nonme']=d.o_others+d.o_pool
d['othfrac']=np.where(d.nonme>0,d.o_others/d.nonme.replace(0,np.nan),0.5)
def prior(row):
    h=[x for x in hist[row.gid].get(row.o_id,[]) if x[0]<row.turn]
    last=h[-2:]
    return pd.Series(dict(last_rev=np.mean([x[2] or 0 for x in last]) if last else np.nan,
        last_pay=np.mean([x[3]=='payout' for x in last]) if last else np.nan))
d=pd.concat([d,d.apply(prior,axis=1)],axis=1)
d['ofb']=pd.cut(d.othfrac,[-0.01,0.34,0.67,1.01],labels=['mostly market','mixed','mostly players'])
print(d.groupby('ofb',observed=True)[['o_price','o_gap','last_rev','last_pay','o_cash','o_trains','o_my']].mean().round(2))
base='rel_final ~ split*(othfrac + notrain + opcash100) + rel_now + skill + C(ph) + C(n)'
for extra in ['', ' + split*I(last_rev/100)', ' + split*last_pay', ' + split*gap10', ' + split*(I(last_rev/100)+last_pay+gap10)']:
    dd=d.dropna(subset=['last_rev','last_pay'])
    m=smf.ols(base+extra,data=dd).fit(cov_type='cluster',cov_kwds={'groups':dd.gid})
    print(f'{extra or "(base)":45s}', '  '.join(f'{k.replace("split:","")}={m.params[k]:+.3f}({m.bse[k]:.3f})' for k in m.params.index if k.startswith('split:')))
