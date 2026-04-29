# EngineeringPapyr — Native Desktop Edition

A native Windows desktop build of [EngineeringPaper.xyz](https://engineeringpaper.xyz) using **PyWebView** + **native Python** instead of Pyodide/WebAssembly. Calculations run via native CPython with SymPy — faster startup, faster computation (3-5x faster), and a smaller footprint (~330 MB to ~120 MB).

---

## What Is EngineeringPaper.xyz?

A web app for engineering calculations with:
- Automatic unit conversion and dimensional analysis
- Plotting and data tables
- Systems of equations
- Documentation cells with rich text

---

## What's Different in EngineeringPapyr

EngineeringPapyr replaces that entire stack:

| Aspect | Original Standalone | EngineeringPapyr |
|--------|-------------------|------------------|
| Window | System browser (Chrome/Firefox) | Native window (Edge WebView2) |
| Python runtime | Pyodide (WASM, ~92MB) | Native CPython |
| Computation engine | SymPy via Pyodide | SymPy via native Python |
| SymPy startup | ~10-15s (WASM load + init) | ~2-5s (native import) |
| Frontend | Svelte + KaTeX (same) | Svelte + KaTeX (same) |
| Frontend assets | ~165MB (includes pyodide/) | ~73MB (no pyodide/) |
| Code completion | Jedi via Pyodide Worker | Jedi via native Python |
| Packaging | Node.js exe via pkg | Python exe via PyInstaller |

All features are preserved: math cells, documentation cells, system solve cells, EVA/RSS analysis cells, code cells, plot cells, fluid cells, data tables, DOCX export (pandoc-wasm), and PDF export (print dialog).

---

## Additional Features 

Additional features maintained from [EngineeringPaperStandalone](https://github.com/animagr/EngineeringPaperStandalone)

### Annotation Column for Math Cells

Math cells have an optional annotation column to the right for units descriptions, notes, or labels (e.g., "velocity", "kg/m^3").

- Click a math cell to reveal the annotation input
- Saves automatically and persists with the sheet
- Included in Markdown/DOCX export as `*[annotation]*`

### Extreme Value Analysis (EVA) Cell

Finds worst-case min/max of an output expression by evaluating all 2^n combinations of input parameter bounds, plus sensitivity analysis.

1. Define parameters on the sheet (e.g., `V = 10 [V]`, `R = 1000 [Ω]`, `I = V / R =`)
2. Insert an EVA cell
3. Set the **Query** field to the expression to evaluate (e.g., `I=`)
4. Add parameter rows with **Parameter** name, **Min**, and **Max** values

### Root Sum Square (RSS) Analysis Cell

Statistical tolerance analysis cell that computes the RSS error envelope. Unlike EVA's worst-case (all tolerances at extremes simultaneously), RSS assumes parameter variations are independent and combines them as root-sum-of-squares.

1. Define parameters on the sheet
2. Insert an RSS cell
3. Set the **Query** field to the expression to evaluate
4. Add parameter rows with **Parameter** name, **Min**, **Nominal**, and **Max** values

---

## How to Build and Run

### Prerequisites

- [Node.js](https://nodejs.org/)
- [Git for Windows](https://gitforwindows.org/) (includes Git Bash, required for building npm dependencies)
- Python 3.10 to 3.12 with pip (best compatibility with scientific packages)
- Edge WebView2 runtime (pre-installed on Windows 11)

### 1. Install Python dependencies

```bash
cd C:\Claude\EngPaper\EngineeringPapyr
py -3.10 -m pip install -r requirements.txt
```

### 2. Build the frontend

**Windows users:** Run `npm install` from **Git Bash**, not PowerShell or cmd. Some dependencies require bash to build.

```bash
cd C:\Claude\EngPaper\EngineeringPapyr\frontend
npm install
npm run build:native
```

Output goes to `frontend/public/`.

### 3. Run the app

```bash
cd C:\Claude\EngPaper\EngineeringPapyr
py -3.10 python/main.py
```

### 4. Package as .exe

```bash
cd C:\Claude\EngPaper\EngineeringPapyr
py -3.10 build.py
```

Output: `dist/EngineeringPapyr.exe`

---

## Dev Workflow

For iterating on frontend changes:

- **Terminal 1:** `cd frontend && npm run dev:native` (watches + rebuilds on save)
- **Terminal 2:** `cd .. && py -3.10 python/main.py` (launch app, restart manually after frontend rebuild)

---

## Architecture

```
PyWebView window (Edge WebView2)
  |
  |-- Loads Svelte frontend from local files (frontend/public/)
  |-- JS calls window.pywebview.api.solve_sheet(json)
  |
  v
Native Python (python/api.py)
  |-- solve_sheet()  ->  dimensional_analysis.py (SymPy)
  |-- get_code_context()  ->  jedi_code_analysis.py (Jedi)
  |-- LRU cache (100 entries, replaces QuickLRU in JS)
```

The JS-Python boundary is 100% JSON strings in both directions. PyWebView runs API methods in background threads, so long computations don't freeze the UI.

### Key files

| File | Purpose |
|------|---------|
| `python/main.py` | PyWebView entry point, creates window |
| `python/api.py` | JS API bridge (solve_sheet, get_code_context) |
| `python/dimensional_analysis.py` | Core computation engine (SymPy, ~4800 lines) |
| `python/jedi_code_analysis.py` | Code cell autocomplete via Jedi |
| `frontend/src/App.svelte` | Main app (calls `window.pywebview.api` instead of Web Workers) |
| `frontend/src/jediWrapper.ts` | Jedi bridge (PyWebView API instead of Worker) |
| `frontend/rollup.config.js` | Build config (no pyodide/jedi worker entries) |
| `pyinstaller.spec` | PyInstaller packaging config |
| `build.py` | Build orchestrator (npm build + PyInstaller) |

---

## Troubleshooting

- **SymPy first import takes 2-5 seconds** — the app shows "Loading Python..." during this, normal behavior
- **CoolProp fails to install** — skip it initially (`pip install` the rest manually), only needed for fluid cells
- **`npm install` slow** — expected, the mathlive/plotly GitHub dependencies take time
- **Python 3.13/3.14** — may have issues with scientific packages; use 3.10-3.12 for best compatibility

---

## License

MIT license, same as original.

See the original [EngineeringPaper.xyz](https://github.com/mgreminger/EngineeringPaper.xyz) project for license information.
