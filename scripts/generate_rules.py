#!/usr/bin/env python3
"""Regenerate a traceable rules index from the original catalog, using stdlib only."""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "references/catalogo-completo.md"
OUT = ROOT / "references/rules.json"
PFX = {"SA": "Sailop", "IM": "Impeccable", "UH": "Unslop UI (Herbert-Labs)",
       "UC": "Unslop UI (claudiusararu)", "NX": "Extensões pesquisadas"}
RULE_RE = re.compile(r"^#{3,4}\s+((?:SA|IM|UH|UC|NX)-\d{3})\s+[—–-]\s+(.+?)\s*$", re.M)


def parse_catalog(txt: str) -> dict:
    matches = list(RULE_RE.finditer(txt))
    rules = []
    for i, m in enumerate(matches):
        prefix = m.group(1).split("-")[0]
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(txt)
        # The body ends at a heading of equal or higher relevance to avoid consuming entire sections.
        tail = txt[start:end]
        stop = re.search(r"(?m)^#{2,3} (?!((?:SA|IM|UH|UC|NX)-\d{3})\s)[^\n]+$", tail)
        if stop:
            tail = tail[:stop.start()]
        fields = {}
        for key, aliases in {
            'signal': ["Sinal", "Evidência/detecção"],
            'fix': ["Correção sugerida", "Orientação"],
            'priority': ["Prioridade", "Prioridade contextual"],
            'class': ["Classe"],
            'method': ["Método"],
            'source_url': ["Fonte"],
        }.items():
            for label in aliases:
                pattern = r"(?m)^-\s+\*\*"+re.escape(label)+r"\*\*:\s*(.*)$"
                hit = re.search(pattern, tail)
                if hit:
                    fields[key] = hit.group(1).strip()
                    break
        # Extract category heading before this rule, and strip heading number.
        above = txt[:m.start()]
        subsections = re.findall(r"(?m)^###\s+(?!UH-\d{3}\b)([^\n]+)", above)
        category = subsections[-1] if subsections else "Catálogo"
        rules.append({
            "id": m.group(1), "name": m.group(2), "source": PFX[prefix],
            "category": category, "catalog_line": txt.count("\n", 0, m.start()) + 1,
            **fields,
        })
    palette_matches = {}
    for line in txt.splitlines():
        if re.match(r"^\|\s*P\d{2}\s*\|", line):
            parts = [part.strip() for part in line.split("|")[1:-1]]
            if len(parts) >= 4:
                pid = parts[0]
                colors = re.findall(r"#[0-9A-Fa-f]{6}\b", line)
                palette_matches[pid] = {"id": pid, "name": re.sub(r"[*`]", "", parts[1]),
                                        "colors": colors, "raw": line}
    return {
        "skill": "anti-ai-slop", "version": "1.0.0", "language": "pt-BR",
        "notice": "Rastreador de heurísticas, não prova de origem por IA nem proibição de cor/fonte/efeito.",
        "catalog_source": "references/catalogo-completo.md", "total_rules": len(rules),
        "counts": dict(sorted(Counter(rule['id'].split('-')[0] for rule in rules).items())),
        "total_palettes": len(palette_matches), "rules": rules,
        "palettes": [palette_matches[key] for key in sorted(palette_matches)]
    }


def main():
    data = parse_catalog(DOC.read_text(encoding="utf-8"))
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Rules: {data['total_rules']} / palettes: {data['total_palettes']} / {data['counts']}")

if __name__ == "__main__":
    main()
