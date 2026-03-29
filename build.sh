#!/bin/bash
set -e

echo "=== LeCroy Options Recovery - Linux Build ==="
echo

echo "[1/2] Installing dependencies..."
pip3 install pycryptodome pyinstaller

echo
echo "[2/2] Building executables..."

pyinstaller --onefile --clean --name gen      gen.py
pyinstaller --onefile --clean --name list     list.py
pyinstaller --onefile --clean --name validate validate.py

echo
echo "=== Build complete ==="
echo "Executables are in: dist/"
echo "  dist/gen"
echo "  dist/list"
echo "  dist/validate"
