import functools
import http.server
import importlib.util
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from browser_audit import run

@unittest.skipUnless(importlib.util.find_spec('playwright') is not None, 'Playwright não instalado')
class BrowserE2E(unittest.TestCase):
    def test_three_viewports_and_evidence(self):
        folder=ROOT/'tests'/'fixtures'/'site'
        handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(folder))
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
        t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                chromium=shutil.which('chromium')
                result=run(None,Path(tmp),browser_path=chromium,html_path=folder/'index.html',interaction_spec=[{'selector':'button[aria-label="Abrir menu"]','expect_selector':'#answer','expect_text':'OK'}])
                self.assertEqual(result['status'],'completed')
                self.assertEqual(set(result['viewport_results']),{'desktop','tablet','mobile'})
                for viewport in result['viewport_results'].values():
                    self.assertIsNone(viewport['http_status'])
                    self.assertTrue(Path(viewport['screenshot']).is_file())
                    self.assertEqual(len(viewport['checks']['broken_images']),1)
                    self.assertEqual(len(viewport['checks']['dead_links']),1)
                    self.assertFalse(viewport['checks']['horizontal_overflow'])
                    self.assertTrue(viewport['interactions'][0]['passed'])
        finally:
            server.shutdown();server.server_close()

if __name__=='__main__':unittest.main()
