# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-04-29

### Added

- Version number displayed in window title bar.
- `pypandoc_binary` dependency for native pandoc support.
- Code cell Python info tooltip now shows live Python version and all installed packages from the native environment.
- Users can import any `pip install`-ed package in code cells.

### Changed

- DOCX export now uses native pandoc via Python backend (`pypandoc`) instead of `pandoc-wasm` in the browser.
- Rebranded UI text and URLs from EngineeringPaper.xyz to EngineeringPapyr.
- GitHub link in side nav now points to `animagr/EngineeringPapyr`.
- Bug report and error messages now link to GitHub Issues instead of upstream email.
- Package name in `package.json` changed from `svelte-app` to `engineering-papyr`.
- Code cell package detection replaced with native Python introspection via `importlib.metadata`.

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

[unreleased]: https://github.com/animagr/EngineeringPapyr/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/animagr/EngineeringPapyr/releases/tag/v1.0.0
