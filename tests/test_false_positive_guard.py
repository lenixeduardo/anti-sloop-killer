"""Offline False Positive Guard regression tests (no fabricated browser evidence)."""
import json
from datetime import date
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from false_positive_guard import MAPPINGS, check_registry, guard_report
from audit_slop import DETECTORS, audit


def candidate(key='BLUE_VIOLET_GRADIENT', ids=None, severity='P3', filename='src/Hero.tsx', line=5):
    return {'key': key, 'source_rules': list(MAPPINGS[key] if ids is None else ids),
            'severity': severity, 'file': filename, 'line': line, 'occurrences': 1,
            'status': 'candidate_not_verified'}


def policy(**edits):
    rev = {'id': 'APPROVAL-001', 'decision': 'intentional', 'path': 'src/Hero.tsx',
           'finding_keys': ['BLUE_VIOLET_GRADIENT'], 'rule_ids': ['SA-013'],
           'reviewed_by': 'owner', 'rationale': 'Approved brand gradient',
           'evidence': 'brand/approved-colors.md'}
    rev.update(edits)
    return {'schema_version': 1, 'reviews': [rev]}


def run(*items, policy_data=None):
    return guard_report({'findings': list(items)}, policy=policy_data)


class FalsePositiveGuardTests(unittest.TestCase):
    def test_catalog_and_every_static_detector_mapping(self):
        self.assertEqual(len(check_registry()), 228)
        for key, _, _, ids, *_ in DETECTORS:
            self.assertEqual(set(ids), set(MAPPINGS[key]), key)

    def test_aesthetic_candidate_is_not_defect(self):
        result = run(candidate())
        self.assertEqual(result['findings'][0]['status'], 'candidate_not_verified')
        self.assertFalse(result['findings'][0]['autofix_permitted'])
        self.assertEqual(result['guard']['unreviewed_count'], 1)

    def test_exception_scoped_to_specific_file(self):
        result = run(candidate(), candidate(filename='src/Other.tsx'), policy_data=policy())
        self.assertEqual([f['status'] for f in result['findings']],
                         ['intentional', 'candidate_not_verified'])
        self.assertEqual(result['guard']['reviewed_count'], 1)

    def test_expired_exception_does_not_suppress(self):
        result = guard_report({'findings': [candidate()]},
                              policy=policy(expires_on='2025-01-01'), today=date(2026, 10, 30))
        self.assertEqual(result['guard']['unreviewed_count'], 1)

    def test_critical_findings_cannot_be_marked_intentional(self):
        finding = candidate('MISSING_IMG_ALT', severity='P1_CANDIDATE')
        review = policy(finding_keys=['MISSING_IMG_ALT'], rule_ids=['SA-076'])
        self.assertEqual(run(finding, policy_data=review)['guard']['reviewed_count'], 0)

    def test_critical_false_positive_requires_runtime_evidence(self):
        finding = candidate('MISSING_IMG_ALT', severity='P1_CANDIDATE')
        rev = policy(decision='false_positive', finding_keys=['MISSING_IMG_ALT'], rule_ids=['SA-076'])
        self.assertEqual(run(finding, policy_data=rev)['guard']['reviewed_count'], 0)
        rev['reviews'][0]['runtime_verified'] = True
        self.assertEqual(run(finding, policy_data=rev)['findings'][0]['status'], 'false_positive')

    def test_registry_mismatch_and_exclusion_fail_closed(self):
        for ids in (['NX-031'], ['UH-013'], ['NX-999']):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                run(candidate(ids=ids))

    def test_rejects_unscoped_or_unjustified_exception(self):
        for edits in ({'path': '*'}, {'rationale': ''}, {'evidence': ''},
                      {'reviewed_by': ''}, {'rule_ids': ['NX-999']},
                      {'decision': 'confirmed'}):
            with self.subTest(edits=edits), self.assertRaises(ValueError):
                run(candidate(), policy_data=policy(**edits))

    def test_conflicts_are_explicit(self):
        review1 = policy()['reviews'][0]
        review2 = dict(review1, id='APPROVAL-002', decision='false_positive')
        with self.assertRaisesRegex(ValueError, 'Conflicting reviews'):
            run(candidate(), policy_data={'schema_version': 1, 'reviews': [review1, review2]})

    def test_dedupe_same_detector_same_position_only(self):
        result = run(candidate(), candidate(), candidate(line=6),
                     candidate(key='GRADIENT_TEXT', ids=['IM-016', 'UH-004']))
        self.assertEqual(result['candidate_count'], 3)
        self.assertEqual(result['guard']['unreviewed_count'], 3)

    def test_unmapped_generic_detection_does_not_claim_catalog_id(self):
        result = run(candidate('FIXED_VIEWPORT_HEIGHT', ids=[]))
        self.assertEqual(result['findings'][0]['source_rules'], [])

    def test_project_scoped_policy_is_loaded_by_integrated_scanner(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'src').mkdir()
            (root / '.anti-ai-slop').mkdir()
            (root / 'src' / 'Hero.tsx').write_text(
                "export const Hero = () => <div className='from-blue-600 to-purple-600' />;\n",
                encoding='utf-8'
            )
            (root / '.anti-ai-slop' / 'false-positive-guard.json').write_text(
                json.dumps(policy()), encoding='utf-8'
            )
            output = audit(root)
            matching = [x for x in output['findings'] if x['key'] == 'BLUE_VIOLET_GRADIENT']
            self.assertEqual(len(matching), 1)
            self.assertEqual(matching[0]['status'], 'intentional')
            self.assertEqual(output['guard']['reviewed_count'], 1)


if __name__ == '__main__':
    unittest.main()
