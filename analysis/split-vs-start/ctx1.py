import json, collections, pandas as pd, numpy as np
pd.set_option('display.width',200)
ends={}; first_sr={}
splits=[]; starts=[]
for l in open('all.jsonl'):
    r=json.loads(l)
    if r['t']=='end' and r['status']=='finished' and not r.get('exception') and r['recorded']==r['engine_result']: ends[r['gid']]=r
    elif r['t']=='split': splits.append(r)
    elif r['t']=='sr' and r['type']=='par': starts.append(r)
rows=[]
def life(e,cid,from_turn):
    h=[x for x in e['hist'].get(cid,[])]
    pays=sum(1 for x in h if x[3]=='payout'); wh=sum(1 for x in h if x[3]=='withhold')
    rev=sum(x[2] or 0 for x in h)
    paid=sum((x[2] or 0) for x in h if x[3]=='payout')
    c=next(c for c in e['corps'] if c['id']==cid)
    return dict(ors=len(h),pays=pays,withholds=wh,rev=rev,paid_out=paid,final_price=c['price'],end_cash=c['cash'],end_trains=len(c['trains']))
for s in splits:
    e=ends.get(s['gid'])
    if not e or not s.get('branch_after'): continue
    b=s['branch_after']; d=life(e,b['id'],s['turn']); d.update(kind='branch',par=b['price'],start_cash=b['cash'],turn=s['turn'],phase=s['phase'],gid=s['gid'],nsr=e['turn'])
    rows.append(d)
for s in starts:
    e=ends.get(s['gid'])
    if not e: continue
    d=life(e,s['corp'],s['turn']); d.update(kind='started',par=s['price'],start_cash=10*s['price'],turn=s['turn'],phase=s['phase'],gid=s['gid'],nsr=e['turn'])
    rows.append(d)
L=pd.DataFrame(rows)
L['price_gain']=L.final_price-L.par
L['payrate']=L.pays/L.ors.replace(0,np.nan)
print(L.groupby('kind')[['par','start_cash','ors','pays','withholds','payrate','rev','paid_out','final_price','price_gain','end_cash']].median().round(2))
print(L.groupby('kind')[['ors','pays','rev','paid_out','price_gain','end_cash']].mean().round(1))
L['ph']=L.phase.map({'2H':'early H','3H':'early H','4H':'early H','5H':'5-6H','6H':'5-6H','2+':'2+','3+':'3+','4+':'4+','7':'7/D','D':'7/D'})
print('\nBy phase started (median):')
print(L.pivot_table(index='ph',columns='kind',values=['ors','paid_out','price_gain','end_cash'],aggfunc='median').round(0))
# stranded cash: all corps at game end
tot=[]; 
for e in ends.values():
    for c in e['corps']:
        if c['id']=='PEIR' or not (c['floated']): continue
        tot.append(dict(id=c['id'],branch=c['branch'],cash=c['cash']))
T=pd.DataFrame(tot); print('\nEnd-of-game treasury cash (counts for nobody):'); print(T.groupby('branch').cash.describe()[['count','mean','50%']])
L.to_pickle('L.pkl')
