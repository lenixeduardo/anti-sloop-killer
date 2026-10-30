#!/usr/bin/env python3
"""Verify source/index consistency and exhaustive rule ID sequences."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_rules import parse_catalog  # noqa

EXPECTED = {"SA": 87, "IM": 37, "UH": 13, "UC": 35, "NX": 56}


def validate() -> list[str]:
    errors = []
    doc = (ROOT / "references/catalogo-completo.md").read_text(encoding="utf-8")
    parsed = parse_catalog(doc)
    indexed = json.loads((ROOT / "references/rules.json").read_text(encoding="utf-8"))
    if parsed != indexed:
        errors.append("The rules.json index does not match the source Markdown. Run generate_rules.py.")
    for prefix, count in EXPECTED.items():
        ids = {r["id"] for r in parsed["rules"] if r["id"].startswith(prefix + "-")}
        expected = {f"{prefix}-{i:03}" for i in range(1, count+1)}
        if ids != expected:
            errors.append(f"{prefix}: missing={sorted(expected-ids)} unexpected={sorted(ids-expected)}")
    expected_palettes = {f"P{i:02}" for i in range(1, 15)}
    ids = {p["id"] for p in parsed["palettes"]}
    if ids != expected_palettes:
        errors.append(f"Palettes missing: {sorted(expected_palettes - ids)}")
    if len(parsed["rules"]) != sum(EXPECTED.values()):
        errors.append(f"Rule total mismatch: {len(parsed['rules'])}")
    return errors

if __name__ == "__main__":
    failures = validate()
    for message in failures:
        print("ERROR:", message)
    if failures:
        sys.exit(1)
    print("OK: 228 catalog IDs present, 14 palettes present, source/index synchronized.")
