import pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
P=pd.read_pickle('P2.pkl'); cs=P[P.could_split].copy()
cs['gapb']=pd.cut(cs.o_gap,[-99,0,15,30,50,999],labels=['<=0','1-15','16-30','31-50','>50'])
cs['myb']=pd.cut(cs.o_my,[0,40,50,60,100],labels=['40','50','60','70+'])
cs['othb']=pd.cut(cs.o_others,[-1,10,20,30,40,100],labels=['0-10','20','30','40','50+'])
cs['poolb']=pd.cut(cs.o_pool,[-1,0,10,20,30,100],labels=['0','10','20','30','40+'])
cs['cashb']=pd.cut(cs.cash_now/cs.maxpar,[-1,2,4,6,99],labels=['<2xpar','2-4x','4-6x','6x+'])
cs['trainb']=cs.o_trains.clip(upper=3)
cs['tokb']=cs.o_tokens.clip(upper=4)
cs['pkind']=np.select([cs.o_ml.astype(bool),cs.o_sl.astype(bool),cs.o_branch.astype(bool)],['Mainline','Shortline','Branch'],'PEIR co')
cs['opcashb']=pd.cut(cs.o_cash,[-1,100,250,400,9999],labels=['<100','100-250','250-400','400+'])
cs.to_pickle('cs.pkl')
def eff(df):
    out={}
    for ref in ['neither','start']:
        try:
            m=smf.ols(f'rel_final ~ C(choice, Treatment("{ref}")) + rel_now + skill + C(ph) + C(n)',data=df).fit(cov_type='cluster',cov_kwds={'groups':df.gid})
            k=[x for x in m.params.index if 'T.split' in x][0]
            out[ref]=(m.params[k],m.bse[k])
            if ref=='neither':
                k2=[x for x in m.params.index if 'T.start' in x][0]; out['start_vs_neither']=(m.params[k2],m.bse[k2])
        except Exception as e: out[ref]=(np.nan,np.nan)
    return out
def table(var,label):
    print(f'\n== {label}')
    print(f'{"bin":10s} {"N":>5s} {"#split":>6s} {"#start":>6s} | {"split-neither":>15s} | {"start-neither":>15s} | {"split-start":>15s}')
    for b,g in cs.groupby(var,observed=True):
        if len(g)<120: continue
        e=eff(g); f=lambda t:f'{t[0]:+.3f} ({t[1]:.3f})'
        print(f'{str(b):10s} {len(g):5d} {(g.choice=="split").sum():6d} {(g.choice=="start").sum():6d} | {f(e["neither"]):>15s} | {f(e["start_vs_neither"]):>15s} | {f(e["start"]):>15s}')
table('gapb','Parent price minus best available branch par ($)')
table('myb','Your % of the parent')
table('othb','% of parent held by other players')
table('poolb','% of parent in the open market')
table('cashb','Your cash, in multiples of max par')
table('trainb','Parent trains')
table('tokb','Parent stations on map')
table('opcashb','Parent treasury cash')
table('pkind','Parent type')
table('ph','Phase')
