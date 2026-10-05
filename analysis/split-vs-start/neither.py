import json, collections, pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
P=pd.read_pickle('P2.pkl')
# slots filled at the start of each SR
filled={}
for l in open('all.jsonl'):
    if not l.startswith('{"t":"round"'): continue
    r=json.loads(l)
    if r['kind']=='Stock': filled.setdefault((r['gid'],r['turn']), sum(1 for tr in r['tranches'][1:] for c in tr if c))
P['filled']=[filled.get((g,t),np.nan) for g,t in zip(P.gid,P.turn)]
A=P[(P.could_split|P.could_start)].copy()
A['took']=(A.did_split|A.did_start).astype(int)
A['left']=6-A.filled
A['leftb']=A.left.clip(upper=3)
A['pos']=pd.cut(A.rel_now,[0,0.9,1.1,9],labels=['behind','middle','ahead'])
A['cashx']=pd.cut(A.cash_now/A.maxpar.fillna(65),[-1,3,6,99],labels=['<3x par','3-6x','6x+']) if 'maxpar' in A else None
MAXPAR={'2H':80,'3H':80,'4H':80,'5H':74,'6H':74,'2+':74,'3+':65,'4+':65,'7':58,'D':58}
A['cashx']=pd.cut(A.cash_now/A.phase.map(MAXPAR),[-1,3,6,99],labels=['<3x par','3-6x','6x+'])
print('decisions with an open slot:',len(A),' took:',A.took.mean().round(3))
def eff(g):
    m=smf.ols('rel_final ~ took + rel_now + skill + C(ph) + C(n)',data=g).fit(cov_type='cluster',cov_kwds={'groups':g.gid})
    return f"{m.params['took']:+.3f} ({m.bse['took']:.3f})  N={len(g)} took={g.took.sum()}"
for v in ['ph','leftb','pos','cashx','n']:
    print('\n',v)
    for b,g in A.groupby(v,observed=True):
        if len(g)>150: print(f'  {str(b):10s}', eff(g))
