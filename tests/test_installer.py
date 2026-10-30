"""Installer integration tests: real copies to disposable workspaces."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install.py"


def invoke(*args, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
    )


class InstallerTests(unittest.TestCase):
    def test_project_install_and_verify(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            r = invoke("--agent", "codex", "--scope", "project", "--project", str(p))
            self.assertEqual(r.returncode, 0, r.stderr)
            dest = p / ".agents/skills/anti-ai-slop"
            self.assertTrue((dest / "SKILL.md").is_file())
            self.assertTrue((dest / "assets/icon.png").is_file())
            self.assertTrue((dest / "scripts/install.ps1").is_file())
            self.assertFalse((dest / "scripts/__pycache__").exists())
            r2 = invoke("--agent", "codex", "--scope", "project", "--project", str(p), "--verify")
            self.assertEqual(r2.returncode, 0, r2.stderr)

    def test_refuse_overwrite_and_force_backup(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            args = ("--agent", "cursor", "--scope", "project", "--project", str(p))
            self.assertEqual(invoke(*args).returncode, 0)
            dest = p / ".cursor/skills/anti-ai-slop"
            (dest / "custom-note.txt").write_text("Do not lose this", encoding="utf-8")
            r = invoke(*args)
            self.assertEqual(r.returncode, 2)
            self.assertEqual(invoke(*args, "--force").returncode, 0)
            backups = list((p / ".cursor/skills").glob("anti-ai-slop.backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / "custom-note.txt").read_text(), "Do not lose this")
            self.assertTrue((dest / "SKILL.md").is_file())

    def test_dry_run_and_multiagent(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            args = ("--agent", "all", "--scope", "project", "--project", str(p))
            dry = invoke(*args, "--dry-run")
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertFalse((p / ".agents").exists())
            self.assertEqual(invoke(*args).returncode, 0)
            self.assertTrue((p / ".agents/skills/anti-ai-slop/SKILL.md").exists())
            self.assertTrue((p / ".claude/skills/anti-ai-slop/SKILL.md").exists())
            self.assertTrue((p / ".cursor/skills/anti-ai-slop/SKILL.md").exists())

    def test_global_uses_user_agents_directory(self):
        if os.name == "nt":
            self.skipTest("HOME substitution here targets POSIX only")
        with tempfile.TemporaryDirectory() as td:
            env = dict(os.environ, HOME=td)
            r = invoke("--agent", "codex", "--scope", "global", env=env)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((Path(td) / ".agents/skills/anti-ai-slop/SKILL.md").exists())

    def test_missing_project_is_not_created(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "does-not-exist"
            r = invoke("--scope", "project", "--project", str(p))
            self.assertEqual(r.returncode, 2)
            self.assertFalse(p.exists())

    def test_cannot_install_into_source_itself(self):
        r = invoke("--scope", "project", "--project", str(ROOT), "--dry-run")
        # dry-run protects projects too, no nested installation even in preview.
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
