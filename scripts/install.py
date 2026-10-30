#!/usr/bin/env python3
"""Install anti-ai-slop as a user or project Agent Skill (stdlib-only)."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile
from datetime import datetime, timezone

NAME = "anti-ai-slop"
AGENTS = ("codex", "claude", "cursor", "agents")
PARTS = ("SKILL.md", "README.md", "ABOUT.md", "MANIFEST.sha256", "references", "scripts", "templates", "tests", "assets", "agents")


def skill_source() -> Path:
    root = Path(__file__).resolve().parent.parent
    if not (root / "SKILL.md").is_file():
        raise RuntimeError(f"SKILL.md ausente em {root}")
    if not (root / "references" / "rules.json").is_file():
        raise RuntimeError(f"Catalogo ausente em {root}")
    return root


def target_root(agent: str, scope: str, project: Path) -> Path:
    home = Path.home()
    if scope == "project":
        return project / {"codex": ".agents", "claude": ".claude", "cursor": ".cursor", "agents": ".agents"}[agent] / "skills"
    return home / {"codex": ".agents", "claude": ".claude", "cursor": ".cursor", "agents": ".agents"}[agent] / "skills"


def ignore_entries(_: str, entries: list[str]) -> list[str]:
    return [name for name in entries if name in {"__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "node_modules", ".git", ".DS_Store"} or name.endswith((".pyc", ".pyo"))]


def verify(target: Path) -> tuple[bool, str]:
    manifest = target / "MANIFEST.sha256"
    if not manifest.is_file():
        return False, "MANIFEST.sha256 ausente"
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, rel = line.split("  ", 1)
        except ValueError:
            return False, "linha do manifesto invalida"
        # Manifest is generated from trusted files but cannot escape the skill root.
        candidate = (target / rel).resolve()
        if target.resolve() not in candidate.parents or not candidate.is_file():
            return False, f"arquivo ausente ou inseguro: {rel}"
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual != expected:
            return False, f"hash incorreto: {rel}"
    return True, "integridade SHA-256 OK"


def install_one(src: Path, dest: Path, *, force: bool, dry_run: bool) -> str:
    if src == dest or src in dest.parents:
        raise RuntimeError("Destino esta dentro da propria pasta da skill; escolha outro projeto.")
    if dest.exists() and not force:
        raise FileExistsError(f"{dest} ja existe. Use --force para atualizar (criara backup).")
    if dry_run:
        return f"DRY-RUN: {src} -> {dest}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    stage_base = Path(tempfile.mkdtemp(prefix=f".{NAME}-stage-", dir=str(dest.parent)))
    staged = stage_base / NAME
    old = None
    try:
        staged.mkdir()
        for part in PARTS:
            source = src / part
            if not source.exists():
                raise RuntimeError(f"Arquivo necessario nao encontrado: {source}")
            if source.is_dir():
                shutil.copytree(source, staged / part, ignore=ignore_entries)
            else:
                shutil.copy2(source, staged / part)
        ok, message = verify(staged)
        if not ok:
            raise RuntimeError(message)
        if dest.exists():
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            old = dest.parent / f"{NAME}.backup-{timestamp}"
            suffix = 1
            while old.exists():
                old = dest.parent / f"{NAME}.backup-{timestamp}-{suffix}"
                suffix += 1
            dest.rename(old)
        try:
            staged.rename(dest)
        except Exception:
            if old is not None and old.exists() and not dest.exists():
                old.rename(dest)
            raise
        backup = f" | backup: {old}" if old else ""
        return f"INSTALADO: {dest}{backup}"
    finally:
        shutil.rmtree(stage_base, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Instalar skill anti-ai-slop sem dependencias externas")
    p.add_argument("--agent", choices=(*AGENTS, "all"), default="codex", help="Agente de destino; all instala Codex, Claude e Cursor")
    p.add_argument("--scope", choices=("project", "global"), default="project", help="project = repositorio, global = usuario local")
    p.add_argument("--project", default=".", help="Diretorio raiz do projeto (quando --scope project)")
    p.add_argument("--force", action="store_true", help="Substitui instalacao existente e guarda backup")
    p.add_argument("--dry-run", action="store_true", help="Exibe destinos sem copiar arquivos")
    p.add_argument("--verify", action="store_true", help="Confere se a skill ja esta instalada corretamente")
    args = p.parse_args(argv)
    try:
        src = skill_source()
        project = Path(args.project).expanduser().resolve()
        if args.scope == "project" and not project.is_dir():
            raise RuntimeError(f"Projeto nao existe: {project}")
        targets = ["codex", "claude", "cursor"] if args.agent == "all" else [args.agent]
        dests = list(dict.fromkeys(target_root(a, args.scope, project) / NAME for a in targets))
        if args.verify:
            bad = False
            for dest in dests:
                ok, info = verify(dest)
                print(f"{'OK' if ok else 'FALHA'}: {dest} ({info})")
                bad |= not ok
            return 1 if bad else 0
        if not args.force and not args.dry_run:
            occupied = [str(dest) for dest in dests if dest.exists()]
            if occupied:
                raise FileExistsError("Instalacao existente: " + ", ".join(occupied) + ". Use --force para atualizar com backup.")
        for dest in dests:
            print(install_one(src, dest, force=args.force, dry_run=args.dry_run))
        return 0
    except (RuntimeError, OSError, FileExistsError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
