#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$DIR/install.py" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "$DIR/install.py" "$@"
else
  echo 'Python 3 e necessario para instalar esta skill.' >&2
  exit 127
fi
