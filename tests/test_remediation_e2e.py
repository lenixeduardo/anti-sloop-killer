"""End-to-end synthetic site: finding -> contextual proposal -> preview -> fix -> browser proof.

The fixture is intentionally synthetic. It does not prove an agent's real-world design judgment.
"""
import hashlib
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_slop import audit
from apply_changes import apply
from browser_audit import run

@unittest.skipUnless(importlib.util.find_spec('playwright') is not None, 'Playwright not installed')
class RemediationE2E(unittest.TestCase):
    def test_static_fix_with_actual_chromium_before_after(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/'site'; project.mkdir()
            page=project/'index.html'
            old='''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Teste de reparo</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font-family:Arial,sans-serif;margin:0 auto;max-width:650px;padding:22px}</style></head>
<body><main><h1>Produto real</h1><a href="#">Ver detalhes</a>
<button type="button" aria-label="Abrir detalhes" onclick="document.getElementById('details').textContent='Informações abertas'">Abrir</button><p id="details"></p></main></body></html>'''
            page.write_text(old,encoding='utf-8')
            before=audit(project)
            self.assertIn('PLACEHOLDER_HREF',{x['key'] for x in before['findings']})
            browser=shutil.which('chromium')
            spec=[{'selector':'button[aria-label="Abrir detalhes"]','expect_selector':'#details','expect_text':'Informações abertas'}]
            old_report=run(None,Path(tmp)/'before',html_path=page,browser_path=browser,interaction_spec=spec)
            self.assertEqual(old_report['status'],'completed')
            self.assertEqual(len(old_report['viewport_results']['mobile']['checks']['dead_links']),1)
            plan={'changes':[{'path':'index.html','finding_id':'STATIC-0001',
                 'expected_sha256':hashlib.sha256(page.read_bytes()).hexdigest(),
                 'search':'<a href="#">Ver detalhes</a>',
                 'replace':'<a href="#details">Ver detalhes</a>'}]}
            # In-place anchor is not a dead link: it points to actual content.
            self.assertEqual(apply(project,plan)['status'],'preview')
            accepted=apply(project,plan,approved=True,checks=[[sys.executable,'-c',
                'from pathlib import Path; assert \'href="#details"\' in Path("index.html").read_text()']])
            self.assertEqual(accepted['status'],'applied_verified')
            after=audit(project)
            self.assertNotIn('PLACEHOLDER_HREF',{x['key'] for x in after['findings']})
            report=run(None,Path(tmp)/'after',html_path=page,browser_path=browser,interaction_spec=spec)
            self.assertEqual(report['status'],'completed')
            for viewport in ('desktop','tablet','mobile'):
                self.assertEqual(report['viewport_results'][viewport]['checks']['dead_links'],[])
                self.assertEqual(report['viewport_results'][viewport]['checks']['horizontal_overflow'],False)
                self.assertTrue(report['viewport_results'][viewport]['interactions'][0]['passed'])
                self.assertTrue(Path(report['viewport_results'][viewport]['screenshot']).is_file())

if __name__=='__main__':unittest.main()
