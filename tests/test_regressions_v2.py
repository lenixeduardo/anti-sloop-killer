"""Adversarial regression suite for the production scanner."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_slop import scan_text,audit,mask_comments
from browser_audit import validate_url

class ScannerRegression(unittest.TestCase):
    def keys(self,code,ext='page.tsx'):
        return {x['key'] for x in scan_text(code,ext)}

    def test_html_comments_not_flagged(self):
        self.assertEqual(self.keys('<!-- <img src="bad"> <a href="#">bad</a> -->','index.html'),set())
    def test_css_comments_not_flagged(self):
        self.assertEqual(self.keys('/* bg-clip-text text-transparent */','style.css'),set())
    def test_inline_js_comments_not_flagged(self):
        self.assertEqual(self.keys("const x = true // <img src=\"bad\">"),set())
    def test_js_comments_not_flagged(self):
        self.assertEqual(self.keys('// <img src="bad">\n// href="#"'),set())
    def test_urls_inside_attributes_retained(self):
        self.assertEqual(self.keys('<img src="https://site.test/a.png" alt="ok" />'),set())
    def test_next_image(self):
        self.assertIn('MISSING_IMG_ALT',self.keys('<Image src="/x.png" width={200} height={200} />'))
    def test_next_image_with_alt(self):
        self.assertNotIn('MISSING_IMG_ALT',self.keys('<Image src="/x.png" alt="x" />'))
    def test_jsx_expression_dead_link(self):
        self.assertIn('PLACEHOLDER_HREF',self.keys('<a href={"#"}>go</a>'))
    def test_comment_only_handler(self):
        self.assertIn('EMPTY_ONCLICK',self.keys('<button onClick={() => {/* todo */}}>Go</button>'))
    def test_nonsemantic_click(self):
        self.assertIn('NON_SEMANTIC_CLICK',self.keys('<div onClick={() => open()}>Open</div>'))
    def test_nonsemantic_click_with_keyboard(self):
        self.assertNotIn('NON_SEMANTIC_CLICK',self.keys('<div role="button" tabIndex={0} onKeyDown={handle} onClick={handle}>Open</div>'))
    def test_iframe_title(self):
        self.assertIn('IFRAME_MISSING_TITLE',self.keys('<iframe src="/video"></iframe>'))
    def test_astro_and_vue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'src.astro').write_text('<img src="/bad.png">',encoding='utf-8')
            (root/'comp.vue').write_text('<template><a href="#">test</a></template>',encoding='utf-8')
            result=audit(root)
            self.assertEqual(result['files_scanned'],2)
            self.assertEqual(result['candidate_count'],2)
    def test_ast_ignores_jsx_inside_string_and_detects_real_tag(self):
        import shutil
        if not shutil.which('node'):self.skipTest('Node não disponível')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'page.tsx').write_text('const demo = `<img src="fake" />`;\nexport const C = () => <Image src="/real.png" />;',encoding='utf-8')
            result=audit(root,use_ast=True)
            if result['read_errors']:
                self.skipTest('TypeScript parser não instalado')
            self.assertEqual(result['ast_files_scanned'],1)
            self.assertEqual([x['key'] for x in result['findings']].count('MISSING_IMG_ALT'),1)

    def test_symlink_outside_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            root=path/'src';root.mkdir()
            outside=path/'outside.tsx';outside.write_text('<img src="bad">')
            (root/'link.tsx').symlink_to(outside)
            result=audit(root)
            self.assertEqual(result['files_scanned'],0)
            self.assertEqual(result['unsafe_symlinks_skipped'],1)
    def test_deterministic_findings(self):
        source='<img src="x">\n<a href={"#"}>go</a>'
        self.assertEqual(scan_text(source,'a.tsx'),scan_text(source,'a.tsx'))
    def test_color_alone_unchanged(self):
        self.assertEqual(self.keys('const primary = "#F97316"'),set())
    def test_browser_url_validation(self):
        for bad in ('file:///etc/passwd','javascript:alert(1)','https://user:pass@example.com'):
            with self.assertRaises(ValueError):validate_url(bad)

if __name__=='__main__':unittest.main()
