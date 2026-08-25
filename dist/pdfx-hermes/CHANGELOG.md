# Changelog

## 0.3.0 — complete package (2026-08-25)

### CLI
- Machine-readable **MODE DETECTION HEADER** on every extract (stderr)
- `--inspect` adds `pdfx_version`, `dependencies`, `edge_flags`, `mode_effective_hint`, `plate_page_candidates`
- Edge cases: missing file/type, 0 pages, pages OOB, missing frk/ocrmypdf/pdftoppm, password PDF, large PDF without `--pages`, forced digital on garbled, image-as-digital
- `--plates-sidecar` writes plate candidate JSON next to `--out`
- Portable `PDFX_HOME` / tessdata discovery (no machine-local hardcoding)

### Package
- ATTRIBUTION, NOTICE, LICENSE (MIT wrapper), DEPENDENCIES, INFOGRAPHICS, CONTROL_GATES
- Fraktur template INDEX (specimens not shipped)
- INSTALL.sh --dry-run / --skill / version gate
- Hermes skill `pdfx` 0.3.0 + house `pdf-extract-ocr` 0.3.0

### Credits
- Primary: m (MrxHermesx)
- Co-author fleet: Hermes Agent (Nous Research) under human direction

HANGELOG — pdfx-hermes

## 0.3.0 — 2026-08-25

### Ship / packaging
- Public tarball `pdfx-hermes-0.3.0.tar.gz` with full legal + ops docs:
  `LICENSE`, `NOTICE`, `ATTRIBUTION.md`, `DEPENDENCIES.md`, `CHANGELOG.md`, `MANIFEST`
- `INSTALL.sh` polish: `--dry-run`, `--skill`, `--version`, VERSION↔`pdfx.py` consistency check,
  install to `~/.local/share/pdfx`, symlinks `pdfx` / `pdfx-batch-fraktur` / `pdfx-metrics`,
  optional skill → `~/.hermes/skills/productivity/pdfx`, dependency checks
  (python3, tesseract, ocrmypdf, pdftoppm, pymupdf, frk), mode-header smoke one-liner
- References in skill: `CONTROL_GATES.md`, `INFOGRAPHICS.md`, `fraktur-templates/INDEX.md`
  (**no** specimen JPGs)
- `pdfx --version` flag; package `VERSION` = `0.3.0`
- Path hygiene: no machine-local `/home/…` paths in portable CLI or skill

### Runtime (carried from 0.2.x gates)
- Inspect emits `plate_page_candidates` / `plate_page_candidate_count` (image+thin-text heuristic)
- Fraktur `--engine auto` → **ocrmypdf** (Gate B); QA → `--engine images`
- Inspect quality gate + auto refuses garbled Google digital layers
- Batch chunk default 20; craft metrics helper

## 0.2.2 — 2026-08-25

- Locked Fraktur default engine to ocrmypdf after Gate B bakeoff
- Portable skill + INSTALL dry-run package draft
- CONTROL_GATES.md A/B/C summary
- Fraktur templates INDEX (binaries house-only)

## 0.2.1 — 2026-08-24

- Fix `TESSDATA_PREFIX` (tessdata dir, not parent)
- Honor `--pages` on digital + OCR
- Fraktur / forced OCR uses `--force-ocr` or image path (not `--skip-text`)
- Inspect `text_quality` + `recommend`

## 0.2.0 — 2026-08-24

- Initial unified `pdfx` CLI (digital / scan / fraktur / marker / kurrent)
