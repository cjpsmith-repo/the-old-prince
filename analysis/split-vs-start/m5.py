import pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
SP=pd.read_pickle('SP.pkl'); sk=pd.read_pickle('skill.pkl')
SP=SP.merge(sk,on=['gid','pid'])
MAXPAR={'2H':80,'3H':80,'4H':80,'5H':74,'6H':74,'2+':74,'3+':65,'4+':65,'7':58,'D':58}
SP['maxpar']=SP.phase.map(MAXPAR); SP['par_below_max']=(SP.par<SP.maxpar).astype(int)
SP['rel_final']=SP.final_share*SP.n; SP['rel_now']=SP.share_before*SP.n
SP['ph']=SP.phase.map({'2H':'H','3H':'H','4H':'H','5H':'5-6H','6H':'5-6H','2+':'2+','3+':'3+','4+':'4+','7':'7/D','D':'7/D'})
SP['gave_train']=(SP.trains_moved>0).astype(int); SP['gave_cash']=(SP.cash_moved>0).astype(int)
SP['extra_station']=(SP.tokens_moved>1).astype(int)
SP['float_delay']=SP.branch_first_or-SP.turn
SP['notrain']=(SP.parent_trains==0).astype(int)
print('Branch float timing (ORs of same set = 0):'); print(SP.float_delay.value_counts(dropna=False).sort_index())
print('\nBranch capital vs other players\' holdings in parent:'); print(SP.groupby('others_pct').agg(N=('gid','size'),branch_cash=('branch_cash','median'),dvalue=('dvalue','median'),rel=('rel_final','mean'),delay=('float_delay','mean')).round(2))
print('\nImmediate net-worth change vs gap:'); SP['gapb']=pd.cut(SP.gap,[-99,0,15,30,50,999]); print(SP.groupby('gapb',observed=True).dvalue.describe()[['count','mean','50%']])
m=smf.ols('rel_final ~ gave_train + gave_cash + extra_station + par_below_max + C(float_delay.fillna(9).clip(upper=2)) + notrain + rel_now + skill + C(ph) + C(n)',data=SP).fit(cov_type='cluster',cov_kwds={'groups':SP.gid})
print(); 
for k in m.params.index:
    if k.startswith(('gave','extra','par_','C(float','notrain')): print(f'  {k:50s} {m.params[k]:+.4f} (se {m.bse[k]:.4f}) p={m.pvalues[k]:.3f}')
print(SP[['gave_train','gave_cash','extra_station','par_below_max']].mean())
SP.to_pickle('SP2.pkl')
