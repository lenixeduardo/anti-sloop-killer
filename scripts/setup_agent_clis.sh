#!/usr/bin/env bash
# Installs OFFICIAL Codex, Claude Code and Cursor Agent CLIs in a disposable user HOME.
# Does not log in, request tokens, or claim agent tasks ran.
set -Eeuo pipefail
umask 077
LAB_ROOT="${AGENT_LAB_ROOT:-$(pwd)/.agent-cli-lab}"
LAB_ROOT="$(mkdir -p "$LAB_ROOT" && cd "$LAB_ROOT" && pwd -P)"
export HOME="$LAB_ROOT/home"
export npm_config_cache="$LAB_ROOT/npm-cache"
export PATH="$LAB_ROOT/npm-global/bin:$HOME/.local/bin:$HOME/.cursor/bin:$PATH"
mkdir -p "$HOME" "$LAB_ROOT/logs" "$LAB_ROOT/installers" "$LAB_ROOT/npm-global"

if ! command -v node >/dev/null || ! command -v npm >/dev/null || ! command -v curl >/dev/null; then
  echo "ERRO: node, npm e curl são obrigatórios" >&2
  exit 2
fi

install_codex() {
  npm install --global --prefix "$LAB_ROOT/npm-global" --no-audit --no-fund @openai/codex@latest
}
install_claude() {
  curl --fail --silent --show-error --location --retry 3 --connect-timeout 15 --max-time 180 \
    https://claude.ai/install.sh --output "$LAB_ROOT/installers/claude-install.sh"
  sha256sum "$LAB_ROOT/installers/claude-install.sh" > "$LAB_ROOT/installers/claude-install.sha256"
  bash "$LAB_ROOT/installers/claude-install.sh"
}
install_cursor() {
  curl --fail --silent --show-error --location --retry 3 --connect-timeout 15 --max-time 180 \
    https://cursor.com/install --output "$LAB_ROOT/installers/cursor-install.sh"
  sha256sum "$LAB_ROOT/installers/cursor-install.sh" > "$LAB_ROOT/installers/cursor-install.sha256"
  bash "$LAB_ROOT/installers/cursor-install.sh"
}

failed=0
for agent_name in codex claude cursor; do
  echo "[install] $agent_name: iniciando (sem autenticação)"
  if "install_$agent_name" > "$LAB_ROOT/logs/$agent_name-install.log" 2>&1; then
    echo "[install] $agent_name: instalador concluído"
  else
    code=$?
    echo "[install] $agent_name: FALHA (código $code; veja logs)" >&2
    tail -n 8 "$LAB_ROOT/logs/$agent_name-install.log" >&2 || true
    failed=$((failed+1))
  fi
done

# Always leave a reproducible record, including failures.
printf 'lab_root=%s\nnode=%s\n' "$LAB_ROOT" "$(node --version)" > "$LAB_ROOT/setup-info.txt"
if ((failed)); then
  echo "[install] $failed instalador(es) falharam" >&2
  exit 1
fi
