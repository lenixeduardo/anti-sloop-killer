#!/usr/bin/env python3
"""False Positive Guard: validates catalog mappings and gates design warnings.

Findings are candidates, never proof of AI authorship or permission to edit.
Reviewed exceptions are scoped, evidenced and kept visible in the audit.
No third-party packages required.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from fnmatch import fnmatchcase
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Curated detector -> rule mapping. Empty mapping = generic issue without
# an exact counterpart in the catalog, NOT a reason to fabricate an ID.
MAPPINGS = {
    'GRADIENT_TEXT': ('IM-016', 'UH-004'),
    'BLUE_VIOLET_GRADIENT': ('SA-013', 'IM-013', 'UH-003'),
    'UNIVERSAL_ROUNDING': ('SA-037', 'UH-006'),
    'OVERUSED_CENTERING': ('IM-019', 'SA-028'),
    'REPEATED_THREE_COLUMN_GRID': ('SA-029', 'UH-010'),
    'ANIMATE_BOUNCE': ('IM-026',),
    'EXCESSIVE_PULSE': ('SA-044',),
    'BACKDROP_BLUR_EVERYWHERE': ('IM-002',),
    'EXCESSIVE_IMPORTANT': ('NX-045',),
    'LIFT_ON_HOVER': ('UC-026',),
    'EMOJI_AS_ICON_CANDIDATE': ('UH-008', 'UC-034'),
    'REPEATED_TRANSITION_ALL': ('SA-052',),
    'FIXED_VIEWPORT_HEIGHT': (),
    'EXCESSIVE_Z_INDEX': ('NX-045',),
    'PLACEHOLDER_TEXT': ('NX-043',),
    'MISSING_IMG_ALT': ('SA-076',),
    'PLACEHOLDER_HREF': ('NX-043', 'NX-056'),
    'EMPTY_ONCLICK': ('NX-056',),
    'NON_SEMANTIC_CLICK': ('SA-075',),
    'AUTOPLAY_UNMUTED': (),
    'IFRAME_MISSING_TITLE': ('SA-076',),
    'POSITIVE_TABINDEX': ('NX-037',),
    'UNLABELED_INPUT': ('SA-076',),
    'UNLABELED_SELECT': ('SA-076',),
    'UNLABELED_TEXTAREA': ('SA-076',),
    'LOW_STATIC_CONTRAST': ('IM-033',),
    'FOCUS_OUTLINE_REMOVED': ('SA-072',),
    'DUPLICATE_ID': ('SA-034',),
    'EMPTY_IMAGE_SRC': ('NX-056',),
    'ARIA_HIDDEN_FOCUSABLE': ('NX-040',),
    'EXTERNAL_TARGET_REL': (),
    'IMPLICIT_SUBMIT_BUTTON': ('NX-056',),
    'MISSING_DOCUMENT_LANG': ('SA-034',),
    'MISSING_DOCUMENT_TITLE': (),
    'MISSING_VIEWPORT_META': (),
    'UNNAMED_BUTTON': ('SA-076',),
    'UNNAMED_LINK': ('SA-076',),
}
CONTEXTUAL = {
    'GRADIENT_TEXT', 'BLUE_VIOLET_GRADIENT', 'UNIVERSAL_ROUNDING',
    'OVERUSED_CENTERING', 'REPEATED_THREE_COLUMN_GRID', 'ANIMATE_BOUNCE',
    'EXCESSIVE_PULSE', 'BACKDROP_BLUR_EVERYWHERE', 'EXCESSIVE_IMPORTANT',
    'LIFT_ON_HOVER', 'REPEATED_TRANSITION_ALL', 'FIXED_VIEWPORT_HEIGHT',
    'EXCESSIVE_Z_INDEX', 'EXTERNAL_TARGET_REL', 'IMPLICIT_SUBMIT_BUTTON',
}


def load_json(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'JSON object required: {path}')
    return value


def catalog_ids(path=ROOT / 'references/rules.json'):
    rules = load_json(path)['rules']
    ids = [entry['id'] for entry in rules]
    if len(ids) != 228 or len(set(ids)) != 228:
        raise ValueError('Expected 228 unique catalog rule IDs')
    return set(ids)


def check_registry(path=ROOT / 'references/rules.json'):
    available = catalog_ids(path)
    for key, ids in MAPPINGS.items():
        if set(ids) - available or 'UH-013' in ids:
            raise ValueError(f'Invalid mapping: {key} -> {ids}')
    return available


def check_finding(item, available):
    key = item.get('key')
    ids = item.get('source_rules', [])
    if not isinstance(ids, list) or any(not isinstance(x, str) for x in ids):
        raise ValueError(f'Invalid source_rules: {key}')
    if set(ids) - available:
        raise ValueError(f'Unknown catalog ID in {key}: {ids}')
    if 'UH-013' in ids:
        raise ValueError('UH-013 is an exclusion, never a violation')
    if key in MAPPINGS and set(ids) != set(MAPPINGS[key]):
        raise ValueError(f'Mapping mismatch for {key}: {ids}, expected {MAPPINGS[key]}')


def validated_reviews(policy, available):
    if policy.get('schema_version') != 1 or not isinstance(policy.get('reviews'), list):
        raise ValueError('Expected policy schema_version=1 and reviews[]')
    used = set()
    for rev in policy['reviews']:
        if not isinstance(rev, dict) or not isinstance(rev.get('id'), str) or not rev['id'] or rev['id'] in used:
            raise ValueError('Review ID must be unique and nonempty')
        used.add(rev['id'])
        if rev.get('decision') not in ('intentional', 'false_positive'):
            raise ValueError(f"{rev['id']}: invalid review decision")
        for name in ('path', 'reviewed_by', 'rationale', 'evidence'):
            if not isinstance(rev.get(name), str) or not rev[name].strip():
                raise ValueError(f"{rev['id']}: {name} required")
        if rev['path'] in ('*', '**', '**/*') or rev['path'].startswith('/') or '..' in Path(rev['path']).parts:
            raise ValueError(f"{rev['id']}: require scoped relative path")
        keys, rules = rev.get('finding_keys', []), rev.get('rule_ids', [])
        if not isinstance(keys, list) or not isinstance(rules, list) or not (keys or rules):
            raise ValueError(f"{rev['id']}: finding_keys or rule_ids required")
        if any(not isinstance(x, str) or not x for x in keys + rules) or set(rules) - available or 'UH-013' in rules:
            raise ValueError(f"{rev['id']}: invalid key or rule reference")
        if rev.get('expires_on'):
            date.fromisoformat(rev['expires_on'])
        if rev.get('runtime_verified') not in (None, True, False):
            raise ValueError(f"{rev['id']}: runtime_verified must be boolean")
    return policy['reviews']


def matching_review(item, reviews, today):
    hits = []
    for rev in reviews:
        if rev.get('expires_on') and date.fromisoformat(rev['expires_on']) < today:
            continue
        if not fnmatchcase(item.get('file', '').replace('\\', '/'), rev['path']):
            continue
        if rev.get('finding_keys') and item.get('key') not in rev['finding_keys']:
            continue
        if rev.get('rule_ids') and not set(item.get('source_rules', [])) & set(rev['rule_ids']):
            continue
        # P0/P1 findings may only be dismissed as false positives with runtime proof.
        if item.get('severity', '').startswith(('P0', 'P1')) and not (
            rev['decision'] == 'false_positive' and rev.get('runtime_verified') is True
        ):
            continue
        hits.append(rev)
    if len({rev['decision'] for rev in hits}) > 1:
        raise ValueError(f"Conflicting reviews: {item.get('file')}:{item.get('line')}")
    return hits[0] if hits else None


def guard_report(report, *, catalog_path=ROOT / 'references/rules.json', policy=None, today=None):
    available = check_registry(catalog_path)
    reviews = validated_reviews(policy, available) if policy is not None else []
    found = report.get('findings', [])
    if not isinstance(found, list):
        raise ValueError('findings must be an array')
    unique = {}
    for original in found:
        item = dict(original)
        check_finding(item, available)
        signature = (item.get('file', ''), item.get('line', 0), item.get('key', ''))
        if signature not in unique:
            unique[signature] = item
        else:
            existing = unique[signature]
            existing['source_rules'] = sorted(set(existing['source_rules']) | set(item['source_rules']))
            existing['occurrences'] = max(existing.get('occurrences', 1), item.get('occurrences', 1))
    counts = Counter()
    result = dict(report)
    result['findings'] = list(unique.values())
    result['candidate_count'] = len(result['findings'])
    for item in result['findings']:
        rev = matching_review(item, reviews, today or date.today())
        contextual = item.get('key') in CONTEXTUAL or item.get('severity', '').startswith(('P2', 'P3'))
        item['guard_evidence_type'] = 'contextual' if contextual else 'objective_candidate'
        item['mapping_validated'] = True
        item['autofix_permitted'] = False
        if rev:
            item['status'] = rev['decision']
            item['guard_review'] = {k: rev[k] for k in ('id', 'reviewed_by', 'rationale', 'evidence')}
        else:
            item['status'] = 'candidate_not_verified'
            item['review_required'] = ['brand_and_visual_evidence', 'browser_or_runtime_check'] if contextual else ['runtime_or_accessibility_evidence']
        counts[item['status']] += 1
    result['guard'] = {
        'version': 1, 'catalog_rule_count': len(available),
        'policy_reviews': len(reviews), 'counts_by_status': dict(counts),
        'unreviewed_count': counts['candidate_not_verified'],
        'reviewed_count': counts['intentional'] + counts['false_positive'],
        'autofixes_permitted': 0,
        'note': 'All findings retained. Heuristics are not proof of defects or AI authorship.',
    }
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('report', type=Path, help='Static scanner JSON report')
    p.add_argument('--catalog', type=Path, default=ROOT / 'references/rules.json')
    p.add_argument('--policy', type=Path, help='Optional scoped approved review policy')
    p.add_argument('--out', type=Path)
    args = p.parse_args()
    try:
        data = guard_report(load_json(args.report), catalog_path=args.catalog,
                            policy=load_json(args.policy) if args.policy else None)
        output = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output, encoding='utf-8')
        else:
            print(output, end='')
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    main()
