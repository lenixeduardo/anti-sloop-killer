import functools
import http.server
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from lighthouse_audit import run

class LighthouseE2E(unittest.TestCase):
    def test_lighthouse_on_local_fixture(self):
        cli=ROOT/'node_modules'/'.bin'/'lighthouse'
        if not cli.is_file():self.skipTest('Lighthouse optional dependency not installed')
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            (p/'index.html').write_text('<!doctype html><html lang="pt-BR"><head><title>Portfolio</title><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><main><h1>Bem-vindo</h1><p>Site real</p></main></body></html>',encoding='utf-8')
            handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(p))
            server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
            t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
            try:
                result=run(f'http://127.0.0.1:{server.server_port}/',p/'lighthouse',chrome_path=shutil.which('chromium'),thresholds={k:0 for k in ('performance','accessibility','best-practices','seo')})
                self.assertTrue(result['passed'])
                self.assertEqual(set(result['scores']),{'performance','accessibility','best-practices','seo'})
                self.assertTrue((p/'lighthouse'/'lighthouse-raw.json').is_file())
            finally:server.shutdown();server.server_close()
if __name__=='__main__':unittest.main()
