# UnbrokenOCR stack

# pdf-extract stack (local)

Home of Wave-2 document tools. Part of the GitHub Library **implementation stash**, not a fork dump.

Updated 2026-08-25: **pdfx 0.2.2** — Fraktur default engine **ocrmypdf** (Gate B); images = QA.

## Layout

```
~/src/pdf-extract/
  pdfx.py              # one CLI for all routes (0.2.1)
  archive/             # timestamped backups of pdfx.py
  .venv/               # pymupdf + marker-pdf 2.0
  .venv-kraken/        # kraken 7.1 HTR
  models/kraken/       # offline HTR models + USAGE.md
  smoke/               # install smoke outputs only
  STACK.md             # this file
```

## Papers library index (where extracts go)

```
Documents/papers/
  arxiv/<cat>/<year>/<id>/
    extract/{marker,pymupdf,ocr,fraktur,kurrent}.*
  books/google/<ID>/
    parts/  extract/  compare/
  inbox/   (+ drop/ via HomeDrop)
```

## Route table

| Input | Tool | pdfx flag |
|-------|------|-----------|
| Born-digital PDF | pymupdf | `--mode digital` (+ `--pages`) |
| Complex layout | marker fast | `--mode marker --pages 1-3` |
| Scan / photocopy | ocrmypdf or images | `--ocr` / `--mode scan` |
| Fraktur print | ocrmypdf force-ocr (default) or images QA | `--mode fraktur --pages 8-20` |
| Fraktur via ocrmypdf | force-ocr on slice | `--mode fraktur --engine ocrmypdf` |
| Kurrent / Sütterlin | kraken | `--mode kurrent --pages 1-2` |
| Auto (quality-aware) | inspect gate | default `--mode auto` |
| Folder | list | `--crawl` |
| Write into papers extract/ | | add `--index-paper` |

### Critical flags (0.2.1)

- `--pages A-B` honored on digital + OCR  
- `--engine auto|images|ocrmypdf` (Fraktur defaults to **images**)  
- `--dpi 300` for render OCR  
- `TESSDATA_PREFIX` = `~/.local/share/tessdata`  
- Inspect reports `text_quality` + `recommend` (catches Google Fraktur trap)

## Preferred Kurrent model

`models/kraken/kraken_german_finetuned.mlmodel`

## Catalog

| Repo | Ops |
|------|-----|
| marker | **already** (fast only here) |
| MinerU | hold |
| PaddleOCR | hold |

## Fraktur glyph templates

`references/fraktur-templates/` — 8 clean specimen charts (INDEX.md).  
Primary: `01_deutsches_alphabet_in_fraktur.jpg` · period: `07_mainzer_…historic.jpg`.

## Related vault

- github-library/wave-2-pdf-ocr  
- books/google/AQKAAAAIAAJ/compare/CEO_SYNTHESIS.md  
- books/google/AQKAAAAIAAJ/compare/CONTROL_UPGRADE_PLAN.md  
- books/google/AQKAAAAIAAJ/extract/plates/ (plates + templates mirror)  
- projects/HomeDrop-webapp  

