# RELEASE CHECKLIST — pdfx-hermes 0.3.0

Date: 2026-08-25 · Artifact: `dist/pdfx-hermes-0.3.0.tar.gz`

## Package contents

- [x] `VERSION` = `0.3.0` (matches `pdfx.py` `__version__` and skill frontmatter)
- [x] `LICENSE` (MIT)
- [x] `NOTICE`
- [x] `ATTRIBUTION.md`
- [x] `DEPENDENCIES.md`
- [x] `CHANGELOG.md`
- [x] `README.md`
- [x] `MANIFEST` (matches tar file list)
- [x] `INSTALL.sh` executable
- [x] `pdfx.py`, `pdfx-batch-fraktur.sh`, `pdfx_metrics.py` executable
- [x] `skill/SKILL.md` (name: `pdfx`)
- [x] `skill/references/CONTROL_GATES.md`
- [x] `skill/references/INFOGRAPHICS.md`
- [x] `skill/references/fraktur-templates/INDEX.md` (**no** JPGs)
- [x] `skill/scripts/` batch + metrics copies
- [x] No `__pycache__`, `.venv`, `*.jpg`/`*.jpeg`, model weights, secrets

## INSTALL.sh behavior

- [x] `--dry-run` / `-n` reports only
- [x] `--skill` targets `~/.hermes/skills/productivity/pdfx`
- [x] `--version` prints package version
- [x] VERSION ↔ `pdfx.py` consistency check
- [x] Install root `~/.local/share/pdfx`
- [x] Symlinks: `pdfx`, `pdfx-batch-fraktur`, `pdfx-metrics` → share dir
- [x] Dep checks: python3, tesseract, ocrmypdf, pdftoppm, pymupdf, frk
- [x] Prints mode-header smoke one-liner after install/dry-run

## Verification run (this ship)

- [x] `./INSTALL.sh --dry-run` OK
- [x] `./INSTALL.sh --dry-run --skill` OK
- [x] `tar tzf` file list == `MANIFEST`
- [x] `rg '/home/mrxmoex' skill pdfx.py` → **zero** hits
- [x] Whole package path scan clean
- [x] Functional: `python3 pdfx.py PART2.pdf --inspect` on  
  `…/AQKAAAAIAAJ/parts/AQKAAAAIAAJ_pp187-366.pdf`  
  → `kind=digital`, `text_quality.label=garbled`, `recommend=ocr-fraktur-or-scan` (Google trap OK)
- [x] `pdfx --version` → `pdfx 0.3.0`
- [x] Portable Python: uses `sys.executable` when `$PDFX_HOME/.venv` absent

## Legal / redistribution

- [x] MIT LICENSE present
- [x] NOTICE + ATTRIBUTION name third-party CLIs (not bundled)
- [x] No book PDF corpus in tarball
- [x] No Fraktur specimen binaries (INDEX only)

## Human follow-ups (not blocking 0.3.0 tarball)

- [ ] Optional: real `./INSTALL.sh --skill` on a clean fellow machine
- [ ] optional-skills PR + frontmatter tests in hermes-agent
- [ ] macOS Homebrew smoke
- [ ] Fellows place own `frk.traineddata` + optional template JPGs

## Artifacts

| Path | Notes |
|------|-------|
| `dist/pdfx-hermes-0.3.0.tar.gz` | **Ship this** |
| `dist/pdfx-hermes/` | Unpacked tree (source of tar) |
| `dist/pdfx-hermes-0.2.2.tar.gz` | Prior; retained |
| `dist/COMPLETE_PACKAGE.md` | CEO one-pager |
