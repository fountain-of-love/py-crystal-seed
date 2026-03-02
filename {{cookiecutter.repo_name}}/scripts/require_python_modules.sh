#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: require_python_modules.sh <python> <module> [<module> ...]" >&2
  exit 2
fi

PY="$1"
shift

missing=()
for module in "$@"; do
  if ! "$PY" -c "import ${module}" >/dev/null 2>&1; then
    missing+=("$module")
  fi
done

if [ "${#missing[@]}" -eq 0 ]; then
  exit 0
fi

echo "Missing Python modules for $PY:"
for module in "${missing[@]}"; do
  echo "  - $module"
done
echo "Run ./scripts/bootstrap.sh and install dev dependencies before retrying."
exit 1
