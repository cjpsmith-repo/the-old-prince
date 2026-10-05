import pandas as pd, numpy as np, statsmodels.formula.api as smf, json, warnings; warnings.filterwarnings('ignore')
d=pd.read_pickle('d_ss.pkl')
d['nonme']=d.o_others+d.o_pool
d['othfrac']=np.where(d.nonme>0,d.o_others/d.nonme.replace(0,np.nan),0.5)
cr={}
for l in open('all.jsonl'):
    if '"t": "end"' in l[:20] or '"t":"end"' in l[:20]:
        r=json.loads(l); cr[r['gid']]=r.get('created_at')
d['created']=d.gid.map(cr); med=d.created.median(); d['era']=np.where(d.created<med,'older half','newer half')
f='{y} ~ split*(othfrac + notrain + opcash100) + rel_now + skill + C(ph) + C(n)'
def show(df,label,y='rel_final'):
    m=smf.ols(f.format(y=y),data=df).fit(cov_type='cluster',cov_kwds={'groups':df.gid})
    print(f'{label:22s} N={len(df):4d} ' + '  '.join(f'{k.replace("split:","")}={m.params[k]:+.3f}({m.bse[k]:.3f})' for k in m.params.index if k.startswith('split')))
show(d,'all'); show(d,'all, win outcome','win')
for n,g in d.groupby('n'): show(g.drop(columns=[]),f'{n} players')
for e,g in d.groupby('era'): show(g,e)
# with player fixed effects instead of skill
m=smf.ols('rel_final ~ split*(othfrac + notrain + opcash100) + rel_now + C(ph) + C(n) + C(pid)',data=d).fit(cov_type='cluster',cov_kwds={'groups':d.gid})
print('player fixed effects    '+'  '.join(f'{k.replace("split:","")}={m.params[k]:+.3f}({m.bse[k]:.3f})' for k in m.params.index if k.startswith('split')))
