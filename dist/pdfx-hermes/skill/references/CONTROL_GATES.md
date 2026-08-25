# Control gates A/B/C — Dachdecker summary

Corpus: *Der vollkommene Dachdecker* (Matthaey), Google Books style Fraktur scan.  
pdfx: 0.2.1 → 0.2.2 → **0.3.0** (docs package + plate_page_candidates; Fraktur auto → ocrmypdf). Date: 2026-08-25.

## Why gates exist

Three independent agents compared digital vs Fraktur OCR on the same leaves. Unanimous:

1. **Google “digital” layer is a trap.** Inspect reports `kind: digital` with high char density; content is broken Fraktur→Latin garbage — not greppable craft German.
2. **Real path = image OCR with `deu+frk` (or force-OCR via ocrmypdf).**
3. Historical pdfx bugs (fixed in 0.2.1+): wrong `TESSDATA_PREFIX` (parent of tessdata), `--pages` ignored on OCR, `--skip-text` instead of `--force-ocr` on pre-garbled layers.
4. Marker/nvidia and Kraken/Kurrent were correctly out of scope for print Fraktur.

## Gate results

| Gate | Verdict | Headline |
|------|---------|----------|
| **A** rear smoke | **PASS** | part2 p1–2: ~6 craft stems, ~8.6 s, followable DE |
| **B** engine bakeoff | **ocrmypdf default** | ~2.6× faster than `images`; craft totals tied (9=9) |
| **C** 20-page chunk | **PASS** | part1 1–20: ~65 s on images path, 9 stems / 54 hits, no density collapse |

### Gate B detail (pages 13–16)

| Metric | `images` (pdftoppm+tesseract@300) | `ocrmypdf` |
|--------|----------------------------------:|-----------:|
| Wall (4 pp) | ~17.4 s | ~6.6 s |
| s/page | ~4.4 | ~1.7 |
| Craft total | 9 | 9 |
| Persistent render | ~1.6 MB/page PNG | none |

**Decision:** overnight / batch default = **ocrmypdf**. Override to `images` for QA, quote-critical slices, or re-OCR of thin craft-term failures.

## Locked defaults (0.2.2 → 0.3.0)

| Setting | Value |
|---------|--------|
| Fraktur `--engine auto` | **ocrmypdf** |
| Batch script default | **ocrmypdf** |
| QA / debug | `--engine images --dpi 300` |
| Chunk size | 20 pages |
| Render cleanup | always on images path |

## Operator checklist

1. Always `pdfx FILE --inspect` first; if `text_quality.label` is `garbled`/`mixed`, use `--mode fraktur`.
2. Never trust `kind: digital` without a short human/agent spot-read.
3. Batch: `pdfx-batch-fraktur PDF OUT_DIR 20 ocrmypdf [start] [end]`.
4. Metrics: `pdfx-metrics extract.txt --json` (craft lexicon + long‑s count).
5. Keep raw OCR; optional `ſ→s` normalized sidecar for search.

## Out of scope (still hold)

- Marker nvidia runtime
- Cloud / Transkribus
- Shipping kraken weights or tessdata inside the tarball
