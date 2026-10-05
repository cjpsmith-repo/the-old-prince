import json, glob, pandas as pd, numpy as np
pd.set_option('display.width',200)
rs=[json.loads(l) for f in sorted(glob.glob('cf[0-9].jsonl')) for l in open(f)]
ok={r['gid'] for r in rs if r['t']=='end2' and r.get('match') and not r.get('exception')}
bad=[r for r in rs if r['t']=='end2' and not (r.get('match') and not r.get('exception'))]
print('split games replayed ok:',len(ok),' failed:',len(bad))
C=pd.DataFrame([r for r in rs if r['t']=='cf' and r['gid'] in ok])
C=C[C.opt_actual.notna()&(C.timed_out==False)]
C['match']=C.opt_actual==C.ran
print('parent runs evaluated:',len(C),' optimiser == revenue actually run:',C.match.mean().round(3))
C['loss']=C.opt_cf-C.opt_actual
C['lossp']=C.loss/C.opt_cf.replace(0,np.nan)
C['anyblock']=C.blocked.apply(any)
def summ(g): return pd.Series(dict(N=len(g),share_hurt=(g.loss>0).mean(),median_loss=g.loss.median(),mean_loss=g.loss.mean(),
    mean_loss_pct=g.lossp.mean(),loss_if_hurt=g.loss[g.loss>0].median()))
print('\nAll runs'); print(summ(C).round(3))
print('\nBy run number after the split'); print(C.groupby('eval').apply(summ).round(3))
print('\nBy stations given away'); print(C.groupby('moved').apply(summ).round(3))
print('\nBy whether the given-away city now blocks the parent'); print(C.groupby('anyblock').apply(summ).round(3))
C['ph']=C.split_phase.map({'2H':'H','3H':'H','4H':'H','5H':'5-6H','6H':'5-6H','2+':'2+','3+':'3+','4+':'4+','7':'7/D','D':'7/D'})
print('\nBy phase of split'); print(C.groupby('ph').apply(summ).round(3))
C.to_pickle('C.pkl')
T=pd.DataFrame([r for r in rs if r['t']=='tsale' and r['gid'] in ok])
T['same_owner']=T.buyer_owner==T.seller_owner
T['pair']=np.where(T.buyer_branch|T.seller_branch,'involves a branch','no branch')
print('\nTrain sales between companies:',len(T))
print(T.groupby(['same_owner','pair']).agg(N=('gid','size'),median_price=('price','median'),share_at_1=('price',lambda s:(s<=1).mean()),
   share_full_cash=('price',lambda s: np.nan)).round(2))
T['price_vs_cash']=T.price/T.buyer_cash.replace(0,np.nan)
print(T[T.same_owner].groupby('pair').price_vs_cash.describe()[['count','25%','50%','75%']].round(2))
T.to_pickle('T.pkl')
