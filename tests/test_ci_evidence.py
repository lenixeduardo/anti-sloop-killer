import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from ci_evidence import run_command
from ci_summary import summarize

class CiEvidenceTests(unittest.TestCase):
    def test_success_and_failure_are_proven(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t)
            success=run_command('unit_tests',[sys.executable,'-c','print("PASSED")'],d)
            self.assertEqual(success['exit_code'],0)
            self.assertEqual(success['status'],'passed')
            self.assertIn('PASSED',(d/'unit_tests.log').read_text())
            failure=run_command('gate_contract',[sys.executable,'-c','raise SystemExit(4)'],d)
            self.assertEqual(failure['exit_code'],4)
            self.assertEqual(failure['status'],'failed')
    def test_summary_does_not_claim_real_agent_runtime(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'agent.json'
            p.write_text(json.dumps({'schema':'anti-ai-slop/agent-compat-report/v1',
                'results':[{'agent':'codex','status':'compatible_not_executed'}]}))
            summary=summarize([p])
            self.assertIn('NOT real agent execution',summary)
            self.assertIn('NOT HOMOLOGATED',summary)

if __name__=='__main__':unittest.main()
