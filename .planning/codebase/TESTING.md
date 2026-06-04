# Testing Patterns

**Analysis Date:** 2026-06-04

## Test Framework

**Runner:** None configured

**Assertion Library:** None

**Test files present:** 0 (zero)

There is no test suite of any kind in this project. No `pytest`, `unittest`, `nose2`, or any other test runner is installed or configured. No `pyproject.toml`, `setup.cfg`, or `pytest.ini` file exists to configure one.

The only test files in the repository tree belong to third-party packages inside the vendored virtualenv (`lib/python3.12/site-packages/`) and are not part of this project.

**Run Commands:**
```bash
# No test commands exist. These would need to be added:
pytest                  # run all tests (after installing pytest)
pytest --tb=short       # shorter tracebacks
pytest --cov=lec        # coverage for the lec package
```

## Current Coverage

**Overall: 0%**

No source file in `lec/`, `cli/`, or `gui.py` is exercised by any automated test. The crypto, key encoding/decoding, binary parsing, and GUI logic are all entirely untested.

## Test File Organization

**Current state:** No `tests/` directory, no `test_*.py` files, no `*_test.py` files exist anywhere in the project source tree.

**Recommended layout when adding tests:**
```
Script-Lecroy/
├── tests/
│   ├── __init__.py
│   ├── test_crypto.py      # lec/crypto.py
│   ├── test_key.py         # lec/key.py
│   ├── test_db.py          # lec/db.py
│   └── test_gui.py         # gui.py (optional, harder to test)
├── lec/
├── cli/
└── gui.py
```

## Testing Gaps

### Critical — `lec/key.py` (encode/decode roundtrip)

The `encode()` and `decode()` functions in `lec/key.py` are the core of the project. They are pure functions with no side effects and are trivially testable. The most important invariant — that `decode(encode(iid, flags, mask))` returns the original inputs — is never verified.

Files: `lec/key.py`

What to test:
- `encode()` produces a correctly formatted `XXXX-XXXX-XXXX-XXXX` string
- `decode(encode(iid, flags, mask))` roundtrips back to `(iid, flags, mask)`
- Known good key/value pairs (regression test against real LeCroy keys if available)
- Edge cases: `iid=0`, `mask=0xFFFFFFFF`, flag bit 0x40 set vs unset (the byte-swap branch)
- Invalid input to `decode()` raises an exception

### Critical — `lec/crypto.py` (encrypt/decrypt roundtrip)

`encrypt()` and `decrypt()` in `lec/crypto.py` are pure functions. The invariant `decrypt(encrypt(x)) == x` for any 8-byte block is never tested.

Files: `lec/crypto.py`

What to test:
- `decrypt(encrypt(blk)) == blk` for a range of 8-byte inputs
- `revd(revd(blk)) == blk` (double reversal is identity)
- Known ciphertext/plaintext pairs if available

### High — `lec/db.py` (binary file parsing)

`LicReader`, `LicDB`, `LicDBv2`, and `fromfile()` parse a proprietary binary format. Parsing failures are silent (the `fromfile()` fallback swallows `LicError` without logging). No test exercises the parser against a known-good `.cfg` file.

Files: `lec/db.py`

What to test:
- `fromfile()` returns a `LicDB` for a valid v1 `.cfg` file
- `fromfile()` falls back to `LicDBv2` for a v2 `.cfg` file
- `LicReader.get()` raises `LicError` on truncated input
- `LicReader.get()` raises `LicError` on an unsupported type byte
- `LoadGroup()` returns a correctly keyed dict

### Medium — `cli/` scripts (argument validation)

The CLI scripts use `sys.exit()` for argument errors and do no validation of hex input values. There is no way to unit-test them as currently written (logic is at module level, not inside functions).

Files: `cli/gen.py`, `cli/list.py`, `cli/validate.py`, `cli/gen_all.py`

What would need to change first: wrap top-level logic in a `main()` function so it can be imported and called in tests without executing immediately.

### Low — `gui.py` (GUI interaction)

GUI testing with `tkinter` requires either `unittest.mock` to patch the Tk root or a full UI automation framework. This is lower priority given the project scope.

Files: `gui.py`

What to test (if pursued):
- `_get_scope_iid()` validation logic (pure logic inside a method, easy to extract)
- `_load_default_options()` parses `default_opts.json` correctly
- `_do_generate()` calls `lec_key.encode()` and populates the result tree

## Recommended Testing Approach

### Framework

Use `pytest` — it is the de-facto standard for Python projects, requires no test class boilerplate, and has excellent plugin support.

```bash
pip install pytest pytest-cov
```

### Priority order

1. Add roundtrip tests for `lec/key.py` — highest value, zero setup required, pure functions
2. Add roundtrip tests for `lec/crypto.py` — same rationale
3. Add parsing tests for `lec/db.py` — requires a fixture `.cfg` file (binary blob committed to `tests/fixtures/`)
4. Refactor `cli/` scripts to use `main()` functions, then add subprocess or direct call tests

### Example test structure for `lec/key.py`

```python
# tests/test_key.py
import pytest
from lec.key import encode, decode

def test_roundtrip_basic():
    iid, flags, mask = 0x1A2B3C, 0x00, 0x00000001
    key = encode(iid, flags, mask)
    assert decode(key) == (iid, flags, mask)

def test_key_format():
    key = encode(0x123456, 0x00, 0x00000001)
    parts = key.split("-")
    assert len(parts) == 4
    assert all(len(p) == 4 for p in parts)

def test_flag_0x40_branch():
    # exercises the byte-swap path
    iid, flags, mask = 0xAABBCC, 0x40, 0x00000002
    key = encode(iid, flags, mask)
    assert decode(key) == (iid, flags, mask)

def test_decode_invalid_key_raises():
    with pytest.raises(Exception):
        decode("ZZZZ-ZZZZ-ZZZZ-ZZZZ")
```

### Example test structure for `lec/crypto.py`

```python
# tests/test_crypto.py
from lec.crypto import encrypt, decrypt

def test_decrypt_encrypt_roundtrip():
    for blk in [b'\x00' * 8, b'\xff' * 8, b'\x01\x02\x03\x04\x05\x06\x07\x08']:
        assert decrypt(encrypt(blk)) == blk

def test_encrypt_decrypt_roundtrip():
    for blk in [b'\x00' * 8, b'\xde\xad\xbe\xef\xca\xfe\xba\xbe']:
        assert encrypt(decrypt(blk)) == blk
```

### Fixtures for `lec/db.py`

A minimal binary `.cfg` fixture would need to be crafted or extracted from a real device and committed to `tests/fixtures/options.cfg`. Without a fixture file the parser cannot be tested without significant mocking effort.

## Minimum Viable Test Suite (MVP)

To reach a baseline of confidence without major refactoring, the following 10–15 tests covering `lec/key.py` and `lec/crypto.py` would immediately protect the core logic. This requires no changes to existing source files.

| Module | Tests | Effort |
|---|---|---|
| `lec/crypto.py` | 4 roundtrip tests | ~30 min |
| `lec/key.py` | 6 roundtrip + format + edge tests | ~45 min |
| `lec/db.py` | 4 parser tests (needs fixture) | ~2 h |
| `cli/` | Requires refactor first | High effort |
| `gui.py` | Optional, low ROI | High effort |

---

*Testing analysis: 2026-06-04*
