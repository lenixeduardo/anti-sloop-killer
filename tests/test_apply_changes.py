"""Prove that exact edits change only approved files and roll back on failures."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from apply_changes import apply, prepare

class ApplyChangesTests(unittest.TestCase):
    def setup_project(self, folder):
        project=Path(folder)/'project';project.mkdir()
        page=project/'index.html'
        page.write_text('<a href="#">Buy</a>\n',encoding='utf-8')
        before=page.read_bytes()
        proposal={'changes':[{'path':'index.html','finding_id':'STATIC-0001',
             'expected_sha256':hashlib.sha256(before).hexdigest(),
             'search':'<a href="#">Buy</a>', 'replace':'<a href="/buy">Buy</a>'}]}
        return project,page,proposal,before
    def test_preview_is_readonly(self):
        with tempfile.TemporaryDirectory() as tmp:
            project,page,plan,before=self.setup_project(tmp)
            result=apply(project,plan)
            self.assertEqual(result['status'],'preview')
            self.assertIn('+<a href="/buy">',result['diff'])
            self.assertEqual(page.read_bytes(),before)
    def test_approved_change_with_acceptance_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            project,page,plan,_=self.setup_project(tmp)
            check=[sys.executable,'-c','from pathlib import Path; assert \'href="/buy"\' in Path("index.html").read_text()']
            result=apply(project,plan,approved=True,checks=[check])
            self.assertEqual(result['status'],'applied_verified')
            self.assertIn('href="/buy"',page.read_text())
    def test_failed_check_rolls_back_exact_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project,page,plan,before=self.setup_project(tmp)
            result=apply(project,plan,approved=True,checks=[[sys.executable,'-c','raise SystemExit(7)']])
            self.assertEqual(result['status'],'rolled_back')
            self.assertEqual(page.read_bytes(),before)
    def test_baseline_drift_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            project,page,plan,_=self.setup_project(tmp)
            page.write_text('changed')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):prepare(project,plan)
    def test_traversal_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            project,page,plan,_=self.setup_project(tmp)
            plan['changes'][0]['path']='../outside.html'
            with self.assertRaisesRegex(ValueError,'traversal'):prepare(project,plan)
    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            project,page,plan,_=self.setup_project(tmp)
            other=Path(tmp)/'outside.html';other.write_text(page.read_text())
            link=project/'link.html';link.symlink_to(other)
            plan['changes'][0]['path']='link.html'
            with self.assertRaisesRegex(ValueError,'Symlink'):prepare(project,plan)
    def test_ambiguous_match_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            project,page,plan,_=self.setup_project(tmp)
            plan['changes'][0]['search']='a'
            with self.assertRaisesRegex(ValueError,'occur once'):prepare(project,plan)
    def test_no_approval_no_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            project,page,plan,before=self.setup_project(tmp)
            result=apply(project,plan,approved=False,checks=[[sys.executable,'-c','raise SystemExit(7)']])
            self.assertEqual(result['status'],'preview')
            self.assertEqual(page.read_bytes(),before)

if __name__=='__main__':unittest.main()
