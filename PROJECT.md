# UnbrokenOCR

> Fraktur = (Knochen‑)Bruch in German — broken script vs Antiqua, not “looks messy.”
> UnbrokenOCR: the pipeline that doesn’t snap on blackletter.

**Project name:** UnbrokenOCR  
**CLI:** `pdfx`  
**Version (package):** 0.3.0  
**Authors:** m (MrxHermesx) · Hermes Agent fleet (under human direction)  
**License (wrapper):** MIT — see `dist/pdfx-hermes/LICENSE` + `ATTRIBUTION.md`  
**Policy:** **Do not push into hermes-agent upstream until absolute bulletproof** (human gate).

## What it is

Local-first PDF/image extraction for agents and humans:

1. **Inspect** — kind, text quality, plate candidates, dependency flags  
2. **Detect** — usable digital vs garbled Google Fraktur trap vs scan  
3. **Route** — digital / scan / Fraktur / marker / Kurrent  
4. **Execute** — best-path engines (Fraktur default: ocrmypdf)  
5. **Chunk** — batch Fraktur for long books  
6. **Plates** — separate infographic/Tafel path (not fake empty-OCR)

## Why the name

**Fraktur** (German): literally *break/fracture* (cf. Knochenbruch) — historically the “broken” script family vs round Antiqua, **not** “it looks broken/messy.”  
**UnbrokenOCR** — playful counter: blackletter is Fraktur; the *pipeline* stays unbroken (quality gates, no silent garbage index).

## Layout

```
~/src/pdf-extract/                 # house / UnbrokenOCR monorepo root
  pdfx.py                          # CLI 0.3.0 (portable)
  pdfx-batch-fraktur.sh
  pdfx_metrics.py
  PROJECT.md                       # this file
  STACK.md
  references/fraktur-templates/    # glyph charts (house)
  dist/
    COMPLETE_PACKAGE.md
    pdfx-hermes-0.3.0.tar.gz       # fellow-facing tarball
    pdfx-hermes/                   # unpacked package SoT
  models/kraken/                   # optional HTR (not in public tarball)
  smoke/
```

## Give a fellow (local / private)

```bash
tar xzf pdfx-hermes-0.3.0.tar.gz && cd pdfx-hermes
./INSTALL.sh --dry-run
./INSTALL.sh --skill   # optional Hermes skill install
pdfx book.pdf --inspect
```

## Do not

- Push to hermes-agent / Nous upstream before bulletproof sign-off  
- Ship third-party Fraktur specimen JPGs without clearance (INDEX only in public tarball)  
- Ship book corpora or secrets  
- Index garbled Google digital layers as library text  

## Control corpus (house only)

*Der vollkommene Dachdecker* (Matthaey) — gates A/B/C, full Fraktur batch, plate index.  
Not part of the public package.

## Vault

`Documents/Obsidian Vault/projects/UnbrokenOCR.md`
