"""Unit and regression tests for the self-contained skill package."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_slop import audit, scan_text
from validate_catalog import validate


class CatalogTests(unittest.TestCase):
    def test_catalog_complete(self):
        self.assertEqual(validate(), [])

    def test_catalog_includes_orange_palettes(self):
        import json
        data = json.loads((ROOT / "references/rules.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["rules"]), 228)
        self.assertEqual(len(data["palettes"]), 14)
        self.assertTrue(any(p["id"] == "P09" for p in data["palettes"]))
        self.assertTrue(any(p["id"] == "P14" for p in data["palettes"]))


class ScannerTests(unittest.TestCase):
    def test_detects_gradient_and_dead_link(self):
        txt = '<a href="#">Start</a>\n<h1 class="bg-clip-text text-transparent from-blue-600 to-purple-600">AI</h1>'
        keys = {x["key"] for x in scan_text(txt, "page.tsx")}
        self.assertIn("PLACEHOLDER_HREF", keys)
        self.assertIn("GRADIENT_TEXT", keys)
        self.assertIn("BLUE_VIOLET_GRADIENT", keys)

    def test_orange_is_not_a_violation(self):
        txt = '<button style={{ backgroundColor: "#F97316" }}>Comprar</button>'
        self.assertEqual(scan_text(txt, "page.tsx"), [])

    def test_image_alt_is_checked(self):
        txt = '<img src="/banner.webp" />\n<img src="/decoration.png" alt="" />'
        findings = scan_text(txt, "index.html")
        self.assertEqual([f["key"] for f in findings], ["MISSING_IMG_ALT"])

    def test_reports_are_reproducible_except_clock(self):
        with tempfile.TemporaryDirectory() as work:
            p = Path(work) / "src"
            p.mkdir()
            (p / "example.tsx").write_text('<a href="#">Teste</a>\n', encoding="utf-8")
            results = audit(p)
            self.assertEqual(results["files_scanned"], 1)
            self.assertEqual(results["candidate_count"], 1)
            self.assertEqual(results["findings"][0]["id"], "STATIC-0001")


if __name__ == "__main__":
    unittest.main()
