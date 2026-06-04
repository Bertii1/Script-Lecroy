# Technology Stack

**Analysis Date:** 2026-06-04

## Languages

**Primary:**
- Python 3.12.3 — all application code (GUI, CLI, core library)

**Secondary:**
- None

## Runtime

**Environment:**
- CPython 3.12.3
- Virtualenv present at project root (`pyvenv.cfg`, base interpreter `/usr/bin/python3.12`)

**Package Manager:**
- pip (via `bin/pip3.12` inside the project venv)
- Lockfile: not present (only `requirements.txt` with a loose version pin)

## Frameworks

**GUI:**
- `tkinter` (stdlib) + `ttk` — desktop GUI (`gui.py`)
  - Notebook, Treeview, PanedWindow, filedialog, messagebox widgets
  - No external GUI framework; entirely stdlib

**Cryptography:**
- `pycryptodome` 3.23.0 (pinned `>=3.0` in `requirements.txt`)
  - `Crypto.Cipher.Blowfish` ECB mode — `lec/crypto.py`

**Build / Packaging:**
- `PyInstaller` 6.20.0 — produces a single-file native executable
  - Build script: `build_exe.py`
  - Spec file: `LeCroy-KeyGen.spec`
  - Output: `LeCroy-KeyGen` binary (14 MB, already built, committed to repo root)
  - Flags: `--onefile --windowed`, UPX compression enabled

## Key Dependencies

**Critical:**
- `pycryptodome >=3.0` — Blowfish cipher is the only external runtime dependency;
  without it the application cannot encode or decode any key

**Stdlib modules used across source files:**
- `struct` — binary packing/unpacking (`lec/crypto.py`, `lec/key.py`, `lec/db.py`)
- `binascii` — hex encoding (`lec/key.py`)
- `tkinter`, `tkinter.ttk`, `tkinter.filedialog`, `tkinter.messagebox` — GUI (`gui.py`)
- `json` — reading `default_opts.json` and writing `opzioni.json` (`cli/gen_all.py`, `cli/list.py`, `gui.py`)
- `io.BytesIO`, `io.StringIO` — in-memory binary/text buffers
- `os`, `sys`, `subprocess` — path resolution, process spawning

**Dev / Build only:**
- `pyinstaller 6.20.0` — not imported at runtime; only used by `build_exe.py`

## Configuration

**Environment:**
- No environment variables required; no `.env` files present
- Runtime configuration loaded from `default_opts.json` (committed JSON file)
- Optional: user-supplied `options.cfg` (proprietary binary format from LeCroy scopes)

**Build:**
- `LeCroy-KeyGen.spec` — PyInstaller spec (auto-generated, references absolute dev path)
- `build_exe.py` — wrapper that invokes `pyinstaller --onefile --windowed`

## Platform Requirements

**Development:**
- Python 3.12+ (tested on Linux with CPython 3.12.3)
- `pip install pycryptodome` (only external dependency)
- `pip install pyinstaller` (build only)

**Production / Distribution:**
- Single native executable `LeCroy-KeyGen` (Linux ELF or Windows PE depending on build host)
- No Python installation required on target machine (PyInstaller bundles the runtime)
- GUI requires a display server (X11/Wayland on Linux, native on Windows/macOS)

---

*Stack analysis: 2026-06-04*
