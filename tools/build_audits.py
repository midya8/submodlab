import json,random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from submodlab import audit

def facility(rows,k):return {'kind':'facility','data':[[str(x) for x in r] for r in rows],'k':k}
def table(v,k):return {'kind':'table','data':[str(x) for x in v],'k':k}
cases=[]
def add(name,s):cases.append({'name':name,'report':audit(s)})
# A covers 4/6, then either B or C adds one. B+C cover all six.
rows=[[1,1,0],[1,1,0],[1,0,1],[1,0,1],[0,1,0],[0,0,1]]
add('Greedy is useful, not always optimal',facility(rows,2))
add('Singleton top-k repeats a representative',facility([[5,5,0],[0,0,4]],2))
add('One slot is exact',facility(rows,1))
add('Zero slots',facility(rows,0))
add('All items',facility(rows,3))
add('All zero: every feasible subset ties',facility([[0,0,0]],2))
add('Fractional facility values',facility([['1/2','2/3','0'],['0','1/3','4/5']],2))
add('Weighted coverage, encoded row weights',facility([[3,3,0],[0,2,2],[1,0,0]],2))
add('Modular table: singleton selection is exact',table([0,3,2,5,1,4,3,6],2))
add('Synergy breaks diminishing returns',table([0,2,1,3,1,3,10,12],2))
add('Submodular but nonmonotone: forced greedy can lose',table([0,2,1,0],2))
add('Nonzero empty baseline: normalized guarantee withheld',table([1,2,3,4],1))
add('Negative values: guarantee withheld',table([0,-1,-2,-3],2))
add('k zero does not license a theorem factor',table([0,1,2,3],0))
rng=random.Random(901)
for t in range(10):
 n=3+t%4;m=3+t%6;add('Seeded facility control '+str(t+1),facility([[rng.randrange(8) for _ in range(n)] for _ in range(m)],t%(n+1)))
Path('docs/audits.json').write_text(json.dumps({'cases':cases},separators=(',',':'))+'\n')
Path('examples/coverage.json').write_text(json.dumps(cases[0]['report']['spec'],indent=2)+'\n')
print('Retained',len(cases),'exact reports')
