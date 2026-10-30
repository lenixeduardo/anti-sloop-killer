#!/usr/bin/env python3
"""A low-noise static pre-screen of likely website AI-slop or quality issues.

This is a candidate detector, not a repair tool, provenance classifier, brand judge,
accessibility audit or replacement for browser testing. No source code is mutated.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SUFFIXES = {".tsx", ".jsx", ".ts", ".js", ".css", ".scss", ".sass", ".html", ".vue", ".svelte"}
SKIP = {"node_modules", ".next", "dist", "build", "coverage", ".git", "vendor", ".nuxt", ".svelte-kit", ".turbo"}

# Candidates must be reviewed in context. Every regex maps to a source catalog rule.
DETECTORS = [
    {
        "key": "GRADIENT_TEXT", "pattern": r"(?:bg-clip-text[^\n]{0,120}text-transparent|text-transparent[^\n]{0,120}bg-clip-text|background-clip\s*:\s*text)",
        "min_occ": 1, "rules": ["IM-016", "UH-004"], "severity": "P2", "confidence": "medium",
        "note": "Texto com gradiente: investigar intenção, contraste e identidade; não remover automaticamente."
    },
    {
        "key": "BLUE_VIOLET_GRADIENT", "pattern": r"(?:from-(?:blue|indigo)-\d{2,3}[^\n]{0,150}to-(?:purple|violet|fuchsia)-\d{2,3}|linear-gradient\([^)]{0,200}#(?:2563eb|6366f1)[^)]{0,160}#(?:8b5cf6|a855f7))",
        "min_occ": 1, "rules": ["SA-013", "IM-013", "UH-003"], "severity": "P2", "confidence": "low",
        "note": "Gradiente azul/violeta: somente problemático se for default não justificado pela marca."
    },
    {
        "key": "UNIVERSAL_ROUNDING", "pattern": r"\brounded-(?:2xl|3xl|full)\b",
        "min_occ": 4, "rules": ["SA-037", "UH-006"], "severity": "P3", "confidence": "low",
        "note": "Uso frequente de raios grandes; conferir variedade de papéis dos componentes."
    },
    {
        "key": "OVERUSED_CENTERING", "pattern": r"\btext-center\b",
        "min_occ": 5, "rules": ["IM-019", "SA-028"], "severity": "P3", "confidence": "low",
        "note": "Alinhamento central recorrente no arquivo; comparar com semântica do conteúdo e composição."
    },
    {
        "key": "REPEATED_THREE_COLUMN_GRID", "pattern": r"\b(?:grid-cols-3|grid-template-columns\s*:\s*repeat\(3)\b",
        "min_occ": 3, "rules": ["SA-029", "UH-010"], "severity": "P3", "confidence": "low",
        "note": "Grid de três colunas repetido; verificar se conteúdo demanda outra estrutura."
    },
    {
        "key": "ANIMATE_BOUNCE", "pattern": r"\banimate-bounce\b|cubic-bezier\(\s*0\.68\s*,\s*-0\.55",
        "min_occ": 1, "rules": ["IM-026"], "severity": "P3", "confidence": "low",
        "note": "Bounce/elástico presente; avaliar intenção e acessibilidade do movimento."
    },
    {
        "key": "EXCESSIVE_PULSE", "pattern": r"\banimate-pulse\b",
        "min_occ": 3, "rules": ["SA-044"], "severity": "P3", "confidence": "low",
        "note": "Pulse frequente; confirmar se estado de loading real requer esse efeito."
    },
    {
        "key": "BACKDROP_BLUR_EVERYWHERE", "pattern": r"\bbackdrop-blur(?:-[a-z0-9]+)?\b|backdrop-filter\s*:\s*blur\(",
        "min_occ": 4, "rules": ["IM-002", "UH-013"], "severity": "P3", "confidence": "low",
        "note": "Blur recorrente; UH-013 alerta contra penalizar glassmorphism automaticamente."
    },
    {
        "key": "EXCESSIVE_IMPORTANT", "pattern": r"!important\b",
        "min_occ": 4, "rules": ["NX-045"], "severity": "P2", "confidence": "low",
        "note": "Muitos !important no mesmo arquivo; revisar arquitetura CSS sem alterar a marca."
    },
    {
        "key": "LIFT_ON_HOVER", "pattern": r"\bhover:-translate-y-(?:\d+|px)\b|:hover\s*\{[^}]{0,180}translateY\s*\(\s*-",
        "min_occ": 4, "rules": ["UC-026"], "severity": "P3", "confidence": "low",
        "note": "Hover lift repetitivo; só reduzir se for efeito automático não aprovado."
    },
    {
        "key": "PLACEHOLDER_HREF", "pattern": r"\bhref\s*=\s*['\"](?:#|javascript:void\(0\))['\"]",
        "min_occ": 1, "rules": ["NX-043", "NX-056"], "severity": "P0_CANDIDATE", "confidence": "medium",
        "note": "Link pode ser placeholder; verificar ação real. href=# pode ser válido como volta ao topo."
    },
    {
        "key": "EMOJI_AS_ICON_CANDIDATE", "pattern": r"(?:(?:<span|<button|<div)[^>]*>\s*[\U0001F300-\U0001FAFF][^<]{0,6}<|['\"][\U0001F300-\U0001FAFF]['\"])",
        "min_occ": 1, "rules": ["UH-008", "UC-034"], "severity": "P2", "confidence": "medium",
        "note": "Emoji possivelmente usado como ícone; verificar contexto antes de trocar por SVG."
    },
    {
        "key": "REPEATED_TRANSITION_ALL", "pattern": r"\btransition-all\b",
        "min_occ": 6, "rules": ["NX-048"], "severity": "P3", "confidence": "low",
        "note": "Uso frequente de transition-all; verificar propriedades animadas e desempenho."
    },
]

IMG_RE = re.compile(r"<img\b[^>]*>", re.I | re.S)
ALT_RE = re.compile(r"\balt\s*=", re.I)
EMPTY_CLICK_RE = re.compile(r"\bonClick\s*=\s*\{\s*(?:\(\s*\)\s*=>\s*\{\s*\}|\(\s*\)\s*=>\s*undefined)\s*\}")


def line_of(src: str, offset: int) -> int:
    return src.count("\n", 0, offset) + 1


def scan_text(src: str, filename: str) -> list[dict]:
    results = []
    for detector in DETECTORS:
        hits = list(re.finditer(detector["pattern"], src, re.I | re.S if detector["key"] == "LIFT_ON_HOVER" else re.I))
        if len(hits) < detector["min_occ"]:
            continue
        results.append({
            "key": detector["key"], "file": filename,
            "line": line_of(src, hits[0].start()), "occurrences": len(hits),
            "source_rules": detector["rules"], "severity": detector["severity"],
            "confidence": detector["confidence"], "note": detector["note"],
            "status": "candidate_not_verified"
        })
    for match in IMG_RE.finditer(src):
        if not ALT_RE.search(match.group()):
            results.append({"key": "MISSING_IMG_ALT", "file": filename,
                "line": line_of(src, match.start()), "occurrences": 1, "source_rules": ["NX-021", "SA-034"],
                "severity": "P1_CANDIDATE", "confidence": "medium",
                "note": "<img> sem alt; imagens decorativas devem possuir alt vazio, imagens informativas precisam descrição apropriada.",
                "status": "candidate_not_verified"})
    for match in EMPTY_CLICK_RE.finditer(src):
        results.append({"key": "EMPTY_ONCLICK", "file": filename,
                "line": line_of(src, match.start()), "occurrences": 1, "source_rules": ["NX-056"],
                "severity": "P0_CANDIDATE", "confidence": "high",
                "note": "Handler de clique vazio; verificar se é funcionalidade incompleta ou intenção de desabilitar.",
                "status": "candidate_not_verified"})
    return results


def audit(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    root = path if path.is_dir() else path.parent
    files = ([path] if path.is_file() else (p for p in path.rglob("*") if p.is_file()))
    findings = []
    checked = 0
    skipped_large = 0
    for candidate in files:
        if candidate.suffix.lower() not in SUFFIXES or any(part in SKIP for part in candidate.parts):
            continue
        if candidate.stat().st_size > 2_000_000:
            skipped_large += 1
            continue
        checked += 1
        content = candidate.read_text(encoding="utf-8", errors="replace")
        findings.extend(scan_text(content, str(candidate.relative_to(root))))
    findings.sort(key=lambda f: (f["file"], f["line"], f["key"]))
    for i, f in enumerate(findings, 1):
        f["id"] = f"STATIC-{i:04}"
    return {
        "scanner": "anti-ai-slop/static-prescreen-1.0", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "path": str(path.resolve()), "files_scanned": checked, "oversized_files_skipped": skipped_large,
        "candidate_count": len(findings),
        "warning": "Heuristics only. Not a quality score. No automated changes. Must review brand context and verify in browser.",
        "counts_by_key": dict(Counter(f["key"] for f in findings)), "findings": findings
    }


def to_markdown(result: dict) -> str:
    rows = ["# Pré-varredura estática Anti-AI-Slop", "",
        f"- Arquivos analisados: **{result['files_scanned']}**",
        f"- Suspeitas para revisão: **{result['candidate_count']}**",
        "- **Nenhuma ocorrência é defeito confirmado automaticamente.**", "",
        "| ID | Categoria | Regras | Arquivo:linha | Prioridade | Ocorrências |",
        "|---|---|---|---|---|---:|"]
    for f in result["findings"]:
        rows.append(f"| {f['id']} | {f['key']} | {', '.join(f['source_rules'])} | `{f['file']}:{f['line']}` | {f['severity']} | {f['occurrences']} |")
    rows.extend(["", "## Próximos passos", "", "Inspecionar manualmente as ocorrências, registrar brand rationale, corrigir apenas achados confirmados, executar build, testes e screenshots em browser real.", ""])
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", type=Path)
    ap.add_argument("--format", choices=["json", "md", "text"], default="text")
    ap.add_argument("--out", type=Path, help="Optional report path")
    args = ap.parse_args()
    try:
        result = audit(args.path)
    except (OSError, ValueError) as exc:
        ap.error(str(exc))
    data = json.dumps(result, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else to_markdown(result)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(data, encoding="utf-8")
    else:
        print(data)

if __name__ == "__main__":
    main()
