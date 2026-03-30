# LeCroy Options Recovery

Tool for generating, validating and decoding license keys for LeCroy oscilloscopes.

> **For educational use only.** Compatible with X-Stream firmware versions prior to 8.x.x and with the vxfusion platform (DDA/WP9xx) version 9.3.0.

---

## Requirements

- Python 2.7.x
- PyCrypto (`pip install pycrypto`) or PyCryptodome (`pip install pycryptodome`)
- Visual C++ Compiler for Python 2.7 (Windows only, required by PyCrypto)

---

## Directory structure

```
script-papa/
├── lec/
│   ├── __init__.py
│   ├── crypto.py
│   ├── db.py
│   └── key.py
├── gen.py
├── list.py
└── validate.py
```

---

## Quick start

### 1. List available options

```
python list.py "X-STREAM options.cfg"
```

Example output:
```
00-00000001  BasicFFT             Basic FFT Package
00-00000008  Histogram            Histogram/Trend Package
...
```

### 2. Generate a key

```
python gen.py <ScopeID> <flags> <mask>
```

- `ScopeID`: the first 6 hex characters of the Scope ID (the part **before** the dash)
- `flags`: column 1 from list.py output (e.g. `00`)
- `mask`: column 2 from list.py output (e.g. `00000008`)

**Example:**
```
python gen.py 2F0DAB 00 00000008
```

Output: `XXXX-XXXX-XXXX-XXXX` — the key to enter into the scope.

### 3. Validate an existing key

```
python validate.py <key>
python validate.py <key> "X-STREAM options.cfg"
```

---

## Where to find the ScopeID

On the scope menu: **Utility > Utility Setup > Options tab**

The field shows e.g. `ScopeID: 2F0DAB-DE` — use **only** `2F0DAB` (the 6 characters before the dash).

---

## Where to find options.cfg

- **Windows-based scope (X-Stream):** `C:\Program Files\Lecroy\X-STREAM options.cfg`
- **vxfusion scope (DDA/WP9xx):** extract from the firmware package using innoextract or 7-Zip
- **Via remote command:** `app.Utility.Options.ScopeID`

For full details see [DOCUMENTATION.md](DOCUMENTATION.md).