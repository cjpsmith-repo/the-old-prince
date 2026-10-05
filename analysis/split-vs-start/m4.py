import pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
d=pd.read_pickle('d_ss.pkl')
d['nonme']=d.o_others+d.o_pool
d['othfrac']=np.where(d.nonme>0,d.o_others/d.nonme.replace(0,np.nan),0.5)
d['othfracb']=pd.cut(d.othfrac,[-0.01,0.34,0.67,1.01],labels=['mostly market','mixed','mostly players'])
m=smf.ols('rel_final ~ split*(othfrac + notrain + opcash100) + rel_now + skill + C(ph) + C(n)',data=d).fit(cov_type='cluster',cov_kwds={'groups':d.gid})
for k in [k for k in m.params.index if k.startswith('split')]: print(f'  {k:28s} {m.params[k]:+.4f} (se {m.bse[k]:.4f}) p={m.pvalues[k]:.3f}')
print()
for b,g in d.groupby('othfracb',observed=True):
    mm=smf.ols('rel_final ~ split + rel_now + skill + C(ph) + C(n)',data=g).fit(cov_type='cluster',cov_kwds={'groups':g.gid})
    print(f'{b:15s} N={len(g):4d} splits={g.split.sum():4d} split-start {mm.params["split"]:+.3f} ({mm.bse["split"]:.3f}) win split {g[g.split==1].win.mean():.3f} start {g[g.split==0].win.mean():.3f}')
# timing: slot vs neither by SRs remaining
cs=pd.read_pickle('cs.pkl'); cs['left']=cs.nsr-cs.turn
cs['leftb']=pd.cut(cs.left,[-1,0,1,2,3,99],labels=['last SR','1 more','2 more','3 more','4+ more'])
cs['took']=(cs.choice!='neither').astype(int)
print('\nTaking the slot vs neither, by stock rounds remaining')
for b,g in cs.groupby('leftb',observed=True):
    mm=smf.ols('rel_final ~ took + rel_now + skill + C(n)',data=g).fit(cov_type='cluster',cov_kwds={'groups':g.gid})
    ms=smf.ols('rel_final ~ C(choice,Treatment("start")) + rel_now + skill + C(n)',data=g[g.choice!='neither']).fit(cov_type='cluster',cov_kwds={'groups':g[g.choice!='neither'].gid})
    k=[x for x in ms.params.index if 'split' in x][0]
    print(f'{b:9s} N={len(g):4d} took={g.took.sum():4d} took-neither {mm.params["took"]:+.3f} ({mm.bse["took"]:.3f}) | split-start {ms.params[k]:+.3f} ({ms.bse[k]:.3f})')
