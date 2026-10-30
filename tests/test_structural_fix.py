import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from structural_fix import plan
from apply_changes import apply

class StructuralFixTests(unittest.TestCase):
    def setup(self,folder,ext='.html',content='<main><a id="cta" href="#">Open</a></main>'):
        root=Path(folder); file=root/('index'+ext);file.write_text(content,encoding='utf-8')
        return root,file,hashlib.sha256(file.read_bytes()).hexdigest()
    def test_html_attribute_replace_and_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,f,digest=self.setup(tmp)
            proposal=plan(root,{'edits':[{'path':f.name,'expected_sha256':digest,'id':'cta','operation':'set_attribute','attribute':'href','value':'/projects'}]})
            preview=apply(root,proposal)
            self.assertEqual(preview['status'],'preview')
            self.assertIn('href="/projects"',preview['diff'])
            self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),digest)
            result=apply(root,proposal,approved=True,checks=[[sys.executable,'-c','from pathlib import Path; assert "href=\\\"/projects\\\"" in Path("index.html").read_text()']])
            self.assertEqual(result['status'],'applied_verified')
    def test_rollback_after_failed_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,f,digest=self.setup(tmp)
            proposal=plan(root,{'edits':[{'path':f.name,'expected_sha256':digest,'id':'cta','operation':'set_attribute','attribute':'href','value':'/projects'}]})
            result=apply(root,proposal,approved=True,checks=[[sys.executable,'-c','raise SystemExit(9)']])
            self.assertEqual(result['status'],'rolled_back')
            self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),digest)
    def test_replace_element(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,f,digest=self.setup(tmp)
            proposal=plan(root,{'edits':[{'path':f.name,'expected_sha256':digest,'id':'cta','operation':'replace_element','markup':'<a id="cta" href="/jobs"><span>My work</span></a>'}]})
            self.assertEqual(apply(root,proposal,approved=True)['status'],'applied_unverified')
            self.assertIn('<span>My work</span>',f.read_text())
    def test_reject_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,f,digest=self.setup(tmp,content='<div id="cta"></div><div id="cta"></div>')
            with self.assertRaisesRegex(ValueError,'exactly one'):
                plan(root,{'edits':[{'path':f.name,'expected_sha256':digest,'id':'cta','operation':'set_attribute','attribute':'aria-label','value':'Open'}]})
    def test_reject_injected_handlers_and_baseline_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,f,digest=self.setup(tmp)
            edit={'path':f.name,'expected_sha256':digest,'id':'cta','operation':'set_attribute','attribute':'onclick','value':'alert(1)'}
            with self.assertRaisesRegex(ValueError,'Unsafe'):
                plan(root,{'edits':[edit]})
            edit['attribute']='aria-label';f.write_text('drift',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                plan(root,{'edits':[edit]})
    def test_vue_and_astro_literal_template(self):
        for ext in ['.vue','.astro','.svelte']:
            with self.subTest(ext=ext), tempfile.TemporaryDirectory() as tmp:
                root,f,digest=self.setup(tmp,ext=ext,content='<template><button id="save">Save</button></template>')
                proposal=plan(root,{'edits':[{'path':f.name,'expected_sha256':digest,'id':'save','operation':'set_attribute','attribute':'type','value':'button'}]})
                self.assertEqual(apply(root,proposal,approved=True)['status'],'applied_unverified')
                self.assertIn('type="button"',f.read_text())
    @unittest.skipUnless(shutil.which('node'),'Node missing')
    def test_tsx_ast_target(self):
        check=__import__('subprocess').run(['node','-e',"try{require('typescript')}catch(e){try{require(require('path').join(require('child_process').execFileSync('npm',['root','-g'],{encoding:'utf8'}).trim(),'typescript'))}catch(e2){process.exit(1)}}"],capture_output=True)
        if check.returncode: self.skipTest('TypeScript module not available locally')
        with tempfile.TemporaryDirectory() as tmp:
            root,f,digest=self.setup(tmp,ext='.tsx',content='export default function Page(){return <><button id="save" type="submit">Save</button></>}')
            proposal=plan(root,{'edits':[{'path':f.name,'expected_sha256':digest,'id':'save','operation':'set_attribute','attribute':'type','value':'button'}]})
            self.assertEqual(apply(root,proposal,approved=True)['status'],'applied_unverified')
            self.assertIn('type="button"',f.read_text())

if __name__=='__main__':unittest.main()
