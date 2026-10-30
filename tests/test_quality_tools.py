import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from lighthouse_audit import summarize,run
from browser_audit import run as browser_run

class LighthouseScoringTests(unittest.TestCase):
    def test_thresholds_and_invalid_data(self):
        values={'performance':.82,'accessibility':.98,'best-practices':.92,'seo':.80}
        payload={'categories':{k:{'score':v} for k,v in values.items()}}
        limits={'performance':80,'accessibility':90,'best-practices':90,'seo':80}
        self.assertTrue(summarize(payload,limits)['passed'])
        payload['categories']['accessibility']['score']=.60
        self.assertFalse(summarize(payload,limits)['passed'])
        with self.assertRaisesRegex(ValueError,'Missing score'):
            summarize({'categories':{}},limits)
    def test_no_implicit_lighthouse_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError,'not installed'):
                run('http://127.0.0.1:44125',Path(tmp),cli_path=str(Path(tmp)/'missing'))
    @unittest.skipUnless(importlib.util.find_spec('playwright'),'Playwright unavailable')
    def test_missing_axe_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture=Path(tmp)/'page.html';fixture.write_text('<!doctype html><title>X</title>')
            with self.assertRaisesRegex(RuntimeError,'axe-core unavailable'):
                browser_run(None,Path(tmp)/'out',html_path=fixture,axe_path=Path(tmp)/'missing.js')
    @unittest.skipUnless(importlib.util.find_spec('playwright'),'Playwright unavailable')
    def test_real_axe_when_dependency_installed(self):
        path=ROOT/'node_modules'/'axe-core'/'axe.min.js'
        if not path.is_file():self.skipTest('npm install not available locally')
        with tempfile.TemporaryDirectory() as tmp:
            fixture=Path(tmp)/'page.html'
            fixture.write_text('<!doctype html><html lang="pt-BR"><head><title>Test</title></head><body><main><h1>Test</h1><button> </button><img src="x.png"></main></body></html>')
            r=browser_run(None,Path(tmp)/'out',html_path=fixture,browser_path=shutil.which('chromium'),axe_path=path)
            self.assertEqual(r['status'],'completed')
            violations=r['viewport_results']['desktop']['axe_core']['violations']
            self.assertTrue(violations)
            self.assertTrue(any(v['id'] in ('button-name','image-alt') for v in violations))

if __name__=='__main__':unittest.main()
