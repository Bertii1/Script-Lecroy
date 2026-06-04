# External Integrations

**Analysis Date:** 2026-06-04

## APIs & External Services

None. The tool operates entirely offline. There are no HTTP clients, no web APIs,
and no cloud services.

## Hardware Interface — LeCroy Oscilloscopes

**Target hardware:** LeCroy oscilloscopes (legacy models, WavePro series)

**Interaction model:** Indirect — the tool generates license key strings that are
typed into the oscilloscope's software, or reads `options.cfg` files extracted from
the instrument. No direct USB/GPIB/serial communication.

**Key structure:**
- License key format: `XXXX-XXXX-XXXX-XXXX` (16 hex chars with dashes)
- Encodes three fields: ScopeID (6 hex chars, device serial), flags byte, and a
  32-bit option bitmask
- Encryption: Blowfish ECB with byte-order reversal (`lec/crypto.py`)
- Encode/decode logic: `lec/key.py` — `encode(iid, flags, mask)` / `decode(key_str)`

**Option bitmask system:**
- Each licensable feature maps to a bit position within a page/flag byte
- 37 known options defined in `default_opts.json` across two pages (0x00 and 0x01)
- Examples: WP01 Basic Function Package (`00-00000001`), JTA Jitter Analysis
  (`00-00400000`), WavePro XL (`01-00000008`)

## Data Persistence

**No database.** There is no SQL or key-value store. All persistence is flat-file.

**`lec/db.py` — LeCroy binary options database reader:**
- Reads proprietary binary `options.cfg` files extracted from LeCroy instruments
- File format: Blowfish-encrypted binary stream; decrypted in `DecryptFile()` using
  the same key from `lec/crypto.py`
- Decrypted payload: length-prefixed, typed TLV records (TypeShort=2, TypeInt=3,
  TypeStr=8 with UTF-16LE strings)
- Two schema versions supported: `LicDB` (v1) and `LicDBv2` (v2, adds GUID field
  on components); `fromfile()` auto-detects by catching `LicError` on v1 parse
- Object model: `LicCategory`, `LicComponent`/`LicComponentV2`, `LicOption`,
  `LicProcToCat`, plus internal tables (`LicA`, `LicB`, `LicC`, `LicFlag`)
- Entry point: `lec.db.fromfile(path)` returns a `LicDB` or `LicDBv2` instance

## File Formats Read

| File | Format | Reader | Purpose |
|------|--------|--------|---------|
| `options.cfg` | Blowfish-encrypted binary TLV | `lec/db.py` | Full option database from scope |
| `default_opts.json` | JSON array | `gui.py`, `cli/gen_all.py` | Built-in fallback option list (37 entries) |

## File Formats Written

| File | Format | Writer | Purpose |
|------|--------|--------|---------|
| `codici` (plain text) | Tab-separated values | `cli/gen_all.py` | Bulk-generated key output |
| `opzioni.json` | JSON array | `cli/list.py` | Extracted option list from a `.cfg` file |
| `opzioni.txt` | Tab-separated values | (manual / prior run) | Human-readable option list |
| `chiavi_lecroy.csv` | CSV with header | `gui.py` `_export()` | GUI export of generated keys |
| `chiavi_lecroy.txt` | Tab-separated | `gui.py` `_export()` | GUI export of generated keys |

## CLI Interface

Four standalone scripts in `cli/`, each invoked directly with Python:

**`cli/gen.py`** — single key generator
```
python cli/gen.py <ScopeID_hex> <flags_hex> <mask_hex>
```
Calls `lec.key.encode()` and prints one key string to stdout.

**`cli/gen_all.py`** — batch key generator
```
python cli/gen_all.py          # prompts for ScopeID interactively
```
Reads `default_opts.json`, spawns `cli/gen.py` as a subprocess for each option,
writes tab-separated output to `codici` file in repo root.

**`cli/list.py`** — options extractor
```
python cli/list.py <options.cfg>
```
Decrypts and parses the `.cfg` file via `lec.db.fromfile()`, prints options to
stdout, and writes `opzioni.json` in the current directory.

**`cli/validate.py`** — key decoder
```
python cli/validate.py <key> [options.cfg]
```
Decodes a key via `lec.key.decode()`, prints ScopeID/flags/mask. If `options.cfg`
is provided, also resolves and prints matching option names.

## GUI Interface

**`gui.py`** — `LeCroyGUI` class, entry point `main()`

Two-tab tkinter application:

- **Tab 1 "Genera Chiavi":** Select option source (built-in JSON or external
  `options.cfg`), enter ScopeID, check options, generate keys; export to CSV or TXT
  via `tkinter.filedialog.asksaveasfilename()`
- **Tab 2 "Valida Chiave":** Enter a key string, decode it, display ScopeID/flags/mask,
  and match enabled options against the loaded option list

## Clipboard Integration

The GUI writes to the system clipboard via `tk.Tk.clipboard_append()`:
- "Copia tutto" copies all result rows (tab-separated)
- Double-click on a result row copies that single key string

## Distribution Artifact

**`LeCroy-KeyGen`** (binary, 14 MB at repo root) — PyInstaller single-file
executable bundling Python 3.12, pycryptodome, and all source modules. Targets the
build host OS (Linux ELF in the committed artifact). Windows users must rebuild on
Windows using `build_exe.py`.

---

*Integration audit: 2026-06-04*
