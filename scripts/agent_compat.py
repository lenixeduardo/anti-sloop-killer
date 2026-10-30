#!/usr/bin/env python3
"""Test Agent Skills installation and scanner operation without impersonating an AI agent.

This performs deterministic compatibility checks. It NEVER claims that Codex,
Claude Code, or Cursor executed a prompt, and it never touches a real user home.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from install import NAME, install_one, target_root, verify

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED = ("codex", "claude", "cursor")
CLI_BINARIES = {"codex": "codex", "claude": "claude", "cursor": "agent"}


def frontmatter_ok(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return False
    end = text.find("\n---\n", 4)
    if end == -1:
        return False
    head = text[4:end].splitlines()
    fields = {line.partition(":")[0].strip(): line.partition(":")[2].strip() for line in head if ":" in line}
    return fields.get("name") == NAME and len(fields.get("description", "")) >= 40


def check_agent(agent: str, *, root: Path = ROOT) -> dict:
    if agent not in SUPPORTED:
        raise ValueError(f"Unsupported agent: {agent}")
    with tempfile.TemporaryDirectory(prefix=f"anti-slop-{agent}-") as temp:
        sandbox = Path(temp)
        project = sandbox / "project"
        project.mkdir()
        userhome = sandbox / "home"
        userhome.mkdir()
        checks = []
        with patch("pathlib.Path.home", return_value=userhome):
            for scope in ("project", "global"):
                dest = target_root(agent, scope, project) / NAME
                install_one(root, dest, force=False, dry_run=False)
                integrity, note = verify(dest)
                metadata = frontmatter_ok(dest / "SKILL.md")
                # Run the INSTALLED skill's real scanner, not the original checkout.
                case = root / "benchmarks" / "fixtures" / "html-portfolio" / "broken.html"
                command = [sys.executable, str(dest / "scripts" / "audit_slop.py"),
                           str(case), "--format", "json"]
                run = subprocess.run(command, capture_output=True, text=True, timeout=35,
                                     env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
                try:
                    data = json.loads(run.stdout)
                    count = data.get("candidate_count", 0)
                except (ValueError, TypeError):
                    count = 0
                checks.append({"scope": scope, "expected_discovery_path": str(dest.relative_to(project)) if scope == "project" else str(dest.relative_to(userhome)),
                               "manifest_ok": integrity, "manifest_detail": note,
                               "frontmatter_ok": metadata, "scanner_exit_code": run.returncode,
                               "scanner_candidates": count,
                               "passed": integrity and metadata and run.returncode == 0 and count > 0})
    return {"schema": "anti-ai-slop/agent-compat/v1", "agent": agent,
            "status": "compatible_not_executed" if all(c["passed"] for c in checks) else "failed",
            "checks": checks, "runtime_binary_present": shutil.which(CLI_BINARIES[agent]) is not None,
            "runtime_executed": False,
            "limitation": "Filesystem discovery and scanner execution validated; real agent invocation requires authenticated CLI and separate transcript."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=(*SUPPORTED, "all"), default="all")
    parser.add_argument("--out", type=Path, default=Path("reports/agent-compat.json"))
    parser.add_argument("--require-runtime", action="store_true", help="Fail if no authenticated, separately recorded real-agent invocation exists")
    args = parser.parse_args()
    agents = SUPPORTED if args.agent == "all" else (args.agent,)
    result = {"schema": "anti-ai-slop/agent-compat-report/v1", "results": [check_agent(a) for a in agents]}
    result["approved_for_compatibility"] = all(x["status"] == "compatible_not_executed" for x in result["results"])
    result["approved_for_real_agent_runtime"] = False
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.out), "compatibility": result["approved_for_compatibility"],
                      "real_agent_runtime": False}, ensure_ascii=False))
    return 0 if result["approved_for_compatibility"] and not args.require_runtime else 1


if __name__ == "__main__":
    raise SystemExit(main())
