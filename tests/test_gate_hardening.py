"""Negative cases: fabricated success must not pass a strict gate."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_gate import evaluate, _artifact_json_valid, _agent_runtime_valid, REQUIRED_EVIDENCE

class GateHardeningTests(unittest.TestCase):
    def base(self):
        return {'scores':{k:9.9 for k in ('identity','layout','functionality','accessibility','motion','content')},
                'evidence':{k:True for k in REQUIRED_EVIDENCE},
                'catalog_review_complete':True,'manual_visual_review':True,
                'unreviewed_candidates':0,'findings':[],'commit_sha':'a'*40}
    def dump(self,root,name,content):
        path=root/name
        if isinstance(content,dict):content=json.dumps(content)
        path.write_text(content,encoding='utf-8')
        return {'path':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    def test_boolean_gate_does_not_approve(self):
        self.assertFalse(evaluate(self.base(),strict=True)['approved'])
    def test_hash_only_dummy_log_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            fake=self.dump(root,'dummy.txt','synthetic fixture evidence')
            self.assertFalse(_artifact_json_valid('unit_tests',fake,root,'a'*40))
    def test_invalid_result_and_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            log=self.dump(root,'test.log','test suite completed successfully')
            obj={'schema':'anti-ai-slop/test-result/v1','kind':'unit_tests','status':'passed',
                 'exit_code':0,'command':'python -m unittest','tests':{'passed':2,'failed':0},
                 'commit_sha':'a'*40,'log':log}
            artifact=self.dump(root,'test.json',obj)
            self.assertTrue(_artifact_json_valid('unit_tests',artifact,root,'a'*40))
            obj['tests']['failed']=1
            altered=self.dump(root,'test2.json',obj)
            self.assertFalse(_artifact_json_valid('unit_tests',altered,root,'a'*40))  # status 'passed' inconsistente com falhas
            (root/'test.json').write_text('tampered')
            self.assertFalse(_artifact_json_valid('unit_tests',artifact,root,'a'*40))
    def test_fake_agent_compatibility_is_not_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            artifact=self.dump(root,'compat.json',{'schema':'anti-ai-slop/agent-compat/v1',
               'agent':'codex','status':'compatible_not_executed','runtime_executed':False})
            self.assertFalse(_agent_runtime_valid(artifact,'codex',root,'a'*40))
    def test_all_confirmed_findings_block_in_strict(self):
        a=self.base()
        a['findings']=[{'id':'P2-redesign','status':'confirmed','severity':'P2'}]
        result=evaluate(a,strict=True)
        self.assertFalse(result['approved'])
        self.assertTrue(any('P2-redesign' in x for x in result['blockers']))
    def test_legacy_mode_is_not_valid_ci_proof(self):
        # Existing Python evaluate(strict=False) is analysis-only;
        # CLI --legacy-bools always fails closed.
        self.assertFalse(evaluate(self.base(),strict=False)['approved'])

if __name__=='__main__':unittest.main()
