import pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
CF=pd.read_pickle('C.pkl'); SP=pd.read_pickle('SP2.pkl')
agg=CF.groupby(['gid','parent','split_turn']).agg(lossp=('lossp','mean'),block=('anyblock','max'),moved=('moved','max')).reset_index()
X=SP.merge(agg,left_on=['gid','parent','turn'],right_on=['gid','parent','split_turn'])
X['block']=X.block.astype(int)
print('splits matched:',len(X),' share leaving parent blocked:',X.block.mean().round(3))
for f in ['block','I(lossp*10)']:
    m=smf.ols(f'rel_final ~ {f} + rel_now + skill + C(ph) + C(n)',data=X).fit(cov_type='cluster',cov_kwds={'groups':X.gid})
    k=[x for x in m.params.index if x.startswith(f.split('(')[0])][0]
    print(f, round(m.params[k],4), 'se', round(m.bse[k],4))
X['lb']=pd.cut(X.lossp.fillna(0),[-0.01,0,0.05,0.15,1.01],labels=['none','<5%','5-15%','>15%'])
print(X.lb.value_counts().sort_index())
m=smf.ols('rel_final ~ C(lb) + rel_now + skill + C(ph) + C(n)',data=X).fit(cov_type='cluster',cov_kwds={'groups':X.gid})
for k in m.params.index:
    if 'lb' in k: print(k, round(m.params[k],3), 'se', round(m.bse[k],3))
