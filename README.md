# LeCroy Options Recovery

Tool per la generazione, validazione e decodifica di chiavi di licenza per oscilloscopi LeCroy.

> **Solo uso didattico/educativo.** Compatibile con firmware X-Stream precedenti alla versione 8.x.x e con piattaforma vxfusion (DDA/WP9xx) versione 9.3.0.

---

## Requisiti

- Python 2.7.x
- PyCrypto (`pip install pycrypto`) oppure PyCryptodome (`pip install pycryptodome`)
- Visual C++ Compiler for Python 2.7 (solo Windows, richiesto da PyCrypto)

---

## Struttura directory

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

## Uso rapido

### 1. Trovare le opzioni disponibili

```
python list.py "X-STREAM options.cfg"
```

Output esempio:
```
00-00000001  BasicFFT             Basic FFT Package
00-00000008  Histogram            Histogram/Trend Package
...
```

### 2. Generare una chiave

```
python gen.py <ScopeID> <flags> <mask>
```

- `ScopeID`: i primi 6 caratteri hex del Scope ID (la parte **prima** del trattino)
- `flags`: colonna 1 dell'output di list.py (es. `00`)
- `mask`: colonna 2 dell'output di list.py (es. `00000008`)

**Esempio:**
```
python gen.py 2F0DAB 00 00000008
```

Output: `XXXX-XXXX-XXXX-XXXX` — la chiave da inserire nello scope.

### 3. Validare una chiave esistente

```
python validate.py <chiave>
python validate.py <chiave> "X-STREAM options.cfg"
```

---

## Dove trovare il ScopeID

Sul menu dello scope: **Utility > Utility Setup > tab Options**

Il campo mostra ad esempio `ScopeID: 2F0DAB-DE` — usare **solo** `2F0DAB` (i 6 caratteri prima del trattino).

---

## Dove trovare options.cfg

- **Scope Windows-based (X-Stream):** `C:\Program Files\Lecroy\X-STREAM options.cfg`
- **Scope vxfusion (DDA/WP9xx):** estrarre dal pacchetto firmware con innoextract o 7-Zip
- **Via comando remoto:** `app.Utility.Options.ScopeID`

Per dettagli completi vedere [DOCUMENTATION.md](DOCUMENTATION.md).
