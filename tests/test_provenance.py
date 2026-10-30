"""Adversarial authenticity checks: byte hashes are never evidence of execution."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from attested_evidence import verify_attestation, REPO, SIGNER, MANDATORY
from evaluate_gate import evaluate, REQUIRED_EVIDENCE, WEIGHTS
from ci_provenance import build


class ProvenanceTests(unittest.TestCase):
    SHA='f'*40
    def write(self,root,name,content):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(content if isinstance(content,bytes) else content.encode())
        return {'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

    def fabricated(self,root):
        # Reconstruct all 12 signed evidence identifiers, but not a real signed workflow.
        artifacts={k:self.write(root,f'{k}.json','{"status":"passed"}') for k in REQUIRED_EVIDENCE}
        agents={k:self.write(root,f'agent-{k}.json','{"runtime_executed":true}') for k in ('codex','claude','cursor')}
        data={'commit_sha':self.SHA,'scores':{k:10 for k in WEIGHTS},
              'evidence':{k:True for k in REQUIRED_EVIDENCE},
              'artifacts':artifacts,'agent_runs':agents,
              'catalog_review_artifact':self.write(root,'catalog.json','{}'),
              'manual_visual_review_artifact':self.write(root,'visual.json','{}'),
              'catalog_review_complete':True,'manual_visual_review':True,
              'unreviewed_candidates':0,'findings':[]}
        hashes={**{k:v['sha256'] for k,v in artifacts.items()},
                'catalog_review':data['catalog_review_artifact']['sha256'],
                'visual_review':data['manual_visual_review_artifact']['sha256'],
                **{f'agent_{k}':v['sha256'] for k,v in agents.items()}}
        manifest={'schema':'anti-ai-slop/independent-evidence-manifest/v1',
                  'commit_sha':self.SHA,'repository':REPO,'signer_workflow':SIGNER,
                  'project_url':'https://example.org/test','artifact_sha256':hashes}
        data['signed_evidence_manifest']=self.write(root,'signed.json',json.dumps(manifest))
        return data

    def test_fully_fabricated_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            data=self.fabricated(Path(d))
            result=evaluate(data,strict=True,base_dir=Path(d))
            self.assertFalse(result['approved'])
            self.assertTrue(any('Proveniência externa' in b for b in result['blockers']))

    def test_missing_real_verifier_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            data=self.fabricated(Path(d))
            valid,message=verify_attestation(data,Path(d),self.SHA,which=lambda _:None)
            self.assertFalse(valid)
            self.assertIn('ausente',message)

    def test_gh_failure_and_mismatched_subject_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            data=self.fabricated(Path(d)); root=Path(d)
            failed=lambda *args,**kwargs:SimpleNamespace(returncode=1,stdout='',stderr='no attestation')
            self.assertFalse(verify_attestation(data,root,self.SHA,runner=failed,which=lambda x:'/bin/gh')[0])
            wrong=json.dumps([{'verificationResult':{'statement':{'predicateType':'https://slsa.dev/provenance/v1',
                 'subject':[{'name':'signed.json','digest':{'sha256':'0'*64}}]}}}])
            result=lambda *args,**kwargs:SimpleNamespace(returncode=0,stdout=wrong,stderr='')
            self.assertFalse(verify_attestation(data,root,self.SHA,runner=result,which=lambda x:'/bin/gh')[0])

    def test_subject_binding_with_external_verifier(self):
        # Mocks the CLI result *only* to exercise data binding; this is NOT a real signed proof.
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);data=self.fabricated(root)
            content=(root/'signed.json').read_bytes();digest=hashlib.sha256(content).hexdigest()
            verified=json.dumps([{'verificationResult':{'statement':{'predicateType':'https://slsa.dev/provenance/v1',
                'subject':[{'name':'signed.json','digest':{'sha256':digest}}]}}}])
            def fake(argv,**kwargs):
                self.assertIn('--source-digest',argv)
                self.assertIn(SIGNER,argv)
                self.assertIn('--source-ref',argv)
                return SimpleNamespace(returncode=0,stdout=verified,stderr='')
            self.assertTrue(verify_attestation(data,root,self.SHA,runner=fake,which=lambda x:'/bin/gh')[0])
            data['artifacts']['build']['sha256']='e'*64
            self.assertFalse(verify_attestation(data,root,self.SHA,runner=fake,which=lambda x:'/bin/gh')[0])

    def test_synthetic_ci_manifest_refuses_fake_agent_runtime(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for dirname in ('agent-compat-codex','agent-compat-claude','agent-compat-cursor',
                            'gate-contract-evidence','synthetic-benchmark-reports'):
                (root/dirname).mkdir()
                if dirname.startswith('agent-compat-'):
                    agent=dirname.split('-')[-1]
                    (root/dirname/f'agent-{agent}.json').write_text(json.dumps({'real_agent_runtime':False}))
                else:(root/dirname/'result.txt').write_text('synthetic')
            manifest=build(root,self.SHA,'101')
            self.assertFalse(manifest['real_agent_runtime'])
            self.assertEqual(len(manifest['files']),5)
            (root/'agent-compat-claude'/'agent-claude.json').write_text(json.dumps({'real_agent_runtime':True}))
            with self.assertRaises(ValueError):build(root,self.SHA,'101')

if __name__=='__main__':unittest.main()
