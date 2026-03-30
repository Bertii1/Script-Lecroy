# Technical Documentation — LeCroy Options Recovery

> For educational use only.

---

## Table of contents

1. [Compatibility](#compatibility)
2. [Installing dependencies](#installing-dependencies)
3. [The ScopeID](#the-scopeid)
4. [The options.cfg file](#the-optionscfg-file)
5. [Script: list.py](#script-listpy)
6. [Script: gen.py](#script-genpy)
7. [Script: validate.py](#script-validatepy)
8. [Flags and mask structure](#flags-and-mask-structure)
9. [Generated key format](#generated-key-format)
10. [Internal architecture](#internal-architecture)
11. [Notes for specific models](#notes-for-specific-models)
12. [Common issues](#common-issues)

---

## Compatibility

| Platform | Firmware | Compatible |
|---|---|---|
| X-Stream (WaveRunner, WavePro, SDA...) | < 8.x.x | YES |
| X-Stream | >= 8.x.x | NO (encryption changed) |
| vxfusion (DDA260, DDA120, WP9xx, J260) | 9.3.0 | YES |

Starting from X-Stream 8.0.0.0, LeCroy changed the encryption method for the options database, making these tools incompatible with modern firmware versions.

---

## Installing dependencies

### Windows

```bat
:: 1. Install Python 2.7.18 from python.org/downloads/release/python-2718/

:: 2. Install Visual C++ Compiler for Python 2.7
::    Search for "Microsoft Visual C++ Compiler for Python 2.7" on the Microsoft website

:: 3. Install PyCrypto
pip install pycrypto

:: If pycrypto fails on Windows 10/11, use pycryptodome (drop-in replacement)
pip install pycryptodome
```

### Linux / macOS

```bash
pip install pycrypto
# or
pip install pycryptodome
```

---

## The ScopeID

### Format

The ScopeID is displayed by the scope in the following format:

```
XXXXXX-YY
```

Where:
- `XXXXXX` = 6 hexadecimal characters = 3 bytes = the **instrument identifier** (iid)
- `-YY` = 2 hexadecimal characters = 1 byte = suffix (checksum or model code), **not used by the scripts**

Examples: `2F0DAB-DE` or `8cc6ee-79`

### How to find it

**Scope menu (X-Stream and vxfusion):**

```
Utility > Utility Setup > "Options" tab
```

The `ScopeID` field displays the full value.

**Via remote command (xStreamBrowser or GPIB/LAN):**

```
app.Utility.Options.ScopeID
app.Utility.Options.SerialNum
```

### Which part to use with gen.py

**Use ONLY the 6 characters before the dash.**

```
ScopeID shown on scope:  2F0DAB-DE
Parameter for gen.py:    2F0DAB
```

**Technical reason:** `gen.py` calls `int(argv[1], 16)` and `key.py` treats the iid as a 24-bit integer (3 bytes). Passing the full `2F0DABDE` (32-bit) causes the most significant byte to overwrite an intermediate byte in the calculations, producing an incorrect key. The `-DE` suffix is not part of the cryptographic identifier.

---

## The options.cfg file

The `X-STREAM options.cfg` file is a database **encrypted with Blowfish** (the same algorithm used for keys) that contains the complete map of all available options for the platform.

### Where to find it

**X-Stream scope (Windows XP/7 embedded):**

The file is present in the scope's filesystem:
```
C:\Program Files\Lecroy\X-STREAM options.cfg
```
Accessible by connecting a keyboard/mouse and copying via USB.

**From the firmware package (Windows installer):**

X-Stream firmware is distributed as an Inno Setup installer:
```
xstreamdsoinstaller_x.x.x.x.exe
```
Extract the contents using one of the following tools without running the installer:

```bash
# innoextract (cross-platform)
innoextract xstreamdsoinstaller_7.9.x.x.exe

# innounp (Windows)
innounp -x xstreamdsoinstaller_7.9.x.x.exe
```

After extraction, look for the `X-STREAM options.cfg` file.

**Firmware downloads:**
- WaveRunner: https://www.teledynelecroy.com/support/softwaredownload/documents.aspx?sc=9
- WavePro: https://www.teledynelecroy.com/support/softwaredownload/documents.aspx?sc=11
- SDA: https://www.teledynelecroy.com/support/softwaredownload/documents.aspx?sc=16

> Use firmware versions **7.9.x.x or earlier**. Versions 8.x+ contain an options.cfg with an incompatible format.

**vxfusion scope (DDA, WP9xx):**

vxfusion firmware is a binary VxWorks image (not an Inno Setup installer). Try extracting its contents with 7-Zip or binwalk. Alternatively, contact the LeCroy Owners' Group on EEVblog.

### Database versions

`db.py` handles two format versions:
- **LicDB (v1):** original format
- **LicDBv2 (v2):** adds a `guid` field for each component

`fromfile()` first attempts v1 parsing; if it fails, v2 is used automatically.

---

## Script: list.py

Reads and decodes `options.cfg`, listing all available options with their flags and mask codes.

### Usage

```
python list.py <options.cfg>
```

### Output

```
FLAGS-MASK      NAME                 DESCRIPTION
00-00000001     BasicFFT             Basic FFT Package
00-00000002     BasicFunc            Basic Function Package
00-00000008     Histogram            Histogram/Trend Package
01-00000001     JitterPkg            Jitter and Timing Analysis
...
```

Each line represents an option (or group of options sharing the same key).

- **FLAGS** (2 hex): corresponds to the `<flags>` parameter of gen.py
- **MASK** (8 hex): corresponds to the `<mask>` parameter of gen.py

---

## Script: gen.py

Generates a license key for a specific scope.

### Usage

```
python gen.py <ScopeID> <flags> <mask>
```

| Parameter | Type | Description |
|---|---|---|
| `ScopeID` | hex, 6 chars | The 6 characters before the dash in the ScopeID |
| `flags` | hex, 2 chars | Options page (column 1 from list.py) |
| `mask` | hex, 8 chars | Options bitmask (column 2 from list.py) |

### Example

```
python gen.py 2F0DAB 00 00000008
```

Output:
```
A3F1-2B4C-9E87-D012
```

This key must be entered in the scope menu: **Utility > Utility Setup > Options > Add Key**.

### Combining multiple options

If multiple options share the same `flags` value, they can be enabled with **a single key** by performing a bitwise OR of their masks.

Example: enabling `00-00000001` and `00-00000008` together:

```
python gen.py 2F0DAB 00 00000009
```

(`00000001 | 00000008 = 00000009`)

> Options with different flags values cannot be combined: each flags value requires a separate key.

---

## Script: validate.py

Decodes an existing key and displays its components (ScopeID, flags, mask). When the options.cfg file is provided, it also resolves the names of the enabled options.

### Usage

```
python validate.py <key>
python validate.py <key> <options.cfg>
```

### Example

```
python validate.py A3F1-2B4C-9E87-D012
```

Output:
```
ScopeID: 2F0DAB
Flags:   00
Mask:    00000008
```

With options.cfg:

```
python validate.py A3F1-2B4C-9E87-D012 "X-STREAM options.cfg"
```

Output:
```
ScopeID: 2F0DAB
Flags:   00
Mask:    00000008
Options:
00-00000008  Histogram            Histogram/Trend Package
```

**Practical use:** if you have keys already installed on the scope but have lost track of what they do, validate.py lets you identify exactly which options they enable.

---

## Flags and mask structure

### flags

The `flags` byte selects the options register "page". The relevant bits are:

| Bit | Value | Effect |
|---|---|---|
| 0 | 0x01 | Page 1 (second group of 32 options) |
| 1 | 0x02 | Page 2 |
| 6 | 0x40 | Swaps bytes b0/b1 of the iid during encoding |

The page index used for the options.cfg lookup is `flags & 0x43`.

For most common options, flags is `00` or `01`.

### mask

The `mask` field is a 32-bit integer where each bit corresponds to a specific option on the page selected by `flags`. Each set bit (=1) enables the corresponding option.

Example: `mask = 0x00000009` enables bit 0 and bit 3 simultaneously.

---

## Generated key format

Keys always follow this format:

```
XXXX-XXXX-XXXX-XXXX
```

16 uppercase hexadecimal characters split into 4 groups of 4, separated by dashes.

Internally they are 8 bytes encrypted with Blowfish ECB encoding:
- 3 bytes: iid (ScopeID)
- 1 byte: flags
- 4 bytes: mask

---

## Internal architecture

```
gen.py / validate.py
        |
        v
    lec/key.py          encode() / decode()
        |
        v
    lec/crypto.py       encrypt() / decrypt()  [Blowfish ECB]
```

```
list.py / validate.py
        |
        v
    lec/db.py           fromfile() -> LicDB / LicDBv2
        |
        v
    lec/crypto.py       DecryptFile()  [Blowfish ECB, 8-byte blocks]
```

### lec/crypto.py

Implements Blowfish ECB encryption on 8-byte blocks. The Blowfish key is hardcoded in the source (16 bytes, obfuscated with XOR). The `revd()` function reverses the byte order of the two DWORDs before and after each encryption operation (endianness handling).

### lec/key.py

- `encode(iid, flags, mask)`: builds the plaintext `[iid(3B) | flags(1B) | mask(4B)]` in big-endian, encrypts it with Blowfish, returns the ciphertext as a `XXXX-XXXX-XXXX-XXXX` string.
- `decode(ok)`: strips dashes from the key, decrypts, returns `(iid, flags, mask)`.

### lec/db.py

Reads `options.cfg` by decrypting it block by block (8 bytes at a time). The decrypted format is a binary stream with typed records:

| Type ID | Data type | Size |
|---|---|---|
| `0x02` | Short (uint16) | 2 bytes |
| `0x03` | Int (uint32) | 4 bytes |
| `0x08` | String (UTF-16LE) | 4-byte length + N bytes |
| `0x00` | End of stream | — |

The main structures in the database are: categories, components, mappings, options, enable flags.

---

## Notes for specific models

### DDA260 / DDA120 / WP9xx (vxfusion 9.3.0)

- The scope **does not run Windows**: it uses VxWorks, so direct filesystem access to copy `options.cfg` is not possible.
- The ScopeID is found under **Utility > Utility Setup > Options**.
- The vxfusion firmware is simply named `vxfusion` (VxWorks binary image).
- The ScopeID suffix (e.g. `-DE`) is model-specific but does not affect key generation.
- Confirmed working: DDA-120 with firmware 9.3.0 (source: EEVblog forum + fetaudio.com).

### WaveRunner Xi/MXi/6000 (X-Stream < 8.x.x)

- Runs on Windows XP embedded.
- `options.cfg` is located at `C:\Program Files\Lecroy\`.
- Accessible via USB after connecting a keyboard and mouse.

---

## Common issues

### `ImportError: No module named Crypto`

PyCrypto is not installed or cannot be found.

```bat
pip install pycrypto
:: or, if the above fails on Windows 10/11:
pip install pycryptodome
```

### `ValueError: invalid literal for int() with base 16`

The ScopeID passed to gen.py contains non-hexadecimal characters. Make sure to use only the 6 characters before the dash (e.g. `2F0DAB` instead of `2F0DAB-DE`).

### `list.py` produces no output / file error

The `options.cfg` file is from version 8.x or later, which is incompatible. Use an `options.cfg` from firmware 7.9.x.x or earlier.

### The generated key is not accepted by the scope

- Make sure you are using the correct ScopeID for the target scope (not one from a different instrument).
- Make sure the flags and mask correspond to real options present in the database.
- Check firmware compatibility.

### `IOError` or file open error

Make sure the path to `options.cfg` is correct and the file is not open by another process.