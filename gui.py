#!/usr/bin/env python3
# educational use only
"""
LeCroy License Key Generator — GUI
Requires: pycryptodome (pip install pycryptodome)
"""

OPTS_STR = """[
  { "code": "00-00000001", "key": "WP01", "description": "Basic Function Package" },
  { "code": "00-00000002", "key": "WP02", "description": "Basic FFT Package" },
  { "code": "00-00000004", "key": "WP03", "description": "Histogram/Trend Package" },
  { "code": "00-00000008", "key": "DDM",  "description": "Disk Drive Measurements" },
  { "code": "00-00000010", "key": "CKIO", "description": "9310 External clock + Trig. Out" },
  { "code": "00-00000020", "key": "PRML", "description": "PRML (disk drive) Measurements" },
  { "code": "00-00000040", "key": "ORM",  "description": "CD-ROM Measurements" },
  { "code": "00-00000080", "key": "DDFA", "description": "Disk Drive Failure Analysis" },
  { "code": "00-00000100", "key": "MATE", "description": "MATE remote control" },
  { "code": "00-00000200", "key": "MC01", "description": "Memory Card Software" },
  { "code": "00-00000400", "key": "PMSK", "description": "PolyMask" },
  { "code": "00-00000800", "key": "AORM", "description": "Advanced Optical Recording" },
  { "code": "00-00001000", "key": "DFP",  "description": "Digital Filter Package" },
  { "code": "00-00002000", "key": "ATP",  "description": "Advanced Trigger Package" },
  { "code": "00-00004000", "key": "ENET", "description": "Ethernet testing" },
  { "code": "00-00008000", "key": "BETA", "description": "New for customers to try" },
  { "code": "00-00010000", "key": "DEVP", "description": "Parameters under development" },
  { "code": "00-00020000", "key": "CU01", "description": "Telecom present" },
  { "code": "00-00040000", "key": "MT01", "description": "Telecom option 01" },
  { "code": "00-00080000", "key": "MT02", "description": "Telecom option 02" },
  { "code": "00-00100000", "key": "MT03", "description": "Telecom option 03" },
  { "code": "00-00200000", "key": "DDNA", "description": "Disk Drive Noise Analysis" },
  { "code": "00-00400000", "key": "JTA",  "description": "Jitter and Timing Analysis" },
  { "code": "00-00800000", "key": "CCTM", "description": "CCTM needs JTA" },
  { "code": "00-01000000", "key": "PMT",  "description": "Power Measurement Tools" },
  { "code": "00-02000000", "key": "DDA",  "description": "Disk Drive Analyzer" },
  { "code": "00-04000000", "key": "DMOD", "description": "Demodulation Tools" },
  { "code": "00-08000000", "key": "EATN", "description": "Eaton option" },
  { "code": "00-10000000", "key": "EMM",  "description": "Extended Math and Measure" },
  { "code": "00-20000000", "key": "WAVA", "description": "Wave Analyzer" },
  { "code": "00-40000000", "key": "HDS",  "description": "Hard Disk" },
  { "code": "00-80000000", "key": "JPRO", "description": "JitterPro" },
  { "code": "01-00000001", "key": "WPM",  "description": "WavePro M" },
  { "code": "01-00000002", "key": "WPL",  "description": "WavePro L" },
  { "code": "01-00000004", "key": "WPVL", "description": "WavePro VL" },
  { "code": "01-00000008", "key": "WPXL", "description": "WavePro XL" },
  { "code": "01-00000010", "key": "WPDD", "description": "WavePro DDA" },
  { "code": "01-00000020", "key": "JA",   "description": "Jitter Analyzer" },
  { "code": "01-00000040", "key": "SMAP", "description": "Surface Map" }
]"""


import json
import os
import sys
import tkinter as tk
import traceback
from io import StringIO
from itertools import count
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lec import db
from lec import key as lec_key

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OPTS_PATH = os.path.join(_HERE, "default_opts.json")

DEFAULT_OPTS = StringIO(OPTS_STR)

CHECK_ON = "☑"
CHECK_OFF = "☐"

# ── Palette ────────────────────────────────────────────────────────────────────
ROW_ODD = "#eef2f7"
ROW_EVEN = "#ffffff"
ACCENT = "#1a5276"
MONO_FONT = ("Courier", 10)


class LeCroyGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("LeCroy License Key Generator")
        self.root.geometry("1000x780")
        self.root.minsize(820, 620)

        self.options_data: list[dict] = []  # all parsed options
        self._status_var = tk.StringVar()
        self.source_var = tk.StringVar(value="default")
        self.options_count = 0
        self._setup_style()
        self._build_ui()
        self._load_default_options()  # carica subito le opzioni predefinite

    # ── Style ──────────────────────────────────────────────────────────────────

    def _setup_style(self):
        style = ttk.Style(self.root)
        for theme in ("clam", "alt", "default"):
            if theme in style.theme_names():
                style.theme_use(theme)
                break

        style.configure("Treeview", rowheight=26, font=("TkDefaultFont", 9))
        style.configure(
            "Treeview.Heading", font=("TkDefaultFont", 9, "bold"), relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", "#2980b9")],
            foreground=[("selected", "#ffffff")],
        )
        style.configure("Accent.TButton", font=("TkDefaultFont", 9, "bold"))

    # ── Main layout ────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=8)
        outer.pack(fill=tk.BOTH, expand=True)

        nb = ttk.Notebook(outer)
        nb.pack(fill=tk.BOTH, expand=True)

        gen_tab = ttk.Frame(nb, padding=6)
        nb.add(gen_tab, text="  Genera Chiavi  ")
        self._build_gen_tab(gen_tab)

        val_tab = ttk.Frame(nb, padding=6)
        nb.add(val_tab, text="  Valida Chiave  ")
        self._build_val_tab(val_tab)

        # Status bar
        sb = ttk.Label(
            self.root,
            textvariable=self._status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(8, 3),
        )
        sb.pack(fill=tk.X, side=tk.BOTTOM)

    # ── Tab 1 — Generator ──────────────────────────────────────────────────────

    def _build_gen_tab(self, parent):
        # Config row
        cfg = ttk.LabelFrame(parent, text=" Configurazione ", padding=10)
        cfg.pack(fill=tk.X, pady=(0, 6))

        # Row 0 — ScopeID + source selector
        ttk.Label(cfg, text="ScopeID (6 hex):").grid(row=0, column=0, sticky=tk.W)
        self.scope_var = tk.StringVar()
        ttk.Entry(cfg, textvariable=self.scope_var, width=10, font=MONO_FONT).grid(
            row=0, column=1, sticky=tk.W, padx=(4, 28)
        )

        ttk.Label(cfg, text="Sorgente opzioni:").grid(row=0, column=2, sticky=tk.W)
        ttk.Radiobutton(
            cfg,
            text="Predefinite (" + str(self.options_count) + " opzioni)",
            variable=self.source_var,
            value="default",
            command=self._on_source_change,
        ).grid(row=0, column=3, sticky=tk.W, padx=(6, 4))
        ttk.Radiobutton(
            cfg,
            text="Da JSON esterno",
            variable=self.source_var,
            value="cfg",
            command=self._on_source_change,
        ).grid(row=0, column=4, sticky=tk.W, padx=(0, 8))

        # Row 1 — cfg path (visible only when source == "cfg")
        self._cfg_row_frame = ttk.Frame(cfg)
        self._cfg_row_frame.grid(
            row=1, column=0, columnspan=6, sticky=tk.EW, pady=(6, 0)
        )

        ttk.Label(self._cfg_row_frame, text="File:").pack(side=tk.LEFT)
        self.cfg_path_var = tk.StringVar()
        self._cfg_entry = ttk.Entry(
            self._cfg_row_frame,
            textvariable=self.cfg_path_var,
            state="readonly",
            width=55,
        )
        self._cfg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        self._sfoglia_btn = ttk.Button(
            self._cfg_row_frame, text="Sfoglia…", command=self._browse_cfg
        )
        self._sfoglia_btn.pack(side=tk.LEFT)

        cfg.columnconfigure(5, weight=1)

        # Initially hide the cfg row (default source selected)
        self._cfg_row_frame.grid_remove()

        # Vertical split: options on top, results on bottom
        pane = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        pane.pack(fill=tk.BOTH, expand=True)

        opts_lf = ttk.LabelFrame(pane, text=" Opzioni disponibili ", padding=6)
        pane.add(opts_lf, weight=3)
        self._build_opts_pane(opts_lf)

        res_lf = ttk.LabelFrame(pane, text=" Risultati ", padding=6)
        pane.add(res_lf, weight=2)
        self._build_res_pane(res_lf)

    def _build_opts_pane(self, parent):
        # Toolbar
        tb = ttk.Frame(parent)
        tb.pack(fill=tk.X, pady=(0, 4))

        ttk.Button(tb, text="Seleziona tutto", command=self._select_all).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(tb, text="Deseleziona tutto", command=self._deselect_all).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Separator(tb, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Button(
            tb,
            text="▶  Genera selezionate",
            style="Accent.TButton",
            command=self._gen_selected,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(tb, text="▶▶  Genera tutte", command=self._gen_all).pack(
            side=tk.LEFT, padx=2
        )

        # Table
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        cols = ("sel", "code", "name", "description")
        self.opts_tree = ttk.Treeview(
            frame, columns=cols, show="headings", selectmode="browse"
        )
        self.opts_tree.heading("sel", text="✓", anchor=tk.CENTER)
        self.opts_tree.heading("code", text="Codice")
        self.opts_tree.heading("name", text="Nome")
        self.opts_tree.heading("description", text="Descrizione")

        self.opts_tree.column(
            "sel", width=38, minwidth=38, stretch=False, anchor=tk.CENTER
        )
        self.opts_tree.column("code", width=130, minwidth=110, stretch=False)
        self.opts_tree.column("name", width=170, minwidth=130, stretch=False)
        self.opts_tree.column("description", width=500)

        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.opts_tree.yview)
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.opts_tree.xview)
        self.opts_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.opts_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.opts_tree.tag_configure("odd", background=ROW_ODD)
        self.opts_tree.tag_configure("even", background=ROW_EVEN)

        self.opts_tree.bind("<Button-1>", self._on_opts_click)

    def _build_res_pane(self, parent):
        # Toolbar
        tb = ttk.Frame(parent)
        tb.pack(fill=tk.X, pady=(0, 4))

        ttk.Button(tb, text="Copia tutto", command=self._copy_all).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(tb, text="Esporta CSV", command=lambda: self._export("csv")).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(tb, text="Esporta TXT", command=lambda: self._export("txt")).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(tb, text="Pulisci", command=self._clear_results).pack(
            side=tk.RIGHT, padx=2
        )

        # Table
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        cols = ("key", "name", "description")
        self.res_tree = ttk.Treeview(
            frame, columns=cols, show="headings", selectmode="browse"
        )
        self.res_tree.heading("key", text="Chiave di licenza")
        self.res_tree.heading("name", text="Nome")
        self.res_tree.heading("description", text="Descrizione")

        self.res_tree.column("key", width=205, minwidth=180, stretch=False)
        self.res_tree.column("name", width=170, minwidth=130, stretch=False)
        self.res_tree.column("description", width=500)

        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.res_tree.yview)
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.res_tree.xview)
        self.res_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.res_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.res_tree.tag_configure("odd", background=ROW_ODD)
        self.res_tree.tag_configure("even", background=ROW_EVEN)

        ttk.Label(
            parent,
            text="Doppio click su una riga per copiare la chiave.",
            foreground="gray",
        ).pack(anchor=tk.W, pady=(3, 0))

        self.res_tree.bind("<Double-Button-1>", self._copy_single_key)

    # ── Tab 2 — Validate ───────────────────────────────────────────────────────

    def _build_val_tab(self, parent):
        # Input row
        inp = ttk.LabelFrame(parent, text=" Chiave da decodificare ", padding=10)
        inp.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(inp, text="Chiave:").grid(row=0, column=0, sticky=tk.W)
        self.val_key_var = tk.StringVar()
        ttk.Entry(inp, textvariable=self.val_key_var, width=22, font=MONO_FONT).grid(
            row=0, column=1, padx=6
        )
        ttk.Button(
            inp, text="Decodifica", style="Accent.TButton", command=self._validate_key
        ).grid(row=0, column=2, padx=4)
        ttk.Label(
            inp, text="(usa il JSON caricato nel tab Genera)", foreground="gray"
        ).grid(row=0, column=3, padx=14)

        # Decoded fields
        info = ttk.LabelFrame(parent, text=" Informazioni chiave ", padding=10)
        info.pack(fill=tk.X, pady=(0, 8))

        self.val_info: dict[str, tk.StringVar] = {}
        for col, (label, key_name) in enumerate(
            [("ScopeID", "scope"), ("Flags", "flags"), ("Mask", "mask")]
        ):
            ttk.Label(info, text=label + ":").grid(
                row=0, column=col * 2, sticky=tk.W, padx=(0 if col == 0 else 30, 6)
            )
            v = tk.StringVar(value="—")
            self.val_info[key_name] = v
            ttk.Label(info, textvariable=v, font=MONO_FONT, foreground=ACCENT).grid(
                row=0, column=col * 2 + 1, sticky=tk.W
            )

        # Enabled options table
        res_lf = ttk.LabelFrame(
            parent, text=" Opzioni abilitate da questa chiave ", padding=6
        )
        res_lf.pack(fill=tk.BOTH, expand=True)

        frame = ttk.Frame(res_lf)
        frame.pack(fill=tk.BOTH, expand=True)

        cols = ("code", "name", "description")
        self.val_tree = ttk.Treeview(frame, columns=cols, show="headings")
        self.val_tree.heading("code", text="Codice")
        self.val_tree.heading("name", text="Nome")
        self.val_tree.heading("description", text="Descrizione")

        self.val_tree.column("code", width=130, minwidth=110, stretch=False)
        self.val_tree.column("name", width=170, minwidth=130, stretch=False)
        self.val_tree.column("description", width=500)

        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.val_tree.yview)
        self.val_tree.configure(yscrollcommand=vsb.set)
        self.val_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.val_tree.tag_configure("odd", background=ROW_ODD)
        self.val_tree.tag_configure("even", background=ROW_EVEN)

    # ── Logic — load options ───────────────────────────────────────────────────

    def _on_source_change(self):
        if self.source_var.get() == "default":
            self._cfg_row_frame.grid_remove()
            self._load_default_options()
        else:
            self._cfg_row_frame.grid()
            # Se c'è già un file selezionato, ricaricalo; altrimenti aspetta Sfoglia
            path = self.cfg_path_var.get()
            if path:
                self._load_options(path)
            else:
                self.options_data = []
                self._populate_opts_tree()
                self._status("Seleziona un file JSON con il pulsante Sfoglia…")

    def _load_default_options(self):
        if not os.path.isfile(DEFAULT_OPTS_PATH):
            self._status("File default_opts.json non trovato accanto a gui.py.")
            return
        try:
            with open(DEFAULT_OPTS_PATH, encoding="utf-8") as f:
                raw = json.load(f)
            self.options_data = []
            for entry in raw:
                code = entry["code"]  # e.g. "00-00000001"
                flags_hex, mask_hex = code.split("-")
                self.options_data.append(
                    {
                        "code": code,
                        "name": entry["key"],
                        "description": entry["description"],
                        "flags": int(flags_hex, 16),
                        "mask": int(mask_hex, 16),
                        "checked": False,
                        "tree_id": None,
                    }
                )
            self._populate_opts_tree()
            self._status(
                f"Caricate {len(self.options_data)} opzioni predefinite da default_opts.json"
            )
        except Exception:
            messagebox.showerror("Errore default_opts.json", traceback.format_exc())
            self._status("Errore nel caricamento delle opzioni predefinite.")

    def _browse_cfg(self):
        path = filedialog.askopenfilename(
            title="Seleziona file JSON opzioni",
            filetypes=[("JSON files", "*.json"), ("Tutti i file", "*.*")],
        )
        if path:
            self.cfg_path_var.set(path)
            self._load_options(path)

    def _load_options(self, path: str):
        self._status(f"Caricamento {os.path.basename(path)} …")
        self.root.update_idletasks()
        try:
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            self.options_data = []
            for entry in raw:
                code = entry["code"]
                flags_hex, mask_hex = code.split("-")
                self.options_data.append(
                    {
                        "code": code,
                        "name": entry["key"],
                        "description": entry["description"],
                        "flags": int(flags_hex, 16),
                        "mask": int(mask_hex, 16),
                        "checked": False,
                        "tree_id": None,
                    }
                )
            self._populate_opts_tree()
            self._status(
                f"Caricate {len(self.options_data)} opzioni da {os.path.basename(path)}"
            )
        except Exception:
            messagebox.showerror("Errore caricamento JSON", traceback.format_exc())
            self._status("Errore nel caricamento del file.")

    def _populate_opts_tree(self):
        for item in self.opts_tree.get_children():
            self.opts_tree.delete(item)
        for i, opt in enumerate(self.options_data):
            tag = "odd" if i % 2 else "even"
            iid = self.opts_tree.insert(
                "",
                tk.END,
                values=(CHECK_OFF, opt["code"], opt["name"], opt["description"]),
                tags=(tag,),
            )
            opt["tree_id"] = iid

    # ── Logic — checkbox toggle ────────────────────────────────────────────────

    def _on_opts_click(self, event):
        region = self.opts_tree.identify_region(event.x, event.y)
        col = self.opts_tree.identify_column(event.x)
        row = self.opts_tree.identify_row(event.y)
        if region == "cell" and col == "#1" and row:
            self._toggle_item(row)

    def _toggle_item(self, iid: str):
        for opt in self.options_data:
            if opt["tree_id"] == iid:
                opt["checked"] = not opt["checked"]
                vals = list(self.opts_tree.item(iid, "values"))
                vals[0] = CHECK_ON if opt["checked"] else CHECK_OFF
                self.opts_tree.item(iid, values=vals)
                break

    def _select_all(self):
        for opt in self.options_data:
            opt["checked"] = True
            if opt["tree_id"]:
                vals = list(self.opts_tree.item(opt["tree_id"], "values"))
                vals[0] = CHECK_ON
                self.opts_tree.item(opt["tree_id"], values=vals)

    def _deselect_all(self):
        for opt in self.options_data:
            opt["checked"] = False
            if opt["tree_id"]:
                vals = list(self.opts_tree.item(opt["tree_id"], "values"))
                vals[0] = CHECK_OFF
                self.opts_tree.item(opt["tree_id"], values=vals)

    # ── Logic — generate ───────────────────────────────────────────────────────

    def _get_scope_iid(self) -> int | None:
        raw = self.scope_var.get().strip().upper()
        if not raw:
            messagebox.showerror(
                "ScopeID mancante", "Inserisci il ScopeID (6 caratteri esadecimali)."
            )
            return None
        if len(raw) != 6 or not all(c in "0123456789ABCDEF" for c in raw):
            messagebox.showerror(
                "ScopeID non valido",
                "Il ScopeID deve essere esattamente 6 caratteri esadecimali.",
            )
            return None
        return int(raw, 16)

    def _gen_selected(self):
        iid = self._get_scope_iid()
        if iid is None:
            return
        selected = [o for o in self.options_data if o["checked"]]
        if not selected:
            messagebox.showwarning(
                "Nessuna selezione", "Seleziona almeno un'opzione prima di generare."
            )
            return
        self._do_generate(iid, selected)

    def _gen_all(self):
        iid = self._get_scope_iid()
        if iid is None:
            return
        if not self.options_data:
            messagebox.showwarning(
                "Nessun dato",
                "Nessuna opzione disponibile. Verifica la sorgente selezionata.",
            )
            return
        self._do_generate(iid, self.options_data)

    def _do_generate(self, iid: int, opts: list[dict]):
        self._clear_results()
        errors = []
        for i, opt in enumerate(opts):
            try:
                k = lec_key.encode(iid, opt["flags"], opt["mask"])
                tag = "odd" if i % 2 else "even"
                self.res_tree.insert(
                    "", tk.END, values=(k, opt["name"], opt["description"]), tags=(tag,)
                )
            except Exception as exc:
                errors.append(f"{opt['name']}: {exc}")

        n = len(opts) - len(errors)
        self._status(
            f"Generate {n} chiavi" + (f" — {len(errors)} errori" if errors else "")
        )
        if errors:
            messagebox.showwarning("Attenzione", "\n".join(errors))

    # ── Logic — results actions ────────────────────────────────────────────────

    def _clear_results(self):
        for item in self.res_tree.get_children():
            self.res_tree.delete(item)

    def _copy_single_key(self, _event):
        sel = self.res_tree.selection()
        if sel:
            k = self.res_tree.item(sel[0], "values")[0]
            self.root.clipboard_clear()
            self.root.clipboard_append(k)
            self._status(f"Copiata: {k}")

    def _copy_all(self):
        items = self.res_tree.get_children()
        if not items:
            messagebox.showwarning("Vuoto", "Nessun risultato da copiare.")
            return
        lines = ["\t".join(self.res_tree.item(i, "values")) for i in items]
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(lines))
        self._status(f"{len(lines)} righe copiate negli appunti.")

    def _export(self, fmt: str):
        items = self.res_tree.get_children()
        if not items:
            messagebox.showwarning("Vuoto", "Nessun risultato da esportare.")
            return
        ext = ".csv" if fmt == "csv" else ".txt"
        ftype = [("CSV", "*.csv")] if fmt == "csv" else [("Testo", "*.txt")]
        path = filedialog.asksaveasfilename(
            defaultextension=ext, filetypes=ftype, initialfile="chiavi_lecroy"
        )
        if not path:
            return
        sep = "," if fmt == "csv" else "\t"
        with open(path, "w", encoding="utf-8") as f:
            if fmt == "csv":
                f.write("Chiave,Nome,Descrizione\n")
            for item in items:
                f.write(sep.join(self.res_tree.item(item, "values")) + "\n")
        self._status(f"Esportato in: {path}")

    # ── Logic — validate ───────────────────────────────────────────────────────

    def _validate_key(self):
        raw = self.val_key_var.get().strip()
        if not raw:
            messagebox.showerror("Errore", "Inserisci una chiave da decodificare.")
            return

        # Reset
        for item in self.val_tree.get_children():
            self.val_tree.delete(item)
        for v in self.val_info.values():
            v.set("—")

        try:
            iid, flags, mask = lec_key.decode(raw)
        except Exception as exc:
            messagebox.showerror("Chiave non valida", str(exc))
            return

        self.val_info["scope"].set(f"{iid:06X}")
        self.val_info["flags"].set(f"{flags:02x}")
        self.val_info["mask"].set(f"{mask:08x}")

        if self.options_data:
            matched = [
                o
                for o in self.options_data
                if o["flags"] == flags and (mask & o["mask"])
            ]
            for i, opt in enumerate(matched):
                tag = "odd" if i % 2 else "even"
                self.val_tree.insert(
                    "",
                    tk.END,
                    values=(opt["code"], opt["name"], opt["description"]),
                    tags=(tag,),
                )
            self._status(f"Chiave valida — {len(matched)} opzione/i riconosciute")
        else:
            self._status(
                "Chiave valida. Carica options.cfg nel tab Genera "
                "per vedere le opzioni abilitate."
            )

    # ── Utility ────────────────────────────────────────────────────────────────

    def _status(self, msg: str):
        self._status_var.set(f"  {msg}")


# ── Entry point ────────────────────────────────────────────────────────────────


def main():
    root = tk.Tk()
    LeCroyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
