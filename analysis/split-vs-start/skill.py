import pandas as pd, numpy as np, json
P=pd.read_pickle('P.pkl')
# per player-game outcome
pg=P.groupby(['gid','pid']).agg(n=('n','first'),final_share=('final_share','first'),win=('win','first')).reset_index()
pg['rel']=pg.final_share*pg.n   # 1.0 = average
tot=pg.groupby('pid').agg(g=('gid','count'),rs=('rel','sum'),ws=('win','sum'),wexp=('n',lambda s:(1/s).sum()))
pg=pg.join(tot,on='pid')
# leave-one-out skill, shrunk toward 1.0 with k=5 pseudo-games
k=5
pg['skill']=((pg.rs-pg.rel)+k*1.0)/((pg.g-1)+k)
pg['games_other']=pg.g-1
pg[['gid','pid','skill','games_other']].to_pickle('skill.pkl')
print(pg.games_other.describe()); print(pg.skill.describe())
print('corr skill vs rel', pg[['skill','rel']].corr().iloc[0,1])
