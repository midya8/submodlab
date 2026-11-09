'''Original synthetic controls; no external data.'''
import json,random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from submodlab.rounding import rounding_audit

def controls():
    f=lambda a,k,p:{'objective':{'kind':'facility','data':[[str(x) for x in row] for row in a],'k':k},'probabilities':p}
    t=lambda a,k,p:{'objective':{'kind':'table','data':[str(x) for x in a],'k':k},'probabilities':p}
    cases=[('expected count is not a hard budget',f([[1,1]],1,['1/2']*2)),('modular endpoint tie',t([0,1,1,2],1,['1/2']*2)),('synergy refuses rounding',t([0,0,0,1],1,['1/2']*2)),('nonmonotone cut still rounds',t([0,1,1,0],1,['1/2']*2)),('nonintegral sum is diagnostic',f([[1,2]],1,['1/4']*2)),('wrong integral sum refuses',f([[1,2,3]],1,['1/2','1/2','1'])),('integral point no steps',f([[3,2,1]],2,['1','0','1'])),('zero budget',f([[1,2]],0,['0','0'])),('all items',f([[1,2]],2,['1','1'])),('negative modular baseline',t([-2,-1,-1,0],1,['1/2']*2)),('asymmetric endpoint',f([[1,4]],1,['1/3','2/3'])),('coverage three probabilities',f([[1,1,0],[1,1,0],[1,0,1],[1,0,1],[0,1,0],[0,0,1]],2,['1/2','3/4','3/4']))]
    cases.append(('one item has no pair',f([[3]],1,['1'])))
    rng=random.Random(191)
    for n in range(3,7):
        for k in [1,n-1]:cases.append((f'seeded n={n} k={k}',f([[rng.randrange(8) for _ in range(n)] for _ in range(n)],k,[f'{k}/{n}']*n)))
    return [{'name':name,'report':rounding_audit(s)} for name,s in cases]
if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]/'docs/rounding-audits.json';p.write_text(json.dumps(controls(),separators=(',',':'))+'\n');print(p.stat().st_size,'bytes',len(controls()),'controls')
