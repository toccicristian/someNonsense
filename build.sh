#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install PyInstaller

rm -rf build
rm -f bin/someNonesense

python -m PyInstaller \
  --clean \
  --onefile \
  --name someNonesense \
  --distpath bin \
  --workpath build \
  src/someNonesense.py

deactivate

echo "Ejecutable creado en: bin/someNonesense"
