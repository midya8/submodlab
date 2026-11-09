import copy,itertools,json,random,subprocess,sys,tempfile,unittest
from fractions import Fraction as F
from pathlib import Path
from submodlab.rounding import rounding_audit
from tools.build_rounding import controls

class RoundingTests(unittest.TestCase):
    def test_retained_controls(self):
        a=controls();r=a[0]['report'];self.assertEqual((r['expected_count'],r['over_budget_probability'],r['expected_value'],r['final_value']),('1','1/4','3/4','1'));self.assertTrue(r['history'][0]['tie']);self.assertEqual(r['final_subset'],[1]);self.assertFalse(a[2]['report']['rounding_allowed']);self.assertEqual(a[2]['report']['expected_value'],'1/4');self.assertTrue(all(t['value']=='0' for t in a[2]['report']['rows'] if t['size']==1));self.assertTrue(a[3]['report']['rounding_allowed']);self.assertEqual(a[3]['report']['final_value'],'1')
        for c in a:
            r=c['report'];self.assertEqual(F(r['probability_sum']),1)
            if r['rounding_allowed']:self.assertTrue(r['nondecrease_verified']);self.assertEqual(len(r['final_subset']),r['k'])
            else:self.assertIsNone(r['final_value']);self.assertEqual(r['history'],[])
    def test_120_independent_product_oracles(self):
        rng=random.Random(701)
        for t in range(120):
            n=1+t%6;p=[F(rng.randrange(5),4) for _ in range(n)];v=[F(rng.randrange(-5,8),3) for _ in range(1<<n)];s={'objective':{'kind':'table','data':list(map(str,v)),'k':t%(n+1)},'probabilities':list(map(str,p))};r=rounding_audit(s);masses={}
            for bits in itertools.product([0,1],repeat=n):
                prob=F(1)
                for j,b in enumerate(bits):prob*=p[j] if b else 1-p[j]
                masses[sum(b<<j for j,b in enumerate(bits))]=prob
            self.assertEqual(F(r['expected_value']),sum(v[m]*w for m,w in masses.items()));self.assertEqual(F(r['over_budget_probability']),sum(w for m,w in masses.items() if m.bit_count()>s['objective']['k']))
            for row in r['rows']:self.assertEqual(F(row['probability']),masses[row['mask']])
            for g in r['gradients']:
                i=g['item'];vv=[]
                for b in [0,1]:
                    pp=p[:];pp[i]=F(b);total=F(0)
                    for bits in itertools.product([0,1],repeat=n):
                        mass=F(1)
                        for j,x in enumerate(bits):mass*=pp[j] if x else 1-pp[j]
                        total+=mass*v[sum(x<<j for j,x in enumerate(bits))]
                    vv.append(total)
                self.assertEqual(F(g['value']),vv[1]-vv[0])
    def test_100_exact_derivative_difference_controls(self):
        rng=random.Random(702)
        for t in range(100):
            n=2+t%4;v=[str(rng.randrange(-6,8)) for _ in range(1<<n)];p=['1/2']*n;s={'objective':{'kind':'table','data':v,'k':n//2},'probabilities':p};r=rounding_audit(s);h=F(1,7)
            def val(a):return F(rounding_audit({'objective':s['objective'],'probabilities':list(map(str,a))})['expected_value'])
            for pair in r['pairs']:
                i,j=pair['i'],pair['j'];a=[F(1,2)]*n;b=a[:];b[i]+=h;b[j]+=h;c=a[:];c[i]+=h;d=a[:];d[j]+=h
                self.assertEqual((val(b)-val(c)-val(d)+val(a))/h**2,F(pair['mixed_partial']))
                b=a[:];b[i]+=h;b[j]-=h;c=a[:];c[i]-=h;c[j]+=h
                self.assertEqual((val(b)-2*val(a)+val(c))/h**2,F(pair['swap_curvature']))
    def test_120_full_rounding_path_oracles(self):
        rng=random.Random(703)
        for t in range(120):
            n=2+t%5;k=1+t%(n-1);a=[[rng.randrange(8) for _ in range(n)] for _ in range(1+t%6)];s={'objective':{'kind':'facility','data':[[str(x) for x in row] for row in a],'k':k},'probabilities':[str(F(k,n))]*n};r=rounding_audit(s)
            def val(p):
                total=F(0)
                for bits in itertools.product([0,1],repeat=n):
                    w=F(1)
                    for j,b in enumerate(bits):w*=p[j] if b else 1-p[j]
                    total+=w*sum(max([0]+[row[j] for j,b in enumerate(bits) if b]) for row in a)
                return total
            for step in r['history']:
                x=list(map(F,step['before']));i,j=step['i'],step['j'];self.assertEqual([i,j],[h for h,z in enumerate(x) if 0<z<1][:2]);self.assertGreaterEqual(F(step['curvature']),0);self.assertLess(step['fractional_after'],step['fractional_before'])
                for side in ['left','right']:
                    pp=list(map(F,step[side]));self.assertEqual(sum(pp),k);self.assertTrue(all(0<=z<=1 for z in pp));self.assertEqual(val(pp),F(step[side+'_value']))
                for h in [F(step['lo']),F(step['hi']),F(0),F(step['lo'])/3+2*F(step['hi'])/3]:
                    pp=x[:];pp[i]+=h;pp[j]-=h;self.assertEqual(val(pp),F(step['before_value'])+F(step['linear'])*h+F(step['quadratic'])*h*h)
                self.assertGreaterEqual(F(step['after_value']),F(step['before_value']))
            self.assertEqual(len(r['final_subset']),k);self.assertEqual(val(list(map(F,r['final_probabilities']))),F(r['final_value']))
    def test_all_vertices_and_probability_boundaries(self):
        for c in controls():
            s=c['report']['spec'];n=c['report']['n']
            if n>3:continue
            for bits in itertools.product([0,1],repeat=n):
                t=copy.deepcopy(s);t['objective']['k']=sum(bits);t['probabilities']=list(map(str,bits));r=rounding_audit(t);self.assertEqual(r['expected_value'],next(row['value'] for row in r['rows'] if row['probability']=='1'));self.assertEqual(r['history'],[])
    def test_gradient_context_terms_and_pair_terms(self):
        for c in controls():
            r=c['report']
            for g in r['gradients']:
                self.assertEqual(sum(F(t['probability']) for t in g['terms']),1);self.assertEqual(sum(F(t['contribution']) for t in g['terms']),F(g['value']))
            for p in r['pairs']:
                self.assertEqual(sum(F(t['probability']) for t in p['terms']),1);self.assertEqual(sum(F(t['contribution']) for t in p['terms']),F(p['mixed_partial']))
    def test_strict_schema(self):
        s=controls()[0]['report']['spec']
        for p in [[],['1/2'],[True,'1/2'],[0.5,'1/2'],['-1/2','1/2'],['2','0'],['01','0'],['1/0','0'],['1e-2','0'],['1/10001','0'],['1/2',' 1/2']]:
            t=copy.deepcopy(s);t['probabilities']=p
            with self.assertRaises(ValueError):rounding_audit(t)
        for t in [None,[],{},dict(s,extra=0)]:
            with self.assertRaises(ValueError):rounding_audit(t)
    def test_no_mutation(self):
        for c in controls():
            s=c['report']['spec'];b=copy.deepcopy(s);rounding_audit(s);self.assertEqual(s,b)
    def test_cli_preserves_output_on_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);o=p/'out.json';o.write_text('KEEP');f=p/'in.json'
            for text in ['{"objective":1,"objective":2,"probabilities":[]}','{"objective":NaN,"probabilities":[]}',' '*32769,'{}']:
                f.write_text(text);r=subprocess.run([sys.executable,'-m','submodlab.rounding_cli','--spec',str(f),'--json',str(o)],capture_output=True);self.assertEqual(r.returncode,2);self.assertEqual(o.read_text(),'KEEP')
            f.write_text(json.dumps(controls()[0]['report']['spec']));r=subprocess.run([sys.executable,'-m','submodlab.rounding_cli','--spec',str(f),'--json',str(o)],capture_output=True);self.assertEqual(r.returncode,0);self.assertEqual(json.loads(o.read_text()),controls()[0]['report'])
