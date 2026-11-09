'''Exact bounded submodular selection. No learned quality or scalability claim.'''
from fractions import Fraction as F
from itertools import combinations
import re

def parse(spec):
    if not isinstance(spec,dict) or set(spec)!={'kind','data','k'}:raise ValueError('Expected exactly kind, data, k')
    kind=spec['kind'];data=spec['data']
    def frac(s):
        if not isinstance(s,str) or len(s)>12 or not re.fullmatch(r'-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?',s):raise ValueError('Values must be exact integer/fraction strings')
        q=F(s)
        if abs(q.numerator)>10000 or q.denominator>10000:raise ValueError('Reduced numerator/denominator bound 10000')
        return q
    if kind=='facility':
        if not isinstance(data,list) or not 1<=len(data)<=8 or not isinstance(data[0],list):raise ValueError('Expected 1..8 represented rows')
        n=len(data[0])
        if not 1<=n<=6 or any(not isinstance(r,list) or len(r)!=n for r in data):raise ValueError('Matrix must have 1..6 item columns')
        a=[[frac(x) for x in r] for r in data]
        if any(x<0 for r in a for x in r):raise ValueError('Facility similarities must be nonnegative')
        values=[sum((max((r[j] for j in range(n) if mask>>j&1),default=F(0)) for r in a),F(0)) for mask in range(1<<n)]
    elif kind=='table':
        if not isinstance(data,list) or len(data) not in [2,4,8,16,32,64]:raise ValueError('Table length must be 2^n, n=1..6')
        n=len(data).bit_length()-1;values=[frac(x) for x in data]
    else:raise ValueError('kind must be facility or table')
    k=spec['k']
    if type(k) not in (int,float) or not 0<=k<=n or int(k)!=k:raise ValueError('k must be integer 0..n')
    return n,int(k),values

def audit(spec):
    n,k,v=parse(spec);full=(1<<n)-1
    def members(mask):return [j for j in range(n) if mask>>j&1]
    def gain(mask,j):return v[mask|1<<j]-v[mask]
    order=sorted(range(1<<n),key=lambda m:(len(members(m)),members(m)))
    edges=[{'mask':m,'subset':members(m),'item':j,'gain':gain(m,j)} for m in order for j in range(n) if not m>>j&1]
    dr=[{'mask':m,'subset':members(m),'item':i,'added':j,'before':gain(m,i),'after':gain(m|1<<j,i),'slack':gain(m,i)-gain(m|1<<j,i)} for m in order for i in range(n) for j in range(i+1,n) if not m>>i&1 and not m>>j&1]
    flags={'normalized':v[0]==0,'nonnegative':all(x>=0 for x in v),'monotone':all(e['gain']>=0 for e in edges),'submodular':all(d['slack']>=0 for d in dr)}
    eligible=all(flags.values());optimal=max(v[m] for m in order if len(members(m))<=k);opts=[members(m) for m in order if len(members(m))<=k and v[m]==optimal]
    mask=0;history=[];prefixes=[]
    for t in range(k+1):
        available=[j for j in range(n) if not mask>>j&1];ranked=sorted(available,key=lambda j:(-gain(mask,j),j));top=ranked[:k]
        upper=min(v[full],v[mask]+sum((max(F(0),gain(mask,j)) for j in top),F(0))) if eligible else None
        prefixes.append({'step':t,'mask':mask,'subset':members(mask),'value':v[mask],'ranked_remaining':ranked,'top_k_items':top,'top_k_gains':[gain(mask,j) for j in top],'upper_bound':upper})
        if t==k:break
        best=gain(mask,ranked[0]);ties=[j for j in available if gain(mask,j)==best];chosen=min(ties)
        history.append({'step':t+1,'before_mask':mask,'before_subset':members(mask),'before_value':v[mask],'candidates':[{'item':j,'gain':gain(mask,j),'value':v[mask|1<<j]} for j in available],'maximizers':ties,'chosen':chosen,'gain':best,'after_mask':mask|1<<chosen,'after_subset':members(mask|1<<chosen),'after_value':v[mask|1<<chosen]});mask|=1<<chosen
    top_single=sorted(range(n),key=lambda j:(-gain(0,j),j))[:k];singlemask=sum(1<<j for j in top_single)
    bound=min(p['upper_bound'] for p in prefixes) if eligible else None
    factor=1-(1-F(1,k))**k if eligible and k else None
    rows=[{'mask':m,'subset':members(m),'size':len(members(m)),'value':v[m],'feasible':len(members(m))<=k,'optimal':len(members(m))<=k and v[m]==optimal,'row_maxima':[max((F(r[j]) for j in members(m)),default=F(0)) for r in spec['data']] if spec['kind']=='facility' else None} for m in order]
    out={'spec':spec,'n':n,'k':k,'rows':rows,'edges':edges,'diminishing_returns':dr,'assumptions':flags,'eligible':eligible,'monotonicity_violations':[e for e in edges if e['gain']<0],'submodularity_violations':[d for d in dr if d['slack']<0],'history':history,'prefixes':prefixes,'greedy_subset':members(mask),'greedy_value':v[mask],'singleton_subset':sorted(top_single),'singleton_value':v[singlemask],'optimal_value':optimal,'optimal_subsets':opts,'actual_ratio':v[mask]/optimal if optimal>0 else None,'upper_bound':bound,'certified_ratio':v[mask]/bound if bound is not None and bound>0 else None,'finite_k_factor':factor,'guaranteed_value':factor*optimal if factor is not None else None,'guarantee_holds':v[mask]>=factor*optimal if factor is not None else None}
    def pack(x):
        if isinstance(x,F):return str(x)
        if isinstance(x,list):return [pack(a) for a in x]
        if isinstance(x,dict):return {k:pack(a) for k,a in x.items()}
        return x
    return pack(out)
