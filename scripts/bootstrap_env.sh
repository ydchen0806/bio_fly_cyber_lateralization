#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export http_proxy="${http_proxy:-http://192.168.32.28:18000}"
export https_proxy="${https_proxy:-http://192.168.32.28:18000}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-${ROOT_DIR}/.cache/matplotlib}"
mkdir -p "${MPLCONFIGDIR}"

python3.10 -m venv "${ROOT_DIR}/env"
source "${ROOT_DIR}/env/bin/activate"
python -m pip install --upgrade pip
pip install -e "${ROOT_DIR}[dev]"
python -m pytest --version >/dev/null

echo "Environment ready at ${ROOT_DIR}/env"
