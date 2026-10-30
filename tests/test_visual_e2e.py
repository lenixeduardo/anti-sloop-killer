import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from browser_audit import run as browser_run
from visual_compare import run as visual_run

@unittest.skipUnless(importlib.util.find_spec('playwright'),'Playwright unavailable')
class VisualE2E(unittest.TestCase):
    def test_real_chromium_baseline_and_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            page=folder/'sample.html'
            original='<!doctype html><html lang="pt-BR"><head><title>Portfolio</title><style>body{font-family:Arial;background:white;color:#111}main{max-width:800px;margin:auto}</style></head><body><main><h1>Meu trabalho</h1><p>Portfolio</p></main></body></html>'
            page.write_text(original,encoding='utf-8')
            before=browser_run(None,folder/'before',html_path=page,browser_path=shutil.which('chromium'))
            same=browser_run(None,folder/'same',html_path=page,browser_path=shutil.which('chromium'))
            self.assertEqual(before['status'],'completed');self.assertEqual(same['status'],'completed')
            identical=visual_run(folder/'before',folder/'same',folder/'identical',max_changed_ratio=.005)
            self.assertEqual(identical['status'],'pass',identical)
            page.write_text(original.replace('background:white','background:black'),encoding='utf-8')
            browser_run(None,folder/'after',html_path=page,browser_path=shutil.which('chromium'))
            changed=visual_run(folder/'before',folder/'after',folder/'changed',max_changed_ratio=.005)
            self.assertEqual(changed['status'],'review_required')
            self.assertTrue((folder/'changed'/'desktop-diff.png').is_file())
if __name__=='__main__':unittest.main()
