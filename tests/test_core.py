import copy,itertools,json,random,subprocess,sys,tempfile,unittest
from fractions import Fraction as F
from pathlib import Path
from submodlab import audit

def facility(a,k):return {'kind':'facility','data':[[str(x) for x in r] for r in a],'k':k}
def table(v,k):return {'kind':'table','data':[str(x) for x in v],'k':k}
def subsets(n):return [frozenset(c) for k in range(n+1) for c in itertools.combinations(range(n),k)]
def mask(s):return sum(1<<j for j in s)
def refvalue(a,s):return sum((sorted([F(r[j]) for j in s])[-1] if s else F(0) for r in a),F(0))

class ExactTests(unittest.TestCase):
    def test_120_facility_exhaustive_oracles(self):
        rng=random.Random(902)
        for t in range(120):
            n=1+t%6;a=[[F(rng.randrange(9),rng.randrange(1,5)) for _ in range(n)] for _ in range(1+t%8)];k=t%(n+1);r=audit(facility(a,k));ss=subsets(n);v={s:refvalue(a,s) for s in ss};self.assertTrue(r['eligible']);opt=max(v[s] for s in ss if len(s)<=k)
            self.assertEqual(F(r['optimal_value']),opt);self.assertEqual(r['optimal_subsets'],[sorted(s) for s in ss if len(s)<=k and v[s]==opt])
            for row in r['rows']:self.assertEqual(F(row['value']),v[frozenset(row['subset'])]);self.assertEqual(sum(map(F,row['row_maxima'])),v[frozenset(row['subset'])])
            s=frozenset()
            for h in r['history']:
                gains={j:v[s|{j}]-v[s] for j in range(n) if j not in s};best=max(gains.values());ties=[j for j,g in gains.items() if g==best];self.assertEqual(h['maximizers'],ties);self.assertEqual(h['chosen'],min(ties));s=s|{h['chosen']};self.assertEqual(F(h['after_value']),v[s])
            for p in r['prefixes']:self.assertGreaterEqual(F(p['upper_bound']),opt)
            self.assertGreaterEqual(F(r['upper_bound']),opt);self.assertLessEqual(F(r['greedy_value']),opt)
            if k:self.assertTrue(r['guarantee_holds']);self.assertGreaterEqual(F(r['greedy_value']),F(r['finite_k_factor'])*opt)
    def test_100_arbitrary_table_lattice_equivalence(self):
        rng=random.Random(903)
        for t in range(100):
            n=1+t%5;v=[F(rng.randrange(-4,10),rng.randrange(1,4)) for _ in range(1<<n)];ss=subsets(n);r=audit(table(v,t%(n+1)));sub=all(v[mask(a)]+v[mask(b)]>=v[mask(a|b)]+v[mask(a&b)] for a in ss for b in ss);mono=all(v[mask(a)]<=v[mask(b)] for a in ss for b in ss if a<=b)
            self.assertEqual(r['assumptions']['submodular'],sub);self.assertEqual(r['assumptions']['monotone'],mono);self.assertEqual(r['eligible'],sub and mono and v[0]==0 and all(x>=0 for x in v))
            if not r['eligible']:self.assertIsNone(r['upper_bound']);self.assertIsNone(r['finite_k_factor']);self.assertIsNone(r['certified_ratio']);self.assertIsNone(r['guarantee_holds'])
            for d in r['diminishing_returns']:
                m=d['mask'];i=d['item'];j=d['added'];self.assertEqual(F(d['slack']),v[m|1<<i]+v[m|1<<j]-v[m]-v[m|1<<i|1<<j])
    def test_40_scale_invariance(self):
        rng=random.Random(904)
        for _ in range(40):
            a=[[rng.randrange(6) for _ in range(4)] for _ in range(5)];b=[[F(3,7)*x for x in row] for row in a];r=audit(facility(a,2));s=audit(facility(b,2));self.assertEqual(r['greedy_subset'],s['greedy_subset']);self.assertEqual(r['optimal_subsets'],s['optimal_subsets']);self.assertEqual(r['actual_ratio'],s['actual_ratio']);self.assertEqual(F(s['upper_bound']),F(3,7)*F(r['upper_bound']))
    def test_30_facility_table_equivalence(self):
        rng=random.Random(905)
        for _ in range(30):
            a=[[rng.randrange(6) for _ in range(4)] for _ in range(4)];r=audit(facility(a,2));v=[refvalue(a,{j for j in range(4) if m>>j&1}) for m in range(16)];s=audit(table(v,2))
            for key in r:
                if key not in ['spec','rows']:self.assertEqual(r[key],s[key])
    def test_60_all_subset_posteriori_bounds(self):
        rng=random.Random(906)
        for _ in range(60):
            n=5;a=[[rng.randrange(10) for _ in range(n)] for _ in range(5)];ss=subsets(n);v={s:refvalue(a,s) for s in ss};k=rng.randrange(n+1);opt=max(v[s] for s in ss if len(s)<=k)
            for s in ss:
                gains=sorted((v[s|{j}]-v[s] for j in range(n) if j not in s),reverse=True);upper=v[s]+sum(gains[:k]);self.assertGreaterEqual(upper,opt)
    def fixtures(self):return json.loads(Path('docs/audits.json').read_text())['cases']
    def test_greedy_counterexample(self):
        r=self.fixtures()[0]['report'];self.assertEqual((r['greedy_subset'],r['greedy_value'],r['optimal_value'],r['actual_ratio']),([0,1],'5','6','5/6'));self.assertEqual(r['optimal_subsets'],[[1,2]]);self.assertEqual(r['finite_k_factor'],'3/4');self.assertEqual(r['history'][0]['maximizers'],[0]);self.assertEqual(r['history'][1]['maximizers'],[1,2])
    def test_singleton_counterexample(self):
        r=self.fixtures()[1]['report'];self.assertEqual(r['singleton_value'],'5');self.assertEqual(r['greedy_value'],'9');self.assertEqual(r['optimal_value'],'9')
    def test_synergy_invalidates_bound(self):
        r=self.fixtures()[9]['report'];self.assertFalse(r['assumptions']['submodular']);self.assertTrue(r['assumptions']['monotone']);self.assertEqual(r['actual_ratio'],'3/10');self.assertIsNone(r['finite_k_factor']);self.assertTrue(r['submodularity_violations'])
    def test_nonmonotone_forced_k_is_not_optimal(self):
        r=self.fixtures()[10]['report'];self.assertTrue(r['assumptions']['submodular']);self.assertFalse(r['assumptions']['monotone']);self.assertEqual(r['greedy_value'],'0');self.assertEqual(r['optimal_value'],'2');self.assertEqual(r['optimal_subsets'],[[0]])
    def test_normalization_is_explicit(self):
        r=self.fixtures()[11]['report'];self.assertFalse(r['assumptions']['normalized']);self.assertTrue(r['assumptions']['monotone']);self.assertIsNone(r['finite_k_factor'])
    def test_zero_budget(self):
        r=audit(facility([[1,2]],0));self.assertEqual(r['greedy_subset'],[]);self.assertEqual(r['optimal_subsets'],[[]]);self.assertEqual(r['upper_bound'],'0');self.assertIsNone(r['finite_k_factor']);self.assertIsNone(r['actual_ratio']);self.assertEqual(len(r['prefixes']),1)
    def test_all_zero_ties_and_zero_ratio(self):
        r=audit(facility([[0,0,0]],2));self.assertEqual(len(r['optimal_subsets']),7);self.assertEqual(r['greedy_subset'],[0,1]);self.assertEqual(r['history'][0]['maximizers'],[0,1,2]);self.assertEqual(r['upper_bound'],'0');self.assertIsNone(r['certified_ratio'])
    def test_all_items(self):
        r=audit(facility([[1,2,3],[3,2,1]],3));self.assertEqual(r['greedy_value'],r['optimal_value']);self.assertEqual(r['upper_bound'],r['optimal_value'])
    def test_finite_factor_exact(self):
        for k in range(1,7):self.assertEqual(F(audit(facility([[1]*6],k))['finite_k_factor']),1-(1-F(1,k))**k)
    def test_negative_monotone_false(self):
        r=audit(table([0,-1,-2,-3],2));self.assertFalse(r['assumptions']['nonnegative']);self.assertIsNone(r['actual_ratio']);self.assertEqual(r['optimal_value'],'0')
    def test_single_item(self):
        r=audit(facility([[2],[3]],1));self.assertEqual(r['greedy_value'],'5');self.assertEqual(r['finite_k_factor'],'1');self.assertEqual(r['certified_ratio'],'1')
    def test_input_hazards(self):
        for x in [1,1.0,True,None,'1.0','01','1/0','1/-2','NaN','1e2','10001','1/10001','1 '*20]:
            with self.assertRaises(ValueError):audit({'kind':'table','data':['0',x],'k':1})
        self.assertEqual(audit(table([0,'20000/2'],1))['greedy_value'],'10000')
    def test_schema(self):
        for s in [None,[],{},dict(facility([[1]],1),extra=0),{'kind':'x','data':['0','1'],'k':1},facility([],0),facility([[]],0),facility([[1],[1,2]],1),table([0,1,2],1),facility([[-1]],1),facility([[1]*7],1),facility([[1]]*9,1)]:
            with self.assertRaises(ValueError):audit(s)
    def test_budget_validation(self):
        for k in [None,True,-1,2,0.1,'1']:
            with self.assertRaises(ValueError):audit(facility([[1]],k))
        self.assertEqual(audit(facility([[1]],1.0))['k'],1)
    def test_no_mutation(self):
        s=facility([[1,0],[0,1]],1);b=copy.deepcopy(s);audit(s);self.assertEqual(s,b)
    def test_retained_reports(self):
        for c in self.fixtures():self.assertEqual(audit(c['report']['spec']),c['report'])
    def test_n6_boundary(self):
        r=audit(facility([[1]*6]*8,6));self.assertEqual(len(r['rows']),64);self.assertEqual(len(r['edges']),192);self.assertEqual(len(r['diminishing_returns']),240)
    def test_cli_valid_invalid_and_no_stale_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);s=p/'s.json';o=p/'o.json';s.write_text(json.dumps(facility([[1]],1)));run=lambda:subprocess.run([sys.executable,'-m','submodlab','--spec',str(s),'--json',str(o)],capture_output=True)
            self.assertEqual(run().returncode,0);good=o.read_text()
            for text in ['{}','{"kind":"table","data":["0","1"],"k":1,"k":0}','{"kind":"table","data":["0","1"],"k":NaN}',' '*32769]:
                s.write_text(text);self.assertEqual(run().returncode,2);self.assertEqual(o.read_text(),good)
    def test_cli_invalid_assumptions_are_valid_input(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'s').write_text(json.dumps(table([0,1,1,5],2)));r=subprocess.run([sys.executable,'-m','submodlab','--spec',str(p/'s'),'--json',str(p/'o')],capture_output=True);self.assertEqual(r.returncode,0);self.assertFalse(json.loads((p/'o').read_text())['eligible'])
if __name__=='__main__':unittest.main()
