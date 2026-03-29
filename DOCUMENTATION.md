# Documentazione Tecnica — LeCroy Options Recovery

> Solo uso didattico/educativo.

---

## Indice

1. [Compatibilità](#compatibilità)
2. [Installazione dipendenze](#installazione-dipendenze)
3. [Il ScopeID](#il-scopeid)
4. [Il file options.cfg](#il-file-optionscfg)
5. [Script: list.py](#script-listpy)
6. [Script: gen.py](#script-genpy)
7. [Script: validate.py](#script-validatepy)
8. [Struttura flags e mask](#struttura-flags-e-mask)
9. [Formato della chiave generata](#formato-della-chiave-generata)
10. [Architettura interna](#architettura-interna)
11. [Note per modelli specifici](#note-per-modelli-specifici)
12. [Problemi comuni](#problemi-comuni)

---

## Compatibilità

| Piattaforma | Firmware | Compatibile |
|---|---|---|
| X-Stream (WaveRunner, WavePro, SDA...) | < 8.x.x | SI |
| X-Stream | >= 8.x.x | NO (cifratura cambiata) |
| vxfusion (DDA260, DDA120, WP9xx, J260) | 9.3.0 | SI |

A partire da X-Stream 8.0.0.0 LeCroy ha modificato il metodo di cifratura del database opzioni, rendendo questi tool incompatibili con le versioni moderne.

---

## Installazione dipendenze

### Windows

```bat
:: 1. Installa Python 2.7.18 da python.org/downloads/release/python-2718/

:: 2. Installa Visual C++ Compiler for Python 2.7
::    Cerca "Microsoft Visual C++ Compiler for Python 2.7" sul sito Microsoft

:: 3. Installa PyCrypto
pip install pycrypto

:: Se pycrypto fallisce su Windows 10/11, usa pycryptodome (drop-in replacement)
pip install pycryptodome
```

### Linux / macOS

```bash
pip install pycrypto
# oppure
pip install pycryptodome
```

---

## Il ScopeID

### Formato

Il ScopeID viene visualizzato dallo scope nel formato:

```
XXXXXX-YY
```

Dove:
- `XXXXXX` = 6 caratteri esadecimali = 3 byte = l'**identificativo strumento** (iid)
- `-YY` = 2 caratteri esadecimali = 1 byte = suffisso (checksum o codice modello), **non usato dagli script**

Esempio: `2F0DAB-DE` oppure `8cc6ee-79`

### Come trovarlo

**Menu scope (X-Stream e vxfusion):**

```
Utility > Utility Setup > tab "Options"
```

Il campo `ScopeID` mostra il valore completo.

**Via comando remoto (xStreamBrowser o GPIB/LAN):**

```
app.Utility.Options.ScopeID
app.Utility.Options.SerialNum
```

### Quale parte usare con gen.py

**Usare SOLO i 6 caratteri prima del trattino.**

```
ScopeID visualizzato:  2F0DAB-DE
Parametro per gen.py:  2F0DAB
```

**Motivazione tecnica:** `gen.py` esegue `int(argv[1], 16)` e `key.py` tratta l'iid come intero a 24 bit (3 byte). Se si passa l'intero `2F0DABDE` (32 bit), il byte più significativo sovrascrive quello intermedio nei calcoli, producendo una chiave errata. Il suffisso `-DE` non fa parte dell'identificativo crittografico.

---

## Il file options.cfg

Il file `X-STREAM options.cfg` è un database **cifrato con Blowfish** (stesso algoritmo usato per le chiavi) che contiene la mappa completa di tutte le opzioni disponibili per la piattaforma.

### Dove trovarlo

**Scope X-Stream (Windows XP/7 embedded):**

Il file è presente nel filesystem dello scope:
```
C:\Program Files\Lecroy\X-STREAM options.cfg
```
Accessibile collegando tastiera/mouse e copiando via USB.

**Dal pacchetto firmware (installer Windows):**

Il firmware X-Stream è distribuito come installer Inno Setup:
```
xstreamdsoinstaller_x.x.x.x.exe
```
Estrarre il contenuto con uno dei seguenti tool senza eseguire l'installer:

```bash
# innoextract (cross-platform)
innoextract xstreamdsoinstaller_7.9.x.x.exe

# innounp (Windows)
innounp -x xstreamdsoinstaller_7.9.x.x.exe
```

Dopo l'estrazione cercare il file `X-STREAM options.cfg`.

**Download firmware:**
- WaveRunner: https://www.teledynelecroy.com/support/softwaredownload/documents.aspx?sc=9
- WavePro: https://www.teledynelecroy.com/support/softwaredownload/documents.aspx?sc=11
- SDA: https://www.teledynelecroy.com/support/softwaredownload/documents.aspx?sc=16

> Usare versioni firmware **7.9.x.x o precedenti**. Le versioni 8.x+ contengono un options.cfg con formato incompatibile.

**Scope vxfusion (DDA, WP9xx):**

Il firmware vxfusion è un'immagine VxWorks binaria (non un installer Inno Setup). Provare a estrarne il contenuto con 7-Zip o binwalk. In alternativa contattare la LeCroy Owners' Group su EEVblog.

### Versioni del database

`db.py` gestisce due versioni del formato:
- **LicDB (v1):** formato originale
- **LicDBv2 (v2):** aggiunge un campo `guid` per ogni componente

`fromfile()` tenta prima il parsing v1; se fallisce usa v2 automaticamente.

---

## Script: list.py

Legge e decodifica `options.cfg`, elencando tutte le opzioni disponibili con i relativi codici flags e mask.

### Uso

```
python list.py <options.cfg>
```

### Output

```
FLAGS-MASK      NOME                 DESCRIZIONE
00-00000001     BasicFFT             Basic FFT Package
00-00000002     BasicFunc            Basic Function Package
00-00000008     Histogram            Histogram/Trend Package
01-00000001     JitterPkg            Jitter and Timing Analysis
...
```

Ogni riga rappresenta una opzione (o gruppo di opzioni con la stessa chiave).

- **FLAGS** (2 hex): corrisponde al parametro `<flags>` di gen.py
- **MASK** (8 hex): corrisponde al parametro `<mask>` di gen.py

---

## Script: gen.py

Genera una chiave di licenza per uno scope specifico.

### Uso

```
python gen.py <ScopeID> <flags> <mask>
```

| Parametro | Tipo | Descrizione |
|---|---|---|
| `ScopeID` | hex, 6 char | I 6 caratteri prima del trattino del ScopeID |
| `flags` | hex, 2 char | Pagina opzioni (colonna 1 di list.py) |
| `mask` | hex, 8 char | Bitmask opzioni (colonna 2 di list.py) |

### Esempio

```
python gen.py 2F0DAB 00 00000008
```

Output:
```
A3F1-2B4C-9E87-D012
```

Questa chiave va inserita nel menu dello scope: **Utility > Utility Setup > Options > Add Key**.

### Combinare più opzioni

Se più opzioni hanno lo stesso valore di `flags`, possono essere abilitate con **una sola chiave** eseguendo l'OR bitwise delle loro mask.

Esempio: abilitare `00-00000001` e `00-00000008` insieme:

```
python gen.py 2F0DAB 00 00000009
```

(`00000001 | 00000008 = 00000009`)

> Non si possono combinare opzioni con flags diversi: ogni flags richiede una chiave separata.

---

## Script: validate.py

Decodifica una chiave esistente e ne mostra i componenti (ScopeID, flags, mask). Con il file options.cfg risolve anche i nomi delle opzioni abilitate.

### Uso

```
python validate.py <chiave>
python validate.py <chiave> <options.cfg>
```

### Esempio

```
python validate.py A3F1-2B4C-9E87-D012
```

Output:
```
ScopeID: 2F0DAB
Flags:   00
Mask:    00000008
```

Con options.cfg:

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

**Uso pratico:** se si hanno chiavi già installate sullo scope ma se ne è perso il significato, validate.py permette di identificare esattamente quali opzioni abilitano.

---

## Struttura flags e mask

### flags

Il byte `flags` seleziona la "pagina" del registro opzioni. I bit rilevanti sono:

| Bit | Valore | Effetto |
|---|---|---|
| 0 | 0x01 | Pagina 1 (secondo gruppo di 32 opzioni) |
| 1 | 0x02 | Pagina 2 |
| 6 | 0x40 | Swap dei byte b0/b1 dell'iid durante la codifica |

Il "page index" usato per la ricerca in options.cfg è `flags & 0x43`.

Nella maggior parte delle opzioni comuni flags vale `00` o `01`.

### mask

Il campo `mask` è un intero a 32 bit dove ogni bit corrisponde a una specifica opzione nella pagina selezionata da `flags`. Ogni bit abilitato (=1) attiva l'opzione corrispondente.

Esempio: `mask = 0x00000009` abilita il bit 0 e il bit 3 contemporaneamente.

---

## Formato della chiave generata

Le chiavi hanno sempre il formato:

```
XXXX-XXXX-XXXX-XXXX
```

16 caratteri esadecimali maiuscoli suddivisi in 4 gruppi da 4 separati da trattino.

Internamente sono 8 byte cifrati con Blowfish ECB che codificano:
- 3 byte: iid (ScopeID)
- 1 byte: flags
- 4 byte: mask

---

## Architettura interna

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
    lec/crypto.py       DecryptFile()  [Blowfish ECB, blocchi da 8 byte]
```

### lec/crypto.py

Implementa la cifratura Blowfish ECB su blocchi da 8 byte. La chiave Blowfish è hardcoded nel sorgente (16 byte, offuscata con XOR). La funzione `revd()` inverte l'ordine dei byte nei due DWORD prima e dopo ogni operazione di cifratura (gestione endianness).

### lec/key.py

- `encode(iid, flags, mask)`: costruisce il plaintext `[iid(3B) | flags(1B) | mask(4B)]` in big-endian, lo cifra con Blowfish, restituisce il ciphertext come stringa `XXXX-XXXX-XXXX-XXXX`.
- `decode(ok)`: rimuove i trattini dalla chiave, decifra, restituisce `(iid, flags, mask)`.

### lec/db.py

Legge `options.cfg` decifrandolo blocco per blocco (8 byte alla volta). Il formato decifrato è un flusso binario con record tipizzati:

| Tipo ID | Tipo dato | Dimensione |
|---|---|---|
| `0x02` | Short (uint16) | 2 byte |
| `0x03` | Int (uint32) | 4 byte |
| `0x08` | String (UTF-16LE) | 4 byte lunghezza + N byte |
| `0x00` | Fine stream | — |

Le strutture principali nel database sono: categorie, componenti, mappature, opzioni, flag abilitazione.

---

## Note per modelli specifici

### DDA260 / DDA120 / WP9xx (vxfusion 9.3.0)

- Lo scope **non gira su Windows**: usa VxWorks, quindi non è possibile accedere direttamente al filesystem per copiare `options.cfg`.
- Il ScopeID si trova in **Utility > Utility Setup > Options**.
- Il firmware vxfusion si chiama semplicemente `vxfusion` (immagine binaria VxWorks).
- Il suffisso del ScopeID (es. `-DE`) è specifico del modello ma non influisce sulla generazione delle chiavi.
- Confermato funzionante: DDA-120 con firmware 9.3.0 (fonte: forum EEVblog + fetaudio.com).

### WaveRunner Xi/MXi/6000 (X-Stream < 8.x.x)

- Gira su Windows XP embedded.
- `options.cfg` si trova in `C:\Program Files\Lecroy\`.
- Accessibile via USB dopo aver collegato tastiera e mouse.

---

## Problemi comuni

### `ImportError: No module named Crypto`

PyCrypto non è installato o non viene trovato.

```bat
pip install pycrypto
:: oppure, se il precedente fallisce su Windows 10/11:
pip install pycryptodome
```

### `ValueError: invalid literal for int() with base 16`

Il ScopeID passato a gen.py contiene caratteri non esadecimali. Assicurarsi di usare solo i 6 caratteri prima del trattino (es. `2F0DAB` invece di `2F0DAB-DE`).

### `list.py` non produce output / errore sul file

Il file `options.cfg` è di una versione 8.x o superiore, incompatibile. Usare un `options.cfg` da firmware 7.9.x.x o precedente.

### La chiave generata non viene accettata dallo scope

- Verificare di usare il ScopeID corretto dello scope destinatario (non quello di un altro strumento).
- Verificare che flags e mask corrispondano a opzioni reali presenti nel database.
- Verificare la compatibilità del firmware.

### `IOError` o errore di apertura file

Verificare che il percorso di `options.cfg` sia corretto e che il file non sia aperto da altri processi.
