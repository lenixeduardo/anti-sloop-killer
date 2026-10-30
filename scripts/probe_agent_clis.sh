#!/usr/bin/env bash
# Checks actual CLI executables and Anti-AI-Slop skill, not model authentication.
set -Eeuo pipefail
umask 077
LAB_ROOT="${AGENT_LAB_ROOT:-$(pwd)/.agent-cli-lab}"
LAB_ROOT="$(mkdir -p "$LAB_ROOT" && cd "$LAB_ROOT" && pwd -P)"
export HOME="$LAB_ROOT/home"
export PATH="$LAB_ROOT/npm-global/bin:$HOME/.local/bin:$HOME/.cursor/bin:$PATH"
export npm_config_cache="$LAB_ROOT/npm-cache"
mkdir -p "$LAB_ROOT/reports" "$LAB_ROOT/project"

# Single installed skill, shared by the three agent discovery locations.
if [[ -e scripts/install.py ]]; then
  python3 scripts/install.py --agent all --scope project --project "$LAB_ROOT/project" > "$LAB_ROOT/reports/skill-install.txt" 2>&1
else
  echo 'scripts/install.py não foi encontrado no checkout; execute a partir da raiz do repositório.' >&2
  exit 2
fi

export AGENT_LAB_ROOT="$LAB_ROOT"
python3 - <<'PY'
import hashlib, json, os, pathlib, shutil, subprocess, sys
root = pathlib.Path(os.environ['AGENT_LAB_ROOT'])
project = root / 'project'
results = {}
for agent, executable, folder in (
    ('codex', 'codex', '.agents'),
    ('claude', 'claude', '.claude'),
    ('cursor', 'agent', '.cursor'),
):
    exe = shutil.which(executable)
    if agent == 'cursor' and not exe:
        exe = shutil.which('cursor-agent')
    item = {'cli_executable': str(exe) if exe else None,
            'installed': bool(exe), 'version': None, 'version_exit_code': None,
            'skill_present': False, 'skill_sha256': None,
            'scanner_executed': False, 'scanner_candidates': None,
            'authentication_verified': False, 'real_model_executed': False,
            'outcome': 'not_installed'}
    skill = project / folder / 'skills' / 'anti-ai-slop' / 'SKILL.md'
    item['skill_present'] = skill.is_file()
    if skill.is_file():
        item['skill_sha256'] = hashlib.sha256(skill.read_bytes()).hexdigest()
    if exe:
        try:
            p = subprocess.run([exe, '--version'], capture_output=True, text=True, timeout=45,
                               env={**os.environ, 'HOME': str(root / 'home')})
            item['version_exit_code'] = p.returncode
            item['version'] = (p.stdout or p.stderr).strip().split('\n')[0][:240]
        except (OSError, subprocess.TimeoutExpired) as e:
            item['version'] = f'Erro: {type(e).__name__}'
    scanner = project / folder / 'skills' / 'anti-ai-slop' / 'scripts' / 'audit_slop.py'
    target = pathlib.Path('benchmarks/cases/portfolio-html/index.html')
    if scanner.is_file() and target.is_file():
        report_path = root / 'reports' / f'{agent}-scanner.json'
        p = subprocess.run([sys.executable, str(scanner), str(target), '--format', 'json', '--out', str(report_path)],
                           capture_output=True, text=True, timeout=60)
        if p.returncode == 0 and report_path.is_file():
            item['scanner_executed'] = True
            item['scanner_candidates'] = json.loads(report_path.read_text()).get('candidate_count')
    item['outcome'] = ('cli_verified_unauthenticated'
                       if item['installed'] and item['version_exit_code'] == 0
                           and item['skill_present'] and item['scanner_executed']
                       else 'incomplete')
    results[agent] = item
out = {'schema':'anti-ai-slop/cli-lab/v1', 'environment':'isolated_ephemeral',
       'note':'Executável/skill e scanner testados; sem autenticação, invocação de modelos ou validação de correções por agentes.',
       'agents':results}
(root/'reports'/'cli-versions.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
for agent, item in results.items():
    print(f"{agent}: {item['outcome']} | version={item['version']} | skill={item['skill_present']} | scanner={item['scanner_executed']}")
if not all(x['outcome']=='cli_verified_unauthenticated' for x in results.values()):
    sys.exit(1)
PY
