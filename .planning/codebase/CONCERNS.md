# Codebase Concerns

**Analysis Date:** 2026-06-04

---

## Security Concerns

### Hardcoded Blowfish Key (Critical)

- **Issue:** The Blowfish symmetric key used to encrypt/decrypt both license keys and the `options.cfg` database is hardcoded in source as `key_ct` with a trivial single-byte XOR obfuscation (`^ 116`). Anyone who reads `lec/crypto.py` can reconstruct the raw 16-byte key in seconds.
- **Files:** `lec/crypto.py` lines 5–7
- **Impact:** The entire key-generation algorithm is fully reversible by any third party who inspects the source repository. The XOR transform provides no real protection — it is not a secret and adds zero cryptographic strength. For an internal HCS tool the risk is information disclosure if the repo is ever made public or shared.
- **Current mitigation:** None. The "educational use only" comment is a disclaimer, not a technical control.
- **Recommendation:** If future use requires stronger confidentiality, the key should be loaded from a runtime secret (environment variable, OS keychain, or a configuration file excluded from version control) rather than embedded in source. For the current internal-only use case, at minimum add `lec/crypto.py` to `.gitignore` and keep the repo private.

### Singleton Cipher Instance at Module Load

- **Issue:** `lec/crypto.py` creates a single `Blowfish.new(key, Blowfish.MODE_ECB)` object at import time (line 9). Blowfish ECB mode is stateless so this is not a correctness bug today, but it means all calls share one cipher object. If the library ever introduces per-call state, or if multi-threading is added to the GUI, this becomes a race condition.
- **Files:** `lec/crypto.py` line 9
- **Impact:** Low currently; medium if the codebase evolves.
- **Recommendation:** Instantiate the cipher inside `encrypt()` and `decrypt()` rather than at module level.

### ECB Mode Usage

- **Issue:** Blowfish ECB mode is used for both database decryption (`lec/db.py`) and key generation (`lec/key.py`). ECB mode is deterministic — identical 8-byte plaintext blocks always produce identical ciphertext blocks — which is why the LeCroy key format works (same ScopeID + same options = same key). This is an inherent property of the protocol being reversed, not a bug introduced here, but it should be documented clearly.
- **Files:** `lec/crypto.py` line 9; `lec/key.py` line 28
- **Impact:** By design; no change needed unless the protocol is extended.

### Generated Keys Committed to Git

- **Issue:** `codici` (a plain-text file containing actual generated license keys for a specific scope) is committed and tracked by git. `opzioni.txt` (a listing of all option codes) is also committed. Although both appear in `.gitignore` as of the current working-tree diff, they are already in the git history and tracked in HEAD.
- **Files:** `codici` (tracked, git-tracked), `opzioni.txt` (tracked)
- **Impact:** Any clone of the repository receives a set of real, working license keys tied to a specific instrument.
- **Recommendation:** Remove both files from git tracking (`git rm --cached codici opzioni.txt`), ensure `.gitignore` is committed, and purge from history if the repo will be shared.

---

## Technical Debt

### `DEFAULT_OPTS` Variable Is Defined But Never Used

- **Issue:** `gui.py` line 67 creates `DEFAULT_OPTS = StringIO(OPTS_STR)` — a `StringIO` wrapping the hardcoded option list. This object is never referenced anywhere in the file. The GUI instead reads from `default_opts.json` on disk via `DEFAULT_OPTS_PATH`. The `StringIO` was presumably intended to serve as an in-memory fallback when the JSON file is absent, but that code path was never wired up.
- **Files:** `gui.py` lines 8–48 (OPTS_STR definition), line 67 (unused DEFAULT_OPTS)
- **Impact:** Silent breakage — when `default_opts.json` is missing (e.g. in a PyInstaller bundle, see below), the GUI shows an error instead of falling back to the embedded data.
- **Fix approach:** Replace the `_load_default_options` method's file-read logic with a primary path that parses `OPTS_STR` directly (the data is already in memory), and use the JSON file as an optional override.

### `options_count` Is Always Zero in the Radio Button Label

- **Issue:** `gui.py` line 89 initialises `self.options_count = 0`. Line 158 embeds it in the "Predefinite (0 opzioni)" radio button label text at construction time. The count is never updated after options load, so the label permanently reads "0 opzioni" regardless of how many options are loaded.
- **Files:** `gui.py` lines 89, 158
- **Fix approach:** Update the radio button label text after `_populate_opts_tree` completes, or derive the count dynamically from `len(self.options_data)`.

### `fromfile()` Silently Swallows All `LicError` Exceptions

- **Issue:** `lec/db.py` lines 297–301: `fromfile()` catches any `LicError` from the v1 parser and silently retries with the v2 parser. If the file is genuinely corrupt (not just a v2 file), the v2 parse will also fail, but with a less informative error context because the original v1 exception is discarded.
- **Files:** `lec/db.py` lines 297–301
- **Fix approach:** Log or chain the original exception (`raise v2_error from v1_error` in Python 3) so callers can diagnose dual-parse failures.

### `cli/gen_all.py` Calls `python` Instead of `sys.executable`

- **Issue:** `cli/gen_all.py` line 21 hardcodes `'python'` as the subprocess command. On systems where `python` resolves to Python 2 (or is absent entirely), this will fail silently or produce incorrect results. The rest of the toolchain uses Python 3.
- **Files:** `cli/gen_all.py` line 21
- **Fix approach:** Replace `'python'` with `sys.executable` (already imported at the module level) to guarantee the same interpreter is used.

### `cli/gen_all.py` Uses Subprocess to Call `cli/gen.py`

- **Issue:** `gen_all.py` spawns a new Python process for every option to generate its key (up to 39 subprocess calls for the default option set). `lec.key.encode()` is a pure Python function — there is no reason to invoke it via subprocess.
- **Files:** `cli/gen_all.py` lines 1–25
- **Fix approach:** Import `lec.key` directly and call `lec.key.encode()` in-process, eliminating all subprocesses.

### Inconsistent `sys.path` Manipulation

- **Issue:** Every CLI script manually inserts the project root into `sys.path` at lines 2–3 (`cli/gen.py`, `cli/list.py`, `cli/validate.py`). `gui.py` does the same at line 60. This is a workaround for the absence of a proper `setup.py` / `pyproject.toml` / installed package.
- **Files:** `cli/gen.py:3`, `cli/list.py:3`, `cli/validate.py:3`, `gui.py:60`
- **Impact:** Scripts must be invoked from specific directories; importing from tests or other contexts requires the same hack.
- **Fix approach:** Add a minimal `pyproject.toml` with `[tool.setuptools]` and install the `lec` package in editable mode (`pip install -e .`).

### `cli/` Is Not a Python Package

- **Issue:** The `cli/` directory has no `__init__.py`. The scripts in it import via `sys.path` hacks rather than relative or absolute package imports.
- **Files:** `cli/` directory
- **Fix approach:** Either add `__init__.py` and entry-point wrappers, or restructure as console scripts in `pyproject.toml`.

### `lec/__init__.py` Is Empty

- **Issue:** `lec/__init__.py` is a zero-byte file. The `lec` package exposes nothing from its `__init__`. Callers must import submodules directly (`from lec import key`, `from lec import db`), which is fine, but it means there is no public API surface defined.
- **Files:** `lec/__init__.py`
- **Impact:** Minor; can cause confusion about what the package exports.

---

## Build and Packaging Issues

### `default_opts.json` Is Not Bundled by the PyInstaller Build

- **Issue:** `build_exe.py` line 27 adds `--add-data lec:lec` to bundle the `lec/` package, but does not add `default_opts.json`. When the compiled `LeCroy-KeyGen` binary is run, `DEFAULT_OPTS_PATH` points to a path relative to `sys._MEIPASS` (the temp extraction dir), but `default_opts.json` is never placed there.
- **Files:** `build_exe.py` line 27; `gui.py` lines 65, 403
- **Impact:** The built executable always shows "File default_opts.json non trovato accanto a gui.py" on launch and starts with an empty option list.
- **Fix approach:** Either (a) add `--add-data default_opts.json:.` to `build_exe.py`, and update `_load_default_options` to use `sys._MEIPASS` when frozen; or (b) eliminate the JSON file dependency entirely by using the already-embedded `OPTS_STR` constant (see the dead-code concern above).

### `LeCroy-KeyGen.spec` Contains an Absolute Developer Path

- **Issue:** `LeCroy-KeyGen.spec` line 5 hardcodes `/home/filippo/Progetti/HCS/Script-Lecroy/gui.py`. This spec file cannot be used on any machine other than the original developer's.
- **Files:** `LeCroy-KeyGen.spec` line 5
- **Impact:** Any team member or CI system running `pyinstaller LeCroy-KeyGen.spec` will fail immediately.
- **Fix approach:** Replace the absolute path with a relative path or use `os.path.join(SPECPATH, 'gui.py')` (SPECPATH is a PyInstaller built-in variable).

### `.pyc` Bytecode Files Are Committed to Git

- **Issue:** Three compiled bytecode files are tracked in git: `lec/__pycache__/__init__.cpython-313.pyc`, `lec/__pycache__/crypto.cpython-313.pyc`, `lec/__pycache__/key.cpython-313.pyc`. The `.gitignore` has `__pycache__/` listed but these files were committed before that rule was added.
- **Files:** `lec/__pycache__/` (all `.pyc` files)
- **Impact:** Bytecode files are Python-version-specific (tagged `cpython-313`), will not work on Python 3.12 used by the venv, and bloat the repository history unnecessarily.
- **Fix approach:** `git rm -r --cached lec/__pycache__/` and commit.

### Venv Artifacts Are Untracked but Not Ignored

- **Issue:** `pyvenv.cfg`, `lib64/`, and the compiled `LeCroy-KeyGen` binary are untracked (`??` in git status) and not yet covered by `.gitignore` (the current working-tree `.gitignore` adds `bin/`, `lib/`, `lib64/`, `include/` but those changes are not yet committed). Until that commit lands, a fresh `git clone` followed by a `git status` will show these as untracked noise.
- **Files:** `.gitignore` (uncommitted changes), `pyvenv.cfg`, `lib64/`
- **Fix approach:** Commit the current `.gitignore` changes immediately.

---

## Maintainability Issues

### No Tests Exist

- **Issue:** There are zero test files in the repository. No unit tests for `lec/key.py` (encode/decode round-trip), `lec/crypto.py` (encrypt/decrypt inverse), or `lec/db.py` (DB parsing). No integration tests for CLI scripts.
- **Files:** entire repository
- **Impact:** Any future change to the crypto or key encoding logic has no safety net. A subtle regression (e.g. byte-order bug in `encode()`/`decode()`) would not be caught until a key fails on a real instrument.
- **Fix approach:** Add `pytest` to `requirements.txt` and create `tests/test_key.py` with round-trip tests (encode then decode should return original inputs) and known-good vectors.

### Unknown Fields in `LicDB` Are Named `u0`, `u1`, `u2`, etc.

- **Issue:** Throughout `lec/db.py`, fields whose meaning is unknown during reverse engineering are named `u0`, `u1`, `u2`, `u3`, `s1`, `s2` and entire record classes are named `LicA`, `LicB`, `LicC`. The groups in `LicDB.__init__` are annotated with `# ???`.
- **Files:** `lec/db.py` lines 189–228, 257–268
- **Impact:** Maintainers cannot tell what these fields represent. If a future firmware version changes the binary layout, there is no semantic anchor for updating the parser.
- **Fix approach:** Document findings from the EEVblog / LeCroy Owners' Group in comments at each field, even if uncertain. Rename from `u0` to names like `unknown_serial` or `padding_field`.

### Dual Class Hierarchy for v1/v2 DB (LicDB vs LicDBv2)

- **Issue:** `lec/db.py` defines `LicDB` (lines 247–269) and `LicDBv2` (lines 272–293) as near-identical classes. The only difference is `LicComponent` vs `LicComponentV2` (the v2 component adds a `guid` field). All other groups are parsed identically.
- **Files:** `lec/db.py` lines 247–293
- **Impact:** Any future change to group loading logic must be made in both classes.
- **Fix approach:** Merge into a single `LicDB` class that accepts a `component_cls` parameter, or have `LicDBv2` inherit from `LicDB` and override only the component loader.

### `cli/list.py` Has a Side Effect: Always Writes `opzioni.json`

- **Issue:** `cli/list.py` lines 20–21 unconditionally write an `opzioni.json` file in the current working directory whenever the script is invoked. This side effect is not documented in the script's help text or README.
- **Files:** `cli/list.py` lines 20–21
- **Fix approach:** Make JSON export optional via a `--json` flag, or at minimum print a notice that the file was written.

### README Documents Old File Paths

- **Issue:** `README.md` references `gen.py`, `list.py`, and `validate.py` at the project root. After the refactor, these scripts live under `cli/`. The README directory tree is also wrong (still shows the old layout without `cli/`, `gui.py`, `build_exe.py`, `default_opts.json`).
- **Files:** `README.md` lines 18–29, 36–70
- **Impact:** New users following the README will get `FileNotFoundError` immediately.
- **Fix approach:** Update README paths to `cli/gen.py`, `cli/list.py`, `cli/validate.py` and add the GUI to the quickstart section.

---

## Portability Concerns

### `build_exe.py` Uses `os.pathsep` Correctly but the Spec Does Not

- **Issue:** `build_exe.py` line 27 correctly uses `os.pathsep` for the `--add-data` separator (`:` on Linux/macOS, `;` on Windows). However, `LeCroy-KeyGen.spec` uses `('lec', 'lec')` tuple syntax which is portable. No portability issue here, but the two build methods are not in sync.
- **Files:** `build_exe.py` line 27; `LeCroy-KeyGen.spec` line 8
- **Impact:** Minor inconsistency; both should produce the same binary.

### GUI Is tkinter-Based: Works on Linux/macOS/Windows

- No portability concern; tkinter ships with CPython on all platforms.

### `cli/gen_all.py` Writes Output to a File Named `codici` (No Extension)

- **Issue:** `cli/gen_all.py` line 16 opens `_OUT = os.path.join(_ROOT, 'codici')` for writing. On Windows, creating a file without an extension in `Program Files` or the project root is unusual and may confuse users expecting `codici.txt`.
- **Files:** `cli/gen_all.py` line 9
- **Fix approach:** Use `codici.txt` as the output filename.

---

## Performance Concerns

### No Performance Concerns at Current Scale

The tool processes at most ~39 options per invocation. Blowfish ECB on 8-byte blocks is fast. The O(n) linear scan in `_toggle_item` (gui.py line 492) iterating over `options_data` for each click is at most ~39 iterations — not a concern. Performance is not a meaningful risk for this codebase at its current scope.

---

## Dependencies at Risk

### `pycryptodome>=3.0` Is Underspecified

- **Risk:** `requirements.txt` specifies only a minimum version (`>=3.0`). pycryptodome is actively maintained (current version 3.23.0 in the project venv) and has had no breaking changes to the `Blowfish` API, but an upper bound would make builds reproducible.
- **Files:** `requirements.txt` line 1
- **Impact:** Low; the API surface used (`Blowfish.new`, `.encrypt`, `.decrypt`) is stable.
- **Recommendation:** Pin to `pycryptodome>=3.10,<4` and add a `requirements-dev.txt` with `pyinstaller` and `pytest`.

### No `pyproject.toml` or `setup.py`

- **Risk:** There is no packaging metadata. The project cannot be installed as a Python package, which forces the `sys.path` hacks described above.
- **Files:** project root
- **Fix approach:** Add a minimal `pyproject.toml` with `[project]` and `[tool.setuptools.packages.find]` sections.

---

## Missing Critical Features

### No Input Sanitisation on ScopeID in CLI Scripts

- **Issue:** `cli/gen.py` line 10 calls `int(argv[1], 16)` without any length or format check. Passing a value larger than 24 bits (e.g. the full `2F0DAB-DE`) silently overflows the 3-byte iid field in `key.py`, producing a wrong key. The GUI validates length (exactly 6 hex chars), but the CLI has no guard.
- **Files:** `cli/gen.py` line 10; `cli/validate.py` line 12
- **Fix approach:** Add a check: `if not (1 <= int(argv[1], 16) <= 0xFFFFFF): exit("ScopeID must be a 3-byte hex value (max FFFFFF")`.

### No Logging or Audit Trail

- **Issue:** The tool generates license keys with no record of who generated what for which scope. For an internal enterprise tool, an audit log (scope ID + options + timestamp + operator) would be valuable for tracking issued licenses.
- **Files:** `gui.py`, `cli/gen_all.py`
- **Impact:** No ability to reconstruct what licenses were issued without keeping the exported `codici` file manually.

---

*Concerns audit: 2026-06-04*
