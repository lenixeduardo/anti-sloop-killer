import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from visual_compare import compare,run

class VisualDiffTests(unittest.TestCase):
    def test_identical_passes_and_creates_diff(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);a=p/'a.png';b=p/'b.png'
            Image.new('RGB',(80,70),(255,255,255)).save(a)
            Image.new('RGB',(80,70),(255,255,255)).save(b)
            r=compare(a,b,p/'diff.png')
            self.assertTrue(r['passed']);self.assertEqual(r['changed_ratio'],0)
            self.assertTrue((p/'diff.png').is_file())
    def test_small_change_flags_and_partial_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);a=p/'a.png';b=p/'b.png'
            Image.new('RGB',(20,20),'white').save(a)
            image=Image.new('RGB',(20,20),'white');image.putpixel((1,1),(0,0,0));image.save(b)
            r=compare(a,b,p/'diff.png',max_changed_ratio=.001)
            self.assertFalse(r['passed']);self.assertEqual(r['status'],'review_required')
            self.assertAlmostEqual(r['changed_ratio'],.0025)
    def test_dimension_mismatch_and_missing_baseline_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);a=p/'a.png';b=p/'b.png';Image.new('RGB',(20,20),'white').save(a);Image.new('RGB',(10,10),'white').save(b)
            self.assertEqual(compare(a,b,p/'diff.png')['status'],'different_dimensions')
            out=run(p/'nonexistent',p/'other',p/'report')
            self.assertEqual(out['status'],'review_required')
            self.assertTrue(all(x['status']=='missing_evidence' for x in out['results'].values()))

if __name__=='__main__':unittest.main()
