#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python_command="${PYTHON_COMMAND:-python3}"
command -v "$python_command" >/dev/null 2>&1 || python_command=python
exec "$python_command" "$script_dir/validate_long_readiness.py" "$@"
