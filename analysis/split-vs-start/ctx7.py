import json, collections, pandas as pd, numpy as np
pd.set_option('display.width',200)
fill=[]; phase_by_sr=[]; ends=0; unfilled=[]
games=collections.defaultdict(list)
for l in open('all.jsonl'):
    r=json.loads(l)
    if r['t'] in ('round','end'): games[r['gid']].append(r)
for gid,rs in games.items():
    e=rs[-1]
    if e['t']!='end' or e['status']!='finished' or e.get('exception') or e['recorded']!=e['engine_result']: continue
    seen=set(); branches={c['id'] for c in e['corps'] if c['branch']}
    for r in rs:
        if r['t']=='round' and r['kind']=='Stock':
            phase_by_sr.append(dict(gid=gid,sr=r['turn'],phase=r['phase']))
        if r['t'] in ('round','end') and r.get('tranches'):
            flat=[c for tr in r['tranches'][1:] for c in tr]
            for i,c in enumerate(flat):
                if c and i not in seen:
                    seen.add(i); fill.append(dict(gid=gid,slot=i+1,sr=r['turn'],branch=c in branches))
    unfilled.append(6-len(seen))
F=pd.DataFrame(fill); PH=pd.DataFrame(phase_by_sr)
print('Slot filled: median SR, share filled by a split')
print(F.groupby('slot').agg(N=('gid','size'),median_sr=('sr','median'),split_share=('branch','mean')).round(2))
print('\nGames with all 6 slots used:', np.mean(np.array(unfilled)==0).round(3))
print('\nPhase at the start of each stock round (share of games):')
print(pd.crosstab(PH.sr,PH.phase,normalize='index').round(2).reindex(columns=['2H','3H','4H','5H','6H','2+','3+','4+','7','D']).fillna(0))
