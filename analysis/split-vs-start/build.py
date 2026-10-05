import json, collections, pandas as pd, numpy as np
recs=collections.defaultdict(list)
for l in open('all.jsonl'):
    r=json.loads(l); recs[r['gid']].append(r)
good={}
for gid,rs in recs.items():
    e=rs[-1]
    if e['t']=='end' and e['status']=='finished' and not e['exception'] and e['recorded']==e['engine_result']:
        good[gid]=rs
print('games',len(good))


MAXPAR={'2H':80,'3H':80,'4H':80,'5H':74,'6H':74,'2+':74,'3+':65,'4+':65,'7':58,'D':58}
def opt_feats(a,pid):
    opts=a['split_opts']
    if not opts: return {}
    if a['did_split']:
        cand=[o for o in opts if o['id']==a['did_split']] or opts
    else:
        cand=opts
    o=sorted(cand,key=lambda o:(-o['my_pct'],o['price']))[0]
    mp=MAXPAR.get(a['phase'],65)
    return dict(o_id=o['id'],o_price=o['price'],o_gap=o['price']-mp,o_my=o['my_pct'],
        o_others=sum(v for k,v in o['holders'].items() if k not in (pid,'pool',o['id'])),
        o_pool=o['holders'].get('pool',0),o_tokens=o['tokens'],o_cash=o['cash'],o_trains=len(o['trains']),
        o_ml=o['ml'],o_sl=o['sl'],o_branch=o['branch'],o_operated=o['operated'],maxpar=mp,
        n_opts=len({x['id'] for x in opts}))

def shares(vals):
    s=sum(vals.values()); return {k:v/s for k,v in vals.items()}

prow=[]; srow=[]; strow=[]
for gid,rs in good.items():
    e=rs[-1]; n=e['nplayers']; final={k:v for k,v in e['engine_result'].items()}
    fshare=shares(final)
    order=sorted(final,key=lambda k:-final[k]); rank={p:i+1 for i,p in enumerate(order)}
    winner=order[0]
    hist=e['hist']; endcorp={c['id']:c for c in e['corps']}
    nsr=max([r['turn'] for r in rs if r['t']=='sr'] or [0])
    # SR-start snapshots
    srsnap={}
    for r in rs:
        if r['t']=='round' and r['kind']=='Stock': srsnap.setdefault(r['turn'], r)
    # player-SR aggregates
    agg={}
    for r in rs:
        if r['t']!='sr': continue
        key=(r['turn'],r['pid'])
        a=agg.setdefault(key,dict(could_split=False,could_start=False,did_split=None,did_start=None,phase=r['phase'],
              split_opts=[],first=r))
        if r['splittable']: a['could_split']=True; a['split_opts'].extend(r['splittable'])
        if r['tranch'] and r['parable']: a['could_start']=True
        if r['type']=='split': a['did_split']=r['corp']; a['split_rec']=r
        if r['type']=='par': a['did_start']=r['corp']; a['start_price']=r['price']; a['start_rec']=r
    for (turn,pid),a in agg.items():
        snap=srsnap.get(turn)
        vals={p['id']:p['value'] for p in (snap['players'] if snap else a['first']['players'])}
        sh=shares(vals)
        prow.append(dict(gid=gid,n=n,turn=turn,nsr=nsr,pid=pid,phase=a['phase'],could_split=a['could_split'],
            could_start=a['could_start'],did_split=a['did_split'] is not None,did_start=a['did_start'] is not None,
            share_now=sh.get(pid,np.nan),final_share=fshare[pid],rank=rank[pid],win=int(pid==winner),
            best_opt_pct=max([o['my_pct'] for o in a['split_opts']] or [np.nan]),
            cash_now=next(p['cash'] for p in a['first']['players'] if p['id']==pid),
            value_now=next(p['value'] for p in a['first']['players'] if p['id']==pid),
            **opt_feats(a,pid)))
    # split records
    for r in rs:
        if r['t']!='split': continue
        pb=r['parent_before']; pa=r['parent_after']; ba=r['branch_after'] or {}
        mv=r['moves']
        par=next((m['choice'] for m in mv if m['step']==3),None)
        parp=ba.get('price') if ba else (int(par.split(',')[0]) if par else None)
        cashmv=next((int(m['choice']) for m in mv if m['step']==5),0)
        before={p['id']:p for p in r['players_before']}; after={p['id']:p for p in r['players_after']}
        pid=r['pid']
        others_parent=sum(v for k,v in pb['holders'].items() if k not in (pid,'pool',pb['id']))
        srow.append(dict(gid=gid,n=n,turn=r['turn'],nsr=nsr,phase=r['phase'],pid=pid,parent=pb['id'],branch=ba.get('id'),
            parent_ml=pb['ml'],parent_sl=pb['sl'],parent_is_branch=pb['branch'],
            parent_price=pb['price'],par=parp,gap=(pb['price']-parp) if parp else None,
            my_pct=pb['holders'].get(pid,0),others_pct=others_parent,pool_pct=pb['holders'].get('pool',0),
            parent_tokens=pb['tokens'],tokens_moved=pb['tokens']-pa['tokens'],
            parent_cash=pb['cash'],cash_moved=cashmv,parent_trains=len(pb['trains']),
            trains_moved=len(pb['trains'])-len(pa['trains']),branch_cash=ba.get('cash'),
            branch_pool_pct=ba.get('holders',{}).get('pool'),
            dvalue=after[pid]['value']-before[pid]['value'],value_before=before[pid]['value'],
            share_before=shares({k:v['value'] for k,v in before.items()})[pid],
            final_share=fshare[pid],rank=rank[pid],win=int(pid==winner),
            parent_operated=pb['operated'],
            branch_final_price=endcorp.get(ba.get('id'),{}).get('price'),
            branch_ors=len(hist.get(ba.get('id'),[])),
            branch_rev=sum(h[2] or 0 for h in hist.get(ba.get('id'),[])),
            branch_first_or=min([h[0] for h in hist.get(ba.get('id'),[])] or [None]),parent_rev_after=sum(h[2] or 0 for h in hist.get(pb['id'],[]) if h[0]>=r['turn']),parent_ors_after=len([h for h in hist.get(pb['id'],[]) if h[0]>=r['turn']]),
            parent_final_price=endcorp[pb['id']]['price'],
            ))
    # starts (par) records
    for r in rs:
        if r['t']=='sr' and r['type']=='par':
            pid=r['pid']; vals={p['id']:p['value'] for p in r['players']}
            c=r['corp']
            strow.append(dict(gid=gid,n=n,turn=r['turn'],nsr=nsr,phase=r['phase'],pid=pid,corp=c,par=r['price'],
                share_before=shares(vals)[pid],final_share=fshare[pid],rank=rank[pid],win=int(pid==winner),
                corp_final_price=endcorp[c]['price'],corp_ors=len(hist.get(c,[])),corp_rev=sum(h[2] or 0 for h in hist.get(c,[]))))
P=pd.DataFrame(prow); SP=pd.DataFrame(srow); ST=pd.DataFrame(strow)
P.to_pickle('P.pkl'); SP.to_pickle('SP.pkl'); ST.to_pickle('ST.pkl')
print(len(P),len(SP),len(ST))
