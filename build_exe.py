#!/usr/bin/env python3
"""
Build script — genera l'eseguibile standalone con PyInstaller.

Uso:
    python build_exe.py

Output:
    dist/LeCroy-KeyGen.exe  (Windows)
    dist/LeCroy-KeyGen      (Linux / macOS)

Requisiti:
    pip install pyinstaller
"""

import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",                       # niente console su Windows
    "--name", "LeCroy-KeyGen",
    "--add-data", f"lec{os.pathsep}lec",  # includi il package lec
    os.path.join(HERE, "gui.py"),
]

print("Avvio build…")
print(" ".join(cmd))
result = subprocess.run(cmd)

if result.returncode == 0:
    print("\nBuild completato!")
    print(f"Eseguibile in: {os.path.join(HERE, 'dist', 'LeCroy-KeyGen')}")
else:
    print("\nBuild fallito. Controlla l'output sopra.")
    sys.exit(1)
