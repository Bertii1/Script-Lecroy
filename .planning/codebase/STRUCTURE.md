# Codebase Structure

**Analysis Date:** 2026-06-04

## Directory Layout

```
Script-Lecroy/               # Project root (also a Python venv)
├── gui.py                   # GUI entry point (tkinter app, ~682 lines)
├── build_exe.py             # PyInstaller build script (~40 lines)
├── default_opts.json        # Built-in option definitions (39 entries)
├── opzioni.txt              # Tab-separated option list (reference / generated)
├── requirements.txt         # Runtime dependency: pycryptodome
├── pyvenv.cfg               # Python 3.12 venv config
│
├── lec/                     # Core library package
│   ├── __init__.py          # Empty package marker
│   ├── crypto.py            # Blowfish crypto primitives (~24 lines)
│   ├── key.py               # License key encode/decode (~30 lines)
│   └── db.py                # Binary options.cfg parser (~316 lines)
│
├── cli/                     # Command-line scripts (no __init__.py, not a package)
│   ├── gen.py               # Single key generator (~11 lines)
│   ├── gen_all.py           # Batch key generator (~25 lines)
│   ├── list.py              # Options.cfg lister/exporter (~23 lines)
│   └── validate.py          # Key decoder/validator (~26 lines)
│
├── dist/                    # PyInstaller output (not committed)
│   └── LeCroy-KeyGen        # Compiled standalone binary
│
├── build/                   # PyInstaller build artifacts (not committed)
│   └── LeCroy-KeyGen/
│
├── bin/                     # Venv executables (not project code)
├── lib/                     # Venv site-packages (not project code)
├── include/                 # Venv headers (not project code)
└── lib64 -> lib             # Venv symlink
```

---

## Directory Purposes

**`lec/` — Core library:**
- Purpose: The only importable Python package. Contains all cryptographic and parsing logic.
- Contains: Three modules — `crypto.py`, `key.py`, `db.py`.
- Key files: `lec/key.py` (public API for encoding/decoding keys), `lec/crypto.py` (Blowfish primitives), `lec/db.py` (binary database reader).

**`cli/` — CLI scripts:**
- Purpose: Standalone Python scripts for command-line use. Not a package (no `__init__.py`). Each script adds the project root to `sys.path` before importing `lec`.
- Contains: Four independent scripts, each covering one operation.
- Key files: `cli/gen.py` (single key), `cli/validate.py` (decode + optional option lookup).

**`dist/` — Build output:**
- Purpose: Contains the compiled `LeCroy-KeyGen` executable produced by `build_exe.py`.
- Generated: Yes
- Committed: No

**`build/` — PyInstaller work directory:**
- Purpose: Intermediate build artifacts (`.toc`, `.pkg`, `.pyz` files).
- Generated: Yes
- Committed: No (present in repo due to missing `.gitignore` entry)

---

## Key File Locations

**Entry Points:**
- `gui.py`: Interactive desktop application (`main()` at line 675)
- `cli/gen.py`: CLI single-key generator (run directly, `argv`-based)
- `cli/gen_all.py`: CLI batch generator (prompts for ScopeID, writes to `codici` file)
- `cli/list.py`: CLI options.cfg dump tool
- `cli/validate.py`: CLI key decoder

**Configuration / Data:**
- `default_opts.json`: Static list of 39 known LeCroy license options (code, key name, description). Used by GUI (default mode) and `cli/gen_all.py`.
- `opzioni.txt`: Tab-separated equivalent of `default_opts.json`; appears to be a generated reference file.
- `requirements.txt`: Declares `pycryptodome>=3.0`; PyInstaller is listed as a comment.
- `pyvenv.cfg`: Marks the root as a Python 3.12 venv.

**Core Logic:**
- `lec/crypto.py`: Blowfish cipher setup and `encrypt`/`decrypt` functions.
- `lec/key.py`: `encode(iid, flags, mask)` and `decode(ok)` — the primary public API.
- `lec/db.py`: `fromfile(fname)` and all record classes for parsing `options.cfg`.

**Build:**
- `build_exe.py`: Invokes PyInstaller with `--onefile --windowed`, bundles `lec/` as data.

---

## Module Dependency Graph

```
gui.py
  ├── lec/key.py       (encode, decode)
  ├── lec/db.py        (fromfile)
  └── default_opts.json

cli/gen.py
  └── lec/key.py       (encode)

cli/gen_all.py
  ├── cli/gen.py       (via subprocess)
  └── default_opts.json

cli/list.py
  └── lec/db.py        (fromfile)

cli/validate.py
  ├── lec/key.py       (decode)
  └── lec/db.py        (fromfile, optional)

lec/key.py
  └── lec/crypto.py    (encrypt, decrypt)

lec/db.py
  └── lec/crypto.py    (decrypt)

lec/crypto.py
  └── pycryptodome     (Crypto.Cipher.Blowfish)
```

---

## Key Classes and Functions Per Module

**`lec/crypto.py` (24 lines):**
| Symbol | Type | Description |
|---|---|---|
| `key_ct` | `bytes` | Obfuscated Blowfish key (XOR + reversed at import) |
| `key` | `bytes` | Decoded Blowfish key |
| `cipher` | `Blowfish` | Module-level ECB cipher singleton |
| `revd(blk)` | function | Reverses byte order of two 32-bit dwords |
| `encrypt(blk)` | function | Blowfish-ECB encrypt with byte-reversal pre/post |
| `decrypt(blk)` | function | Blowfish-ECB decrypt with byte-reversal pre/post |

**`lec/key.py` (30 lines):**
| Symbol | Type | Description |
|---|---|---|
| `encode(iid, flags, mask)` | function | Pack params → encrypt → hex string (`XXXX-XXXX-XXXX-XXXX`) |
| `decode(ok)` | function | Hex string → decrypt → `(iid, flags, mask)` tuple |

**`lec/db.py` (316 lines):**
| Symbol | Type | Description |
|---|---|---|
| `LicError` | exception | Signals malformed binary data |
| `LicReader` | class | Decrypts and streams typed records from `options.cfg` |
| `LicCategory` | class | A license category record |
| `LicComponent` | class | A licensable component (original format) |
| `LicComponentV2` | class | Extended component with extra `guid` field |
| `LicProcToCat` | class | Process-to-category mapping record |
| `LicOption` | class | Core: one licensable option (`page`, `bit`, `name`, `description`) |
| `LicEnabCompWithOpt` | class | Component-option association record |
| `LicA`, `LicB`, `LicC`, `LicFlag` | classes | Partially understood record types |
| `LicDB` | class | Full parsed database (original format) |
| `LicDBv2` | class | Full parsed database (v2 format, `LicComponentV2`) |
| `LoadGroup(reader, cls)` | function | Parse N records of a given class into an `{idx: obj}` dict |
| `fromfile(fname)` | function | Public entry: auto-detects format, returns `LicDB` or `LicDBv2` |
| `DecryptFile(hfi, hfo)` | function | Block-decrypts a full file from one BytesIO to another |

**`gui.py` (682 lines):**
| Symbol | Type | Description |
|---|---|---|
| `LeCroyGUI` | class | Entire GUI application, tkinter-based |
| `LeCroyGUI._load_default_options()` | method | Parse `default_opts.json` into `options_data` list |
| `LeCroyGUI._load_options(path)` | method | Load and parse binary `options.cfg` via `lec.db.fromfile` |
| `LeCroyGUI._do_generate(iid, opts)` | method | Call `lec_key.encode()` for each option and populate results table |
| `LeCroyGUI._validate_key()` | method | Call `lec_key.decode()` and display decoded fields |
| `main()` | function | `tk.Tk()` setup and `LeCroyGUI` instantiation |
| `OPTS_STR` | constant | Inline JSON fallback option list (mirrors `default_opts.json`) |

**`cli/gen.py` (11 lines):** Reads 3 argv args, calls `lec.key.encode()`, prints result.

**`cli/gen_all.py` (25 lines):** Reads `default_opts.json`, invokes `cli/gen.py` via `subprocess` for each entry, writes to `codici` file.

**`cli/list.py` (23 lines):** Calls `lec.db.fromfile()`, prints all options, writes `opzioni.json`.

**`cli/validate.py` (26 lines):** Calls `lec.key.decode()`, optionally resolves option names via `lec.db.fromfile()`.

---

## Naming Conventions

**Files:**
- `lec/` module files: lowercase `snake_case.py`
- CLI scripts: lowercase `snake_case.py`
- Data files: `snake_case.json` / `.txt`

**Classes:**
- `Lic*` prefix for all record types in `lec/db.py` (`LicOption`, `LicDB`, etc.)
- `LeCroyGUI` for the GUI class (CamelCase)

**Functions:**
- Public: `snake_case` (e.g., `fromfile`, `encode`, `decode`)
- Private GUI methods: `_snake_case` prefix (e.g., `_do_generate`, `_load_options`)
- Binary helpers: short abbreviated names (`revd`, `fsize`)

**Variables:**
- GUI tkinter vars: `snake_case_var` suffix (e.g., `scope_var`, `cfg_path_var`)
- Constants: `UPPER_CASE` (e.g., `ROW_ODD`, `ACCENT`, `OPTS_STR`)

---

## File Sizes and Complexity

| File | Lines | Complexity |
|---|---|---|
| `gui.py` | 682 | High — single class, 30+ methods, full tkinter UI |
| `lec/db.py` | 316 | Medium — many small record classes, streaming parser |
| `build_exe.py` | 40 | Low — single subprocess call |
| `cli/gen_all.py` | 25 | Low — sequential script |
| `cli/validate.py` | 26 | Low — argument parsing + two lib calls |
| `cli/list.py` | 23 | Low — argument parsing + lib call |
| `cli/gen.py` | 11 | Trivial — single function call |
| `lec/key.py` | 30 | Low — two pure functions |
| `lec/crypto.py` | 24 | Low — module-level init + two wrapper functions |

---

## Where to Add New Code

**New license feature or option:**
- Data: add entry to `default_opts.json` (format: `{"code": "XX-YYYYYYYY", "key": "NAME", "description": "..."}`)
- No code changes required if the option fits the existing flags/mask scheme.

**New key format or crypto variant:**
- Implementation: `lec/crypto.py` (new cipher) and `lec/key.py` (new pack/unpack logic)
- Tests: add alongside in `lec/` or a new `tests/` directory.

**New CLI operation:**
- Implementation: `cli/<operation>.py` following the pattern of existing scripts (add root to `sys.path`, import from `lec/`)

**New GUI tab or feature:**
- Implementation: `gui.py` — add `_build_<name>_tab()` method and wire it in `_build_ui()`.
- If the tab grows large (>150 lines), consider extracting to a separate module imported by `gui.py`.

**Shared utilities:**
- Location: `lec/` — add a new module (e.g., `lec/utils.py`) if the helper is used by more than one existing module.

---

*Structure analysis: 2026-06-04*
