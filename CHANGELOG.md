# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.5] - 2026-05-02

### Added

- Electronic Part Stress Analysis (EPSA) module (`python/part_stress.py`). Code cells can import `resistor()`, `capacitor()`, and `stress_report()` to check component stresses against derating rules (80% voltage, 60% power) with automatic SMD package selection.
- `PKG_RATINGS.csv` — SMD package ratings database for resistors (0201–2512) and capacitors (0201–2220).
- Standard capacitor voltage rating selection from MLCC series (4V–3kV).
- EPSA output as grouped CSV report: resistors (one row per part with voltage and power) and capacitors (one row per part with voltage), with units in headers (ohm, mA, V, mW, pF).

### Changed

- `build.py` now includes `PKG_RATINGS.csv` in the distribution `DATA_FILES`.

## [1.0.4] - 2026-05-01

### Changed

- Replaced PyInstaller full-app freeze with embedded Python 3.12 distribution. The build now ships a portable directory containing the Python 3.12 embeddable runtime with all pip dependencies pre-installed, plus a small launcher exe.
- Code cells in the packaged distribution now have full access to the embedded Python environment — any package installed into it is available for import.
- Build script (`build.py`) rewritten with 5-phase pipeline: frontend build, embedded Python setup, app file copy, launcher compilation, zip packaging.
- CSV data files (`RES0.1.csv`, `RES1.0.csv`, `CAP.csv`, `IND.csv`) are now properly included in the distribution (fixes pre-existing bug where `pyinstaller.spec` did not bundle them).

### Added

- `launcher.py` — minimal launcher script compiled into a ~6MB exe that starts the embedded Python.
- `pyinstaller_launcher.spec` — PyInstaller spec for the launcher only (replaces the full-app `pyinstaller.spec`).

### Removed

- `pyinstaller.spec` — replaced by `pyinstaller_launcher.spec`.
- `sys.frozen` / `_MEIPASS` code paths in `main.py`, `api.py`, and `standard_parts.py` (dead code with embedded Python approach).

## [1.0.3] - 2026-04-30

### Changed

- EVA (Extreme Value Analysis) now uses `lambdify` to evaluate all 2^n parameter combinations via fast numeric functions instead of repeated SymPy `evalf()` calls. Falls back to the original method if lambdify fails.
- RSS tolerance analysis delta evaluations now use `lambdify` for the same speedup. Nominal evaluation still uses the full SymPy path for proper unit/dimensional analysis results.
- Maximum parameters for EVA and RSS cells increased from 20 to 25.
- App header logo changed from SVG to PNG (`print_logo.png`).
- App header background color changed to pure black.

## [1.0.2] - 2026-04-30

### Fixed

- DOCX export failing due to browser caching stale dynamic import chunk (`docxExport-*.js` hash mismatch). Inlined the export logic to eliminate the separate code-split chunk.
- App logo not updating after change due to stale WebView2 browser cache. Added version-based cache-busting to logo image URLs.
- DOCX export failing with "pandoc not found" because `pypandoc.get_pandoc_path()` returns path without `.exe` extension on Windows.

## [1.0.1] - 2026-04-29

### Added

- Version number displayed in window title bar.
- `pypandoc_binary` dependency for native pandoc support.
- Code cell Python info tooltip now shows live Python version and all installed packages from the native environment.
- Users can import any `pip install`-ed package in code cells.
- Build script (`build.py`) now generates `installed_packages.json` at build time and bundles pandoc binary into the exe.

### Changed

- DOCX export now uses native pandoc via Python backend (`pypandoc`) instead of `pandoc-wasm` in the browser.
- DOCX export save dialog uses `showSaveFilePicker` API for proper file saving in PyWebView.
- Rebranded UI text and URLs from EngineeringPaper.xyz to EngineeringPapyr.
- GitHub link in side nav now points to `animagr/EngineeringPapyr`.
- Bug report and error messages now link to GitHub Issues instead of upstream email.
- Package name in `package.json` changed from `svelte-app` to `engineering-papyr`.
- Code cell package detection replaced with native Python introspection via `importlib.metadata`.

### Fixed

- DOCX export not working in PyWebView (anchor-click downloads don't trigger in WebView2).
- Pandoc not found in packaged exe (now bundled via PyInstaller and located at runtime).
- Code cell package list empty in packaged exe (`importlib.metadata` doesn't work when frozen; now reads static JSON).

### Removed

- Terms and conditions popup, footer banner, and side nav link.
- `pandoc-wasm` npm dependency (replaced by native pandoc via `pypandoc`).
- Upstream blog link from side nav.
- All `support@engineeringpaper.xyz` email references.
- `pyodide-info.json` and Pyodide package detection logic (`neededPyodidePackages`).
- Cloudflare Worker files (`_worker.ts`, `_worker.js`), routing (`_routes.json`), and worker tsconfig.
- Database init scripts and test sheet fixtures (`database/scripts/`).
- Duplicate Python files from `frontend/public/` (`dimensional_analysis.py`, `jedi_code_analysis.py`).
- Web-only files: `robots.txt`, `.well-known/assetlinks.json`, `iframe_test.html`, `Terms.svelte`.
- `@cloudflare/workers-types` and `wrangler` devDependencies.

## [1.0.0] - 2026-04-29

### Added

- Initial fork of [EngineeringPaper.xyz](https://engineeringpaper.xyz) as a native Windows desktop app.
- Native CPython backend via PyWebView replacing Pyodide/WASM for 3-5x faster computation.
- PyInstaller packaging to single `EngineeringPapyr.exe`.
- ExtremeValueCell (EVA) and RssCell (RSS tolerance analysis) cell types.
- Optional annotation column for math cells.
- Jedi-based code completion for code cells.
- LRU caching for Python computation results.

### Changed

- Replaced Pyodide web worker with `window.pywebview.api` calls for JS-Python communication.
- Replaced Cloudflare backend with local-only storage (IndexedDB via `idb-keyval`, file system).
- DOCX export routed through `pandoc-wasm`; PDF export through `window.print()`.

### Removed

- Server-dependent features (shareable links, example sheets, server-side export).
- Pyodide/WASM dependency.
- Cloudflare Pages Functions backend.
