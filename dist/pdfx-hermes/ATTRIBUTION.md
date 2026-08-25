# ATTRIBUTION — pdfx-hermes 0.3.1

Honest credits for code, platforms, runtimes, optional tools, reference
materials, and gate methodology. Fellows redistributing or building on this
package should keep this file (or equivalent NOTICE + LICENSE) with the tree.

## Authors (package / wrapper)

| Role | Credit |
|------|--------|
| **Primary author** | **m (MrxHermesx)** — design, Fraktur gates, packaging, house corpus work |
| Agent co-author / packaging fleet | **Hermes Agent** (CONTROL + composer subagent fleet) under human direction |

Human first. Agents assisted with implementation, docs, and bakeoffs; they do
not own the work.

## Platform

| Component | Credit | Notes |
|-----------|--------|-------|
| **Hermes Agent** | **Nous Research** | Agent runtime, skills, `delegate_task` / multi-agent compare, vision tools |

pdfx is a **local** CLI skill package for Hermes fellows. It does not send
document content to cloud OCR APIs.

## Runtime dependencies (invoked by pdfx)

| Component | Upstream | License (summary) | How pdfx uses it |
|-----------|----------|-------------------|------------------|
| **PyMuPDF** (`pymupdf`, import `fitz`) | Artifex / pymupdf | **AGPL-3.0** *or* commercial license from Artifex | Digital text extract, `--inspect`, page slice |
| **Tesseract OCR** | Google / tesseract-ocr | **Apache-2.0** | Scan + Fraktur OCR (via images path or OCRmyPDF) |
| **tessdata** (`deu`, `frk`, …) | tesseract tessdata / tessdata_best / tessdata_fast | **Apache-2.0** | Language packs; **`frk` required for Fraktur** |
| **OCRmyPDF** | ocrmypdf project | **MPL-2.0** | Default Fraktur/scan engine (`--engine ocrmypdf`) |
| **Poppler** (`pdftoppm`) | freedesktop Poppler | **GPL-2.0 and/or GPL-3.0** (distro packaging varies) | Render PDF pages for image OCR / plate dumps |

### PyMuPDF license note (accurate)

PyMuPDF is dual-licensed:

1. **GNU Affero General Public License v3.0 (AGPL-3.0)** — free use if your
   combined work complies with AGPL (including network-use source obligations
   where AGPL applies), **or**
2. **Commercial license** from Artifex Software for closed-source / non-AGPL
   redistribution.

pdfx’s own wrapper is MIT. **Embedding or shipping pymupdf with a non-AGPL
product is not automatically covered by pdfx’s MIT license.** Operators who
redistribute binaries that include PyMuPDF must satisfy AGPL or obtain a
commercial grant. See upstream: https://github.com/pymupdf/PyMuPDF

## Optional dependencies

| Component | Upstream | License (summary) | Role |
|-----------|----------|-------------------|------|
| **marker-pdf** (`marker_single`) | datalab-to / marker | **Apache-2.0** (project code as of 2026) | Complex layout → markdown (`--mode marker`) |
| **Kraken** HTR | mittagessen / kraken | **Apache-2.0** (engine) | Kurrent / handwriting (`--mode kurrent`) |
| Kraken **model weights** (`.mlmodel`) | various authors | **Per-model** (often Apache-2.0 on catalog entries; **verify each file**) | Not shipped in this tarball |

Marker and Kraken are **optional**. Core Fraktur/scan path does not require them.
Weights and large model caches are **never** vendored in the default public
tarball.

## Reference materials (not redistributed by default)

### Fraktur specimen charts (glyph templates)

- **What:** Clean alphabet / foundry specimen images for long‑s, capitals, ß,
  umlauts, and confusable pairs.
- **Status:** Third-party **foundry/font samples** used as **personal OCR
  reference only**.
- **Public tarball default:** ships **`INDEX.md` only** — not the JPG binaries —
  unless redistribution of each specimen is cleared.
- **Catalog:** `skill/references/fraktur-templates/INDEX.md`
- **Do not** rebundle specimens into a commercial font package.

### Dachdecker control corpus

- **Work:** *Der vollkommene Dachdecker* (Carl Ludwig Matthaei / Matthaey),
  historical German craft book (c. 1833).
- **Access path used for gates:** Google Books / Internet Archive style scans
  (house book id `AQKAAAAIAAJ`).
- **Use in pdfx development:** quality gates A/B/C, Google “digital layer”
  trap documentation, plate/infographic workflow examples.
- **Shipping:** **Not** included in this package. Methodology summary only:
  `skill/references/CONTROL_GATES.md`. Plate workflow pattern:
  `references/INFOGRAPHICS.md` (package) and
  `skill/references/INFOGRAPHICS.md`.

Respect copyright and the terms of the scan source when you obtain your own
copy for local research.

## Gate methodology

Fraktur defaults (engine choice, chunk size, “never trust garbled Google
layers”) were locked after controlled bakeoffs:

1. **Three independent agents** ran blind or semi-blind compares on the same
   leaves (digital layer vs Fraktur OCR; engine bakeoff).
2. **CEO / lead synthesis** merged reports into locked defaults (ocrmypdf
   default; images path for QA; 20-page batch chunks).
3. Orchestration used **Hermes `delegate_task`** (multi-agent) under human
   direction — not a single unchecked model opinion.

Summary for operators: `skill/references/CONTROL_GATES.md`.

## What this package does *not* claim

- Ownership of Tesseract, OCRmyPDF, Poppler, PyMuPDF, Marker, or Kraken.
- Redistribution rights for historical books or foundry specimen images.
- Cloud OCR (no Transkribus / vendor API path in this stack).
- That AGPL obligations for PyMuPDF vanish because the wrapper is MIT.

## Document map

| File | Purpose |
|------|---------|
| `LICENSE` | MIT for pdfx wrapper + authored docs |
| `NOTICE` | Short third-party license banner |
| `ATTRIBUTION.md` | This file — full credits |
| `DEPENDENCIES.md` | Runtime vs optional matrix + install hints |
| `references/INFOGRAPHICS.md` | Plates / figures / vision workflow |
| `skill/references/CONTROL_GATES.md` | Gate A/B/C summary |


## Research cluster (Fraktur GT / models — not shipped)

UnbrokenOCR’s eval and diplomatic-text policies were strengthened after reviewing
the 2018 open historical OCR cluster (citations only; **no weights or GT in this tarball**):

| Work | Credit | License | Use in UnbrokenOCR |
|------|--------|---------|-------------------|
| GT4HistOCR — Springmann, Reul, Dipper, Baiter (arXiv:1809.05501) | Authors + Zenodo CC-BY-4.0 GT | CC-BY-4.0 (GT) | Line-GT eval culture; transcription-policy honesty |
| archiscribe-corpus — Johannes Baiter et al. | https://github.com/jbaiter/archiscribe-corpus | CC-BY-4.0 | Optional CER microbench; long‑s diplomatic samples |
| 19th-century-fraktur-OCR — Reul et al. | https://github.com/chreul/19th-century-fraktur-OCR | MIT (repo) | Cite only; optional future Calamari track |
| Reul et al. SOTA Fraktur (arXiv:1810.03436) | Authors | arXiv | Evidence mixed real-data models beat synthetic-only |

House notes: `research/SYNTHESIS_three_sources.md`, `research/STRENGTHS_ADOPTED.md`.


## Version

Attribution for **pdfx-hermes 0.3.1** (2026-08-25).
