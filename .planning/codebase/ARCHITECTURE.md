# Architecture

**Analysis Date:** 2026-06-04

## Pattern Overview

**Overall:** Small utility tool with a layered architecture — a crypto/encoding core (`lec/`) consumed by two independent frontends (GUI and CLI scripts).

**Key Characteristics:**
- The `lec/` package is the only reusable library layer; all business logic lives there.
- GUI (`gui.py`) and CLI (`cli/`) are thin presentation layers that delegate all key math to `lec/`.
- No shared state between sessions; every key generation is a stateless, pure function call.
- The crypto key and cipher are module-level singletons initialized once at import time (`lec/crypto.py`).

---

## Layers

**Crypto Primitive Layer:**
- Purpose: Blowfish ECB encryption/decryption with a hardcoded, obfuscated key.
- Location: `lec/crypto.py`
- Contains: `encrypt(blk)`, `decrypt(blk)`, byte-reversal helper `revd(blk)`, module-level `cipher` singleton.
- Depends on: `pycryptodome` (`Crypto.Cipher.Blowfish`)
- Used by: `lec/key.py`, `lec/db.py`

**Key Encoding/Decoding Layer:**
- Purpose: Packs oscilloscope license parameters into an 8-byte plaintext block, encrypts it with Blowfish, and formats the result as a human-readable `XXXX-XXXX-XXXX-XXXX` hex string; also reverses the process for validation.
- Location: `lec/key.py`
- Contains: `encode(iid, flags, mask) -> str`, `decode(ok) -> (iid, flags, mask)`
- Depends on: `lec/crypto.py`
- Used by: `gui.py`, `cli/gen.py`, `cli/validate.py`

**Database / Options File Layer:**
- Purpose: Reads and decrypts a proprietary binary `options.cfg` file (LeCroy's encrypted license database) into structured Python objects.
- Location: `lec/db.py`
- Contains: `LicReader`, `LicDB`, `LicDBv2`, `fromfile(fname)`, several `Lic*` record classes (`LicCategory`, `LicComponent`, `LicOption`, etc.), `DecryptFile()`, `LoadGroup()`.
- Depends on: `lec/crypto.py`
- Used by: `gui.py`, `cli/list.py`, `cli/validate.py`

**GUI Frontend:**
- Purpose: Interactive desktop application for generating and validating license keys. Provides option selection, batch generation, clipboard copy, CSV/TXT export, and key decoding.
- Location: `gui.py`
- Contains: `LeCroyGUI` class (~680 lines), `main()` entry point.
- Depends on: `lec/key.py`, `lec/db.py`, `tkinter`, `default_opts.json`
- Used by: End users; also packaged as a standalone binary via `build_exe.py`.

**CLI Scripts:**
- Purpose: Lightweight command-line tools for scripting and batch use.
- Location: `cli/`
- Contains: `gen.py`, `gen_all.py`, `list.py`, `validate.py`
- Depends on: `lec/key.py` (gen, validate), `lec/db.py` (list, validate), `default_opts.json` (gen_all)
- Used by: Operators running scripts directly.

**Build Script:**
- Purpose: Packages `gui.py` and the `lec/` package into a single-file standalone executable using PyInstaller.
- Location: `build_exe.py`
- Depends on: PyInstaller (dev-only dependency), `gui.py`, `lec/`

---

## Data Flow

**Key Generation (encode path):**

1. User supplies a **ScopeID** (6 hex digit oscilloscope serial), a **flags** byte (page/type selector), and a **mask** (32-bit bitmask of enabled features).
2. `lec/key.py::encode(iid, flags, mask)` packs these into an 8-byte big-endian struct:
   - First 4 bytes: `(iid_reordered << 8) | flags`
   - Last 4 bytes: `mask`
   - The byte order of the three ScopeID bytes is conditionally swapped based on bit 6 of `flags` (`0x40`).
3. The 8-byte block is passed to `lec/crypto.py::encrypt(blk)`:
   - Byte order is reversed (`revd`) before Blowfish ECB encryption.
   - Byte order is reversed again on the ciphertext output.
4. The 8-byte ciphertext is hex-encoded, uppercased, and split into four 4-char groups separated by `-` to produce the final key string (e.g., `A1B2-C3D4-E5F6-A7B8`).

**Key Validation (decode path):**

1. User provides a `XXXX-XXXX-XXXX-XXXX` key string.
2. `lec/key.py::decode(ok)` strips dashes, unhexlifies to 8 bytes, calls `lec/crypto.py::decrypt(blk)`.
3. The 8-byte plaintext is unpacked: first 3 bytes + flags byte + 4-byte mask.
4. ScopeID is reconstructed by reversing the conditional byte swap.
5. Returns `(iid, flags, mask)` tuple.

**Options Database Load (options.cfg path):**

1. `lec/db.py::fromfile(fname)` opens the binary `options.cfg` file.
2. `LicReader` decrypts the entire file in 8-byte Blowfish blocks (`DecryptFile`).
3. The decrypted bytes are parsed as a typed record stream (little-endian shorts, ints, and UTF-16LE strings).
4. Records are grouped into `LicDB` or `LicDBv2` (auto-detected by catching `LicError` on the first parse attempt).
5. The `options` dict (`{idx: LicOption}`) is exposed for downstream use.
6. GUI and CLI map each `LicOption` to `(page, bit)` → `(flags, mask)` for key generation.

**State Management:**
- No persistent state. The GUI holds in-memory `options_data` list for the current session.
- `lec/crypto.py` holds a module-level `cipher` object (Blowfish instance, stateless for ECB mode).

---

## Key Abstractions

**`LicOption`:**
- Purpose: Represents one licensable feature parsed from `options.cfg`.
- Examples: `lec/db.py` lines 157–175
- Key fields: `name` (short key like `"JTA"`), `description`, `page` (flags byte), `bit` (bit position within the mask word), `idx` (composite index combining page and bit position).

**`LicDB` / `LicDBv2`:**
- Purpose: Container for all parsed record groups from `options.cfg`.
- Examples: `lec/db.py` lines 247–301
- Pattern: `LicDB` handles the original format; `LicDBv2` handles an extended format with an extra `guid` field on components. `fromfile()` tries `LicDB` first and falls back to `LicDBv2`.

**`LeCroyGUI`:**
- Purpose: Single-class encapsulation of the entire GUI application.
- Examples: `gui.py` lines 79–670
- Pattern: Methods prefixed `_build_*` construct UI widgets; methods prefixed `_` are internal logic; `_do_generate()` is the central generation dispatcher calling `lec_key.encode()`.

---

## Entry Points

**GUI:**
- Location: `gui.py`, `main()` at line 675
- Triggers: `python gui.py` or the compiled `dist/LeCroy-KeyGen` binary
- Responsibilities: Full interactive session — load options, accept ScopeID, generate/validate keys, export results.

**CLI — single key generation:**
- Location: `cli/gen.py`
- Triggers: `python cli/gen.py <ScopeID_hex> <flags_hex> <mask_hex>`
- Responsibilities: Print one key to stdout.

**CLI — batch generation:**
- Location: `cli/gen_all.py`
- Triggers: `python cli/gen_all.py` (interactive ScopeID prompt)
- Responsibilities: Iterate `default_opts.json`, invoke `cli/gen.py` via subprocess for each option, write results to a `codici` file.

**CLI — list options:**
- Location: `cli/list.py`
- Triggers: `python cli/list.py <options.cfg>`
- Responsibilities: Decrypt and pretty-print all options from a binary `options.cfg`; export to `opzioni.json`.

**CLI — validate/decode:**
- Location: `cli/validate.py`
- Triggers: `python cli/validate.py <key> [options.cfg]`
- Responsibilities: Decode a key back to ScopeID/flags/mask; optionally resolve option names from `options.cfg`.

---

## Error Handling

**Strategy:** Minimal. Errors propagate as exceptions; GUI catches them with `messagebox.showerror`; CLI scripts let exceptions terminate the process.

**Patterns:**
- `lec/db.py` defines `LicError(Exception)` for malformed binary data.
- `fromfile()` uses a try/except on `LicError` to select between `LicDB` and `LicDBv2` format.
- GUI wraps key generation and file loading in bare `except Exception` blocks, displaying tracebacks in error dialogs.
- CLI scripts perform no error handling beyond argument count checks.

---

## Cross-Cutting Concerns

**Logging:** None. `print()` only in CLI scripts and `db.py` when run as `__main__`.
**Validation:** Minimal. GUI validates ScopeID length/hex characters before calling `encode`. CLI scripts do not validate input beyond argument count.
**Authentication:** Not applicable — this is a standalone offline tool.

---

*Architecture analysis: 2026-06-04*
