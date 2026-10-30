import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_gate import evaluate

class GateTests(unittest.TestCase):
    def base(self):
        return {'scores':{'identity':9.8,'layout':9.8,'functionality':9.8,'accessibility':9.8,'motion':9.8,'content':9.8},
         'evidence':{x:True for x in ('build','unit_tests','browser_desktop','browser_tablet','browser_mobile','functional_flows','assets_preserved')},
         'catalog_review_complete':True,'manual_visual_review':True,'unreviewed_candidates':0,'findings':[]}
    def test_missing_evidence_blocks(self):
        a=self.base(); a['evidence']['browser_mobile']=False
        self.assertFalse(evaluate(a)['approved'])
    def test_p0_blocks_score(self):
        a=self.base();a['findings']=[{'id':'one','severity':'P0','status':'confirmed'}]
        self.assertFalse(evaluate(a)['approved'])
    def test_verified_fixes_need_tests(self):
        a=self.base();a['findings']=[{'id':'one','severity':'P1','status':'fixed_verified'}]
        self.assertFalse(evaluate(a)['approved'])
    def test_pending_candidates_block(self):
        a=self.base();a['unreviewed_candidates']=1
        self.assertFalse(evaluate(a)['approved'])
    def test_manual_review_block(self):
        a=self.base();a['manual_visual_review']=False
        self.assertFalse(evaluate(a)['approved'])
    def test_score_below_target(self):
        a=self.base();a['scores']['identity']=6
        self.assertFalse(evaluate(a)['approved'])
    def test_valid_evidence_can_pass(self):
        self.assertTrue(evaluate(self.base())['approved'])
    def test_no_data_block(self):
        self.assertFalse(evaluate({})['approved'])

if __name__=='__main__':unittest.main()

class CoverageAndPlanTests(unittest.TestCase):
    def test_coverage_inventory_complete(self):
        from coverage_report import build
        result=build()
        self.assertEqual(result['catalog_count'],228)
        self.assertTrue(result['static_rule_count']<228)
        self.assertTrue(all(x['review_status']=='pending' for x in result['rules']))
    def test_plan_includes_acceptance_and_preservation(self):
        from remediation_plan import make_plan
        plan=make_plan({'findings':[{'id':'S-1','key':'MISSING_IMG_ALT','file':'index.html','line':1,'severity':'P1','source_rules':['NX-021'],'note':'Fix alt'}]})
        self.assertIn('Teste de aceitação',plan)
        self.assertIn('hashes dos assets',plan)
        self.assertIn('S-1',plan)

class StrictEvidenceTests(unittest.TestCase):
    def test_booleans_never_pass_strict(self):
        sample=GateTests().base()
        self.assertTrue(evaluate(sample)['approved'])  # legacy evaluator, not CLI default
        self.assertFalse(evaluate(sample,strict=True)['approved'])
    def test_artifacts_and_catalog_review_must_be_verifiable(self):
        import tempfile, hashlib, json
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            source=Path(__file__).resolve().parents[1]
            ids=[r['id'] for r in json.loads((source/'references/rules.json').read_text())['rules']]
            catalog=base/'catalog.json'
            catalog.write_text(json.dumps({'reviews':[{'id':k,'status':'not_applicable',
                'reason':'Not present in this synthetic test fixture'} for k in ids]}))
            sample=GateTests().base()
            sample['artifacts']={}
            for key in ('build','unit_tests','browser_desktop','browser_tablet','browser_mobile','functional_flows','assets_preserved'):
                f=base/(key+'.txt');f.write_text('synthetic fixture evidence')
                sample['artifacts'][key]={'path':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
            sample['catalog_review_artifact']={'path':'catalog.json','sha256':hashlib.sha256(catalog.read_bytes()).hexdigest()}
            self.assertTrue(evaluate(sample,strict=True,base_dir=base)['approved'])
            (base/'browser_mobile.txt').write_text('changed')
            self.assertFalse(evaluate(sample,strict=True,base_dir=base)['approved'])
