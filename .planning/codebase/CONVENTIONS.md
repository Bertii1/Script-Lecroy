# Coding Conventions

**Analysis Date:** 2026-06-04

## Naming Patterns

**Files:**
- Module files use lowercase snake_case: `crypto.py`, `key.py`, `db.py`
- CLI scripts use lowercase snake_case: `gen.py`, `gen_all.py`, `list.py`, `validate.py`
- The GUI entry point uses a flat name: `gui.py`
- Build tooling uses snake_case: `build_exe.py`

**Functions (module-level):**
- Pure utility functions use lowercase snake_case: `fsize()`, `revd()`, `decode()`, `encode()`
- Functions that operate on file handles use PascalCase (inconsistent): `DecryptFile()`, `LoadGroup()`, `PrintGroup()`
- `fromfile()` uses lowercase with no separator — an outlier

**Classes:**
- All class names use PascalCase: `LicReader`, `LicDB`, `LicDBv2`, `LicCategory`, `LicComponent`, `LicComponentV2`, `LicOption`, `LicError`, `LeCroyGUI`
- Domain classes carry a `Lic` prefix by convention: `LicDB`, `LicCategory`, `LicOption`, etc.
- Versioned variants append a version suffix: `LicComponent` vs `LicComponentV2`, `LicDB` vs `LicDBv2`

**Methods (inside `LeCroyGUI`):**
- Private/internal methods are prefixed with a single underscore: `_setup_style()`, `_build_ui()`, `_gen_selected()`, `_status()`
- Public entry point has no underscore: `main()`

**Variables and attributes:**
- Instance attributes use lowercase snake_case: `self.options_data`, `self._status_var`, `self.scope_var`
- Module-level constants use UPPER_SNAKE_CASE: `ROW_ODD`, `ROW_EVEN`, `ACCENT`, `MONO_FONT`, `CHECK_ON`, `CHECK_OFF`
- Path constants use UPPER_SNAKE_CASE with a leading `_` when module-private: `_HERE`, `_ROOT`, `_GEN_PY`, `_OPTS`, `_OUT`
- Unknown/undocumented fields fall back to terse names: `u0`, `u1`, `u2`, `s1`, `s2`

**Type annotations:**
- Used selectively in `gui.py` for method return types and parameter types: `def _get_scope_iid(self) -> int | None`, `def _load_options(self, path: str)`, `self.val_info: dict[str, tk.StringVar]`, `self.options_data: list[dict]`
- Not used anywhere in the `lec/` library or `cli/` scripts

## Code Style

**Indentation:**
- `lec/` modules use tabs for indentation
- `gui.py` and `cli/gen_all.py` use 4-space indentation
- This inconsistency is the most prominent style issue in the codebase

**Line length:**
- No enforced limit; some `__str__` format strings in `lec/db.py` are very long (120+ characters)

**Blank lines:**
- Module-level functions and classes are separated by two blank lines in `lec/` files
- Inside `gui.py` methods are separated by one blank line, sections by a comment banner

**Section banners:**
- `lec/db.py` uses `###...###` divider comments (lines of `#`) to group related classes and functions
- `gui.py` uses `# ── Section name ──...──` banners to separate logical sections

**String formatting:**
- `lec/` uses `%`-style printf formatting throughout: `"Category: %6d | %04X | ..."  % (...)`
- `gui.py` and `cli/gen_all.py` use f-strings: `f"Caricate {len(self.options_data)} opzioni da ..."`
- Both styles coexist; new code should prefer f-strings

**`__all__` declarations:**
- Used consistently in `lec/crypto.py`, `lec/key.py`, and `lec/db.py` to define the public API of each module
- Not used in `cli/` scripts or `gui.py`

## Import Organization

**Order observed:**
1. Standard library imports (`sys`, `os`, `json`, `struct`, `io`, `subprocess`, `binascii`, `tkinter`)
2. Third-party imports (`Crypto.Cipher`, `Crypto.Cipher.Blowfish`)
3. Local/relative imports (`from .crypto import ...`, `from lec import db`, `import lec.key`)

**Relative vs absolute imports:**
- Inside the `lec/` package, relative imports are used: `from .crypto import decrypt`
- CLI scripts and `gui.py` use absolute imports after manually inserting the project root into `sys.path`:
  ```python
  sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  import lec.key
  ```
- `gui.py` uses both forms: `from lec import db` and `from lec import key as lec_key`

**No linting or formatting tool is configured** (no `.eslintrc`, `pyproject.toml`, `setup.cfg`, `.flake8`, `mypy.ini`, `.pylintrc`, or `ruff.toml` present).

## Error Handling

**Custom exceptions:**
- `LicError(Exception)` is defined in `lec/db.py` for all binary-parsing failures
- Raised with descriptive messages: `raise LicError("Unsupported type %02X" % (t))`
- No other custom exception classes exist

**Library code (`lec/`):**
- Parsing errors propagate as `LicError`; callers are expected to catch them
- `fromfile()` in `lec/db.py` uses a bare `except LicError` to fall back to `LicDBv2`:
  ```python
  def fromfile(fname):
      try:
          return LicDB(LicReader(fname))
      except LicError:
          return LicDBv2(LicReader(fname))
  ```

**GUI code (`gui.py`):**
- Uses broad `except Exception` with `traceback.format_exc()` for file-loading operations
- Shows errors to the user via `messagebox.showerror()` or `messagebox.showwarning()`
- Status bar (`_status()`) is used for non-critical feedback
- Input validation is done before calling library functions (ScopeID hex check)

**CLI scripts:**
- Use `sys.exit("Usage: ...")` for argument errors — no structured error handling
- No try/except blocks in any `cli/` file except `cli/gen_all.py` which has none at all

## Docstring and Comment Patterns

**Module-level disclaimer:**
- Every source file in `lec/` and `cli/` opens with `# educational use only` as the first line

**Module docstrings:**
- Only `gui.py` has a module-level docstring:
  ```python
  """
  LeCroy License Key Generator — GUI
  Requires: pycryptodome (pip install pycryptodome)
  """
  ```
- `build_exe.py` has a module-level docstring describing usage and output
- No other file has a module-level docstring

**Class and function docstrings:**
- None. No class or function in the project has a docstring.

**Inline comments:**
- Used to label binary format fields: `# UTF-16LE string`, `# end`, `# uint`
- Used to label unknown fields: `# ???`
- Used to group GUI sections: `# ── Row 1 — cfg path (visible only when source == "cfg") ──`
- Used to explain intent: `# Initially hide the cfg row (default source selected)`
- Comments are written in English in `lec/`; GUI section comments and some `cli/` comments are in Italian (matching the GUI language)

## Module Design

**Package structure:**
- `lec/` is a proper Python package with `__init__.py` (currently empty — one line)
- `cli/` is not a package (no `__init__.py`)
- `gui.py` is a standalone script at the project root

**Exports:**
- `lec/` modules declare explicit `__all__` lists
- `lec/__init__.py` exports nothing; callers import sub-modules directly

---

*Convention analysis: 2026-06-04*
