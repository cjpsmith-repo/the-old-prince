import pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
cs=pd.read_pickle('cs.pkl')
d=cs[cs.choice!='neither'].copy()
d['split']=(d.choice=='split').astype(int)
d['gap10']=d.o_gap.clip(-20,100)/10
d['gap_le0']=(d.o_gap<=0).astype(int)
d['oth10']=d.o_others/10; d['pool10']=d.o_pool/10; d['my10']=d.o_my/10
d['notrain']=(d.o_trains==0).astype(int); d['multitrain']=(d.o_trains>=2).astype(int)
d['opcash100']=d.o_cash.clip(upper=800)/100
d['late']=d.ph.isin(['7/D']).astype(int)
d['cashpar']=(d.cash_now/d.maxpar).clip(upper=10)
d.to_pickle('d_ss.pkl')
for mods in ['gap10 + oth10 + pool10 + notrain + multitrain + opcash100 + cashpar + C(o_tokens)',
             'gap_le0 + oth10 + pool10 + notrain + opcash100',
             'oth10', 'pool10', 'gap_le0', 'notrain', 'opcash100']:
    f=f'rel_final ~ split*({mods}) + rel_now + skill + C(ph) + C(n)'
    m=smf.ols(f,data=d).fit(cov_type='cluster',cov_kwds={'groups':d.gid})
    print('\n',mods)
    for k in [k for k in m.params.index if k.startswith('split')]: print(f'  {k:28s} {m.params[k]:+.4f} (se {m.bse[k]:.4f}) p={m.pvalues[k]:.3f}')
