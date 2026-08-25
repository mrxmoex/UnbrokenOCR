---
name: pdfx
description: "Extract PDFs, scans, and old German Fraktur print."
version: 0.3.0
author: m (MrxHermesx), Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [pdf, ocr, tesseract, fraktur, marker, kraken, kurrent, local, plates]
    related_skills: [ocr-and-documents, pdf]
---

# pdfx — local PDF extract + OCR

One CLI for born-digital PDFs, scans, Fraktur print, optional Marker layout,
and optional Kraken Kurrent HTR. **No cloud.** Does not ship model weights.

Package version **0.3.0**. Credits: `ATTRIBUTION.md` in the pdfx-hermes tarball
(or repo root next to `pdfx.py`).

## When to Use

- Local PDF or image needs text
- Folder of scans / photocopies / old print
- Old German Fraktur (**print**) or Kurrent/Sütterlin (**hand**)
- Complex layout PDF (marker, if installed)
- Plate / figure blocks (empty text + images) — see Infographics

Don't use for: cloud OCR accounts; dumping third-party books from chat
attachments without a local save path; kids profiles that forbid document tooling.

## Prerequisites

```bash
command -v pdfx || python3 "$PDFX_HOME/pdfx.py" -h
tesseract -v
ocrmypdf --version
pdftoppm -v
python3 -c "import fitz"   # pymupdf — inspect + digital

# Fraktur: TESSDATA_PREFIX = directory with *.traineddata (incl. frk + deu)
export TESSDATA_PREFIX="${TESSDATA_PREFIX:-$HOME/.local/share/tessdata}"
test -f "$TESSDATA_PREFIX/frk.traineddata"
pdfx --version   # expect 0.3.0
```

Optional: Marker under `$PDFX_HOME/.venv`; Kraken under `$PDFX_HOME/.venv-kraken`
+ models in `$PDFX_HOME/models/kraken/` (**not** in package).

Install: tarball `INSTALL.sh` / `README.md` / `DEPENDENCIES.md`.

## Procedure

Prefer `terminal` with generous `timeout` for OCR (minutes for multi-page Fraktur).

1. **Inspect** — `pdfx FILE --inspect`.  
   Completion: JSON has `text_quality`, `recommend`, and often
   `plate_page_candidates`.
2. **Route** — If `label: garbled` or recommend `ocr-fraktur-or-scan` →
   `--mode fraktur`. Else digital / scan / marker per table.
3. **Slice** — Always pass `--pages A-B` on large books before full-volume batch.
4. **OCR** — Fraktur default engine is **ocrmypdf** (Gate B). QA:
   `--engine images --dpi 300`.
5. **Batch** — `pdfx-batch-fraktur PDF OUT 20 ocrmypdf [start] [end]`; read
   `*.meta.json` craft warnings.
6. **Plates** — If candidates or body cites `Fig.`/`Taf.`, follow Infographics
   (render 200 dpi → body index → vision → local plates_search).
7. **Verify** — Spot-read ≥20 lines; optional `pdfx-metrics` craft stems.

### Quick reference

| Kind | Command |
|------|---------|
| Inspect | `pdfx FILE --inspect` |
| Digital | `pdfx FILE --mode digital --pages 1-5` |
| Auto | `pdfx FILE` |
| Marker | `pdfx FILE --mode marker --pages 1-3` |
| Scan | `pdfx FILE --ocr --mode scan --pages 1-10` |
| Fraktur | `pdfx FILE --mode fraktur --pages 8-20` |
| Fraktur QA | `pdfx FILE --mode fraktur --engine images --dpi 300` |
| Kurrent | `pdfx FILE --mode kurrent --pages 1-2` |
| Crawl | `pdfx DIR --crawl` |
| Batch | `pdfx-batch-fraktur PDF OUT 20 ocrmypdf [start] [end]` |
| Metrics | `pdfx-metrics EXTRACT.txt --json` |

### Mode header (stamp on extracts)

```
# pdfx-extract
# source: FILE.pdf
# mode: fraktur
# engine: ocrmypdf
# pages: 8-20
# inspect: label=garbled → forced fraktur
# pdfx: 0.3.0
```

### Google Fraktur trap

`kind: digital` + high chars ≠ usable text. Garbled Google Fraktur layers must
**not** be indexed as the library extract. Details:
`references/CONTROL_GATES.md`.

## Infographics

When text layer is empty but images are present → **plate zone**.

1. Read `plate_page_candidates` from `--inspect`.
2. OCR body for `Fig.` / `Taf.` citations first (plate OCR alone is weak).
3. Render candidates @ **200 dpi** (`pdftoppm -r 200` or `--render-dir`).
4. `vision_analyze` hard pages (roman numerals, labels); ignore Google watermarks.
5. Optional local `plates_index.json` + `plates_search.py` pattern.
6. Glyph QA: `references/fraktur-templates/INDEX.md` + `vision_analyze`.

Full guide: **`references/INFOGRAPHICS.md`**.

Do **not** index Google watermark / brand pages as content.

## Pitfalls

- `TESSDATA_PREFIX` must be the **tessdata directory** (contains
  `frk.traineddata`), not its parent.
- `--pages` is required discipline on big PDFs.
- Kurrent on print Fraktur is the wrong tool; print uses `frk`.
- Marker may need a local venv; GPU/Docker paths are optional/missing.
- Package has **no** kraken weights and **no** tessdata files.
- `plate_page_candidates` is a heuristic — confirm with renders.
- PyMuPDF is AGPL-or-commercial; wrapper MIT does not relicense it
  (see package `ATTRIBUTION.md`).

## Verification

- [ ] `pdfx --version` → 0.3.0
- [ ] `pdfx FILE --inspect` prints `text_quality` + `recommend`
- [ ] Inspect may list `plate_page_candidates` when images dominate pages
- [ ] Fraktur sample pages produce followable DE
- [ ] `tesseract --list-langs` (with `TESSDATA_PREFIX`) includes `frk`
- [ ] Batch: one 2-page chunk exits 0 and writes `.meta.json`

## Attribution pointer

Package root (tarball): `ATTRIBUTION.md`, `NOTICE`, `LICENSE`, `DEPENDENCIES.md`.  
Gate methodology: `references/CONTROL_GATES.md`.  
Authors: **m (MrxHermesx)** + Hermes Agent (Nous Research platform).
