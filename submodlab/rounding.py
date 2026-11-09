'''Exact product distributions and deterministic cardinality pipage rounding.
Established finite submodular theory, not continuous optimization or randomized rounding.
'''
from fractions import Fraction as F
import re
from .core import parse,audit

def rounding_audit(spec):
    if not isinstance(spec,dict) or set(spec)!={'objective','probabilities'}:raise ValueError('Expected exactly objective, probabilities')
    n,k,v=parse(spec['objective']);p=spec['probabilities']
    if not isinstance(p,list) or len(p)!=n:raise ValueError('One probability per selectable item required')
    def q(x):
        if not isinstance(x,str) or len(x)>12 or not re.fullmatch(r'(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?',x):raise ValueError('Probabilities must be nonnegative exact fraction strings')
        z=F(x)
        if not 0<=z<=1 or z.denominator>10000 or z.numerator>10000:raise ValueError('Probabilities in [0,1], reduced bound 10000')
        return z
    x=[q(a) for a in p];members=lambda m:[j for j in range(n) if m>>j&1]
    def probability(m,excluded=(),at=None):
        a=x if at is None else at;z=F(1)
        for j in range(n):
            if j not in excluded:z*=a[j] if m>>j&1 else 1-a[j]
        return z
    def value(a):return sum((v[m]*probability(m,at=a) for m in range(1<<n)),F(0))
    rows=[{'mask':m,'subset':members(m),'size':len(members(m)),'probability':probability(m),'value':v[m],'contribution':v[m]*probability(m),'over_budget':len(members(m))>k} for m in range(1<<n)]
    counts=[sum((r['probability'] for r in rows if r['size']==s),F(0)) for s in range(n+1)]
    gradients=[];pairs=[]
    for i in range(n):
        terms=[{'mask':m,'probability':probability(m,(i,)),'difference':v[m|1<<i]-v[m],'contribution':probability(m,(i,))*(v[m|1<<i]-v[m])} for m in range(1<<n) if not m>>i&1]
        gradients.append({'item':i,'value':sum((t['contribution'] for t in terms),F(0)),'terms':terms})
        for j in range(i+1,n):
            terms=[{'mask':m,'probability':probability(m,(i,j)),'difference':v[m|1<<i|1<<j]-v[m|1<<i]-v[m|1<<j]+v[m],'contribution':probability(m,(i,j))*(v[m|1<<i|1<<j]-v[m|1<<i]-v[m|1<<j]+v[m])} for m in range(1<<n) if not m>>i&1 and not m>>j&1]
            h=sum((t['contribution'] for t in terms),F(0));pairs.append({'i':i,'j':j,'mixed_partial':h,'swap_curvature':-2*h,'terms':terms})
    submod=audit(spec['objective'])['assumptions']['submodular'];total=sum(x,F(0));allowed=submod and total==k;history=[];a=x[:];initial=value(x)
    if allowed:
        while any(0<t<1 for t in a):
            frac=[j for j in range(n) if 0<a[j]<1];assert len(frac)>=2
            i,j=frac[:2];lo=max(-a[i],a[j]-1);hi=min(1-a[i],a[j]);before=value(a)
            def endpoint(t):
                b=a[:];b[i]+=t;b[j]-=t;return b
            left,right=endpoint(lo),endpoint(hi);lv,rv=value(left),value(right)
            # Exact quadratic coefficient from the other coordinates, not a fit.
            mixed=sum((probability(m,(i,j),a)*(v[m|1<<i|1<<j]-v[m|1<<i]-v[m|1<<j]+v[m]) for m in range(1<<n) if not m>>i&1 and not m>>j&1),F(0))
            gi=sum((probability(m,(i,),a)*(v[m|1<<i]-v[m]) for m in range(1<<n) if not m>>i&1),F(0));gj=sum((probability(m,(j,),a)*(v[m|1<<j]-v[m]) for m in range(1<<n) if not m>>j&1),F(0))
            chosen='left' if lv>=rv else 'right';b=left if chosen=='left' else right;after=lv if chosen=='left' else rv
            history.append({'step':len(history)+1,'i':i,'j':j,'before':a[:],'before_value':before,'linear':gi-gj,'quadratic':-mixed,'curvature':-2*mixed,'lo':lo,'hi':hi,'left':left,'right':right,'left_value':lv,'right_value':rv,'tie':lv==rv,'chosen':chosen,'after':b[:],'after_value':after,'gain':after-before,'fractional_before':len(frac),'fractional_after':sum(0<t<1 for t in b)})
            a=b
    final=[j for j in range(n) if a[j]==1] if allowed else None
    out={'spec':spec,'n':n,'k':k,'rows':rows,'count_probabilities':counts,'probability_sum':sum(counts,F(0)),'expected_count':total,'over_budget_probability':sum(counts[k+1:],F(0)),'expected_value':initial,'gradients':gradients,'pairs':pairs,'submodular':submod,'sum_equals_k':total==k,'rounding_allowed':allowed,'withheld_reasons':([] if submod else ['objective is not submodular'])+([] if total==k else ['probability sum must equal integer k']),'history':history,'final_probabilities':a if allowed else None,'final_subset':final,'final_value':v[sum(1<<j for j in final)] if allowed else None,'rounding_gain':value(a)-initial if allowed else None,'nondecrease_verified':value(a)>=initial if allowed else None}
    def pack(z):
        if isinstance(z,F):return str(z)
        if isinstance(z,list):return [pack(t) for t in z]
        if isinstance(z,dict):return {k:pack(t) for k,t in z.items()}
        return z
    return pack(out)
