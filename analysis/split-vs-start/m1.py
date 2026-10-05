import pandas as pd, numpy as np, statsmodels.formula.api as smf
pd.set_option('display.width',200)
P=pd.read_pickle('P.pkl').merge(pd.read_pickle('skill.pkl'),on=['gid','pid'])
P['rel_final']=P.final_share*P.n; P['rel_now']=P.share_now*P.n
P['choice']=np.select([P.did_split,P.did_start],['split','start'],'neither')
P['early']=P.phase.isin(['2H','3H','4H','5H','6H'])
P['ph']=P.phase.map({'2H':'H','3H':'H','4H':'H','5H':'5-6H','6H':'5-6H','2+':'2+','3+':'3+','4+':'4+','7':'7/D','D':'7/D'})
P.to_pickle('P2.pkl')
cs=P[P.could_split]
print('player-SRs with a split option:',len(cs)); print(cs.choice.value_counts())
print(cs.groupby('choice')[['rel_now','rel_final','win','skill']].mean())
def fit(df,label,y='rel_final'):
    m=smf.ols(f'{y} ~ C(choice, Treatment("neither")) + rel_now + skill + C(ph) + C(n)',data=df).fit(cov_type='cluster',cov_kwds={'groups':df.gid})
    out=m.params.filter(like='choice'); se=m.bse.filter(like='choice')
    print(f'\n{label} [{y}] N={len(df)}')
    for k in out.index: print(f'  {k.split("T.")[-1][:-1]:8s} {out[k]:+.3f}  (se {se[k]:.3f})')
fit(cs,'All split opportunities'); fit(cs,'All split opportunities',y='win')
both=cs[cs.could_start]; fit(both,'Could split AND could start'); fit(both,'Could split AND could start','win')
for ph,g in cs.groupby('ph'):
    if len(g)>200: fit(g,f'phase {ph}')
