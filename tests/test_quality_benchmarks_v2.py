"""Independent assertions over fixed benchmark gold; fixture authorship is disclosed."""
from __future__ import annotations
import sys
import unittest
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_accessibility_benchmark import run as access_run
from run_structural_benchmark import run as structural_run

def has_ts():
    if not shutil.which('node'):
        return False
    return subprocess.run(['node','-e',"try { require('typescript'); } catch(e) { process.exit(1) }"],
                          capture_output=True).returncode == 0

class AccessibilityExpansion(unittest.TestCase):
    @unittest.skipUnless(has_ts(), "TypeScript AST module unavailable")
    def test_new_objective_detectors_meet_precision_and_recall(self):
        report=access_run(use_ast=True)
        self.assertEqual(report['frameworks'],5)
        self.assertEqual(len(report['cases']),10)
        self.assertEqual(report['metrics']['tp'],15)
        self.assertEqual(report['metrics']['fp'],0)
        self.assertEqual(report['metrics']['fn'],0)
        self.assertGreaterEqual(report['metrics']['precision'],.95)
        self.assertGreaterEqual(report['metrics']['recall'],.90)
        self.assertTrue(all(not case['read_errors'] for case in report['cases']))
    def test_clean_cases_stay_clean(self):
        report=access_run(use_ast=False)
        self.assertTrue(all(not case['observed'] for case in report['cases'] if not case['expected']))
    def test_fallback_measurement_does_not_claim_full_ast_coverage(self):
        report=access_run(use_ast=False)
        self.assertLess(report['metrics']['recall'],1.0)
        self.assertEqual(report['metrics']['fp'],0)

class StructuralFixBenchmark(unittest.TestCase):
    @unittest.skipUnless(has_ts(), "TypeScript AST module unavailable")
    def test_multi_stack_preservation_and_tested_changes(self):
        report=structural_run()
        self.assertEqual(report['status'],'passed')
        self.assertEqual((report['passed'],report['tested']),(5,5))
        self.assertTrue(all(row['brand_and_copy_preserved'] and row['only_approved_edits_changed'] and row['finding_removed'] for row in report['results']))
    @unittest.skipUnless(has_ts(), "TypeScript AST module unavailable")
    def test_rollback_and_baseline_integrity(self):
        report=structural_run()
        self.assertEqual(len(report['negative_tests']),2)
        self.assertTrue(all(row['passed'] for row in report['negative_tests']))

if __name__=='__main__':unittest.main()
