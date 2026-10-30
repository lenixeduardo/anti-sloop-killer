"""Regression for the exact v1.6 vulnerability: comprehensive forged reports passed.

The fixture fabricates 12 complete-looking artifacts. Only real GitHub/Sigstore
verification should be able to lift the provenance blocker in the strict gate.
"""
import hashlib
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_gate import evaluate,WEIGHTS,REQUIRED_EVIDENCE
from attested_evidence import REPO,SIGNER


def png(width, height=400):
    def chunk(typ, data):
        return struct.pack('>I',len(data))+typ+data+struct.pack('>I',zlib.crc32(typ+data)&0xffffffff)
    # A fully decodable solid-white PNG, not merely a spoofed magic header.
    raw=(b'\x00'+b'\xff\xff\xff'*width)*height
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0)) +
            chunk(b'IDAT',zlib.compress(raw)) + chunk(b'IEND',b''))


class ForgeryRegression(unittest.TestCase):
    def test_previous_fully_forged_10_of_10_now_blocks_on_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def ref(name,bytes_or_text):
                path=root/name;path.parent.mkdir(exist_ok=True,parents=True)
                payload=bytes_or_text if isinstance(bytes_or_text,bytes) else bytes_or_text.encode()
                path.write_bytes(payload)
                return {'path':name,'sha256':hashlib.sha256(payload).hexdigest()}
            def js(name,obj):return ref(name,json.dumps(obj,ensure_ascii=False))
            sha='f'*40;artifacts={}
            for kind in REQUIRED_EVIDENCE:
                if kind in ('build','unit_tests','functional_flows'):
                    log=ref(f'fake/{kind}.log',f'FAKE output from {kind}; not executed. '*5)
                    artifacts[kind]=js(f'fake/{kind}.json',{
                        'kind':kind,'status':'passed','commit_sha':sha,
                        'schema':'anti-ai-slop/test-result/v1','exit_code':0,
                        'command':'echo pretend-tests-passed','tests':{'passed':1,'failed':0},'log':log})
                elif kind.startswith('browser_'):
                    width={'browser_mobile':390,'browser_tablet':768,'browser_desktop':1440}[kind]
                    shot=ref(f'fake/{kind}.png',png(width))
                    artifacts[kind]=js(f'fake/{kind}.json',{
                        'kind':kind,'status':'passed','commit_sha':sha,
                        'schema':'anti-ai-slop/browser-result/v1',
                        'viewport':{'width':width},'checks':{'js_errors':0,'horizontal_overflow':False},
                        'screenshot':shot})
                else:
                    artifacts[kind]=js('fake/assets.json',{
                        'kind':kind,'status':'passed','commit_sha':sha,
                        'schema':'anti-ai-slop/asset-integrity/v1',
                        'no_assets':True,'reason':'Forged evidence claims this project has no protected assets.'})
            ids=[r['id'] for r in json.loads((ROOT/'references/rules.json').read_text())['rules']]
            catalog=js('fake/catalog.json',{'reviews':[{
                'id':rid,'status':'not_applicable','reason':'Invented reason to fake a complete audit.',
                'evidence_refs':['fake']} for rid in ids]})
            visual=js('fake/visual.json',{
                'schema':'anti-ai-slop/visual-review/v1','status':'approved',
                'reviewer':'Invented reviewer','notes':['No visual review happened.']})
            agents={}
            for name in ('codex','claude','cursor'):
                tx=ref(f'fake/{name}.txt',(f'{name} FAKE transcript, tool never invoked. ')*5)
                agents[name]=js(f'fake/{name}.json',{
                    'schema':'anti-ai-slop/agent-runtime/v1','agent':name,
                    'runtime_executed':True,'exit_code':0,'status':'passed',
                    'commit_sha':sha,'invocation':'echo pretend-agent-run','transcript':tx})
            data={'scores':dict.fromkeys(WEIGHTS,10),
                  'evidence':dict.fromkeys(REQUIRED_EVIDENCE,True),
                  'commit_sha':sha,'artifacts':artifacts,'catalog_review_artifact':catalog,
                  'manual_visual_review_artifact':visual,'agent_runs':agents,
                  'catalog_review_complete':True,'manual_visual_review':True,
                  'unreviewed_candidates':0,'findings':[]}
            result=evaluate(data,strict=True,base_dir=root)
            self.assertEqual(result['score'],10)
            self.assertFalse(result['approved'])
            self.assertTrue(any('Proveniência externa' in s for s in result['blockers']))
            # The previous implementation accepted this exact self-reported data.
            self.assertEqual(len(result['blockers']),1, result['blockers'])
            manifest={'schema':'anti-ai-slop/independent-evidence-manifest/v1',
                      'repository':REPO,'signer_workflow':SIGNER,'commit_sha':sha,
                      'project_url':'https://example.org',
                      'artifact_sha256':{**{k:v['sha256'] for k,v in artifacts.items()},
                                          'catalog_review':catalog['sha256'],'visual_review':visual['sha256'],
                                          **{f'agent_{k}':v['sha256'] for k,v in agents.items()}}}
            data['signed_evidence_manifest']=js('fake/signed.json',manifest)
            result2=evaluate(data,strict=True,base_dir=root)
            self.assertFalse(result2['approved'])
            self.assertTrue(any('Proveniência externa' in s for s in result2['blockers']))

if __name__=='__main__':unittest.main()
