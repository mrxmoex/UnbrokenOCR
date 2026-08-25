# UnbrokenOCR

> Fraktur looks broken. This stack is not.

**Project:** UnbrokenOCR · **CLI:** `pdfx` · **Package:** pdfx-hermes 0.3.0

**Upstream policy:** do **not** push into hermes-agent until the human marks it bulletproof.

---

# pdfx-hermes 0.3.0

Local PDF extract + OCR for **Hermes Agent**. **No cloud.** One CLI: `pdfx`.

| Route | Engine |
|-------|--------|
| Born-digital | PyMuPDF |
| Scan / photocopy | OCRmyPDF + Tesseract |
| Fraktur / blackletter **print** | `deu+frk` via OCRmyPDF (default) or images QA |
| Complex layout | optional Marker |
| Kurrent / hand | optional Kraken HTR |

This package does **not** ship model weights (tessdata, kraken `.mlmodel`, marker caches), control-corpus books, or Fraktur specimen **binaries** (INDEX only).

**Authors:** m (MrxHermesx) + Hermes Agent · **Platform:** Nous Research Hermes  
**License:** MIT wrapper — see `LICENSE`, `NOTICE`, `ATTRIBUTION.md`

---

## Quick install

```bash
tar xzf pdfx-hermes-0.3.0.tar.gz
cd pdfx-hermes
chmod +x INSTALL.sh pdfx.py pdfx-batch-fraktur.sh pdfx_metrics.py
./INSTALL.sh --dry-run          # report only
./INSTALL.sh                    # → ~/.local/share/pdfx + ~/.local/bin/pdfx*
./INSTALL.sh --skill            # also copy skill → ~/.hermes/skills/productivity/pdfx

export PATH="$HOME/.local/bin:$PATH"
export TESSDATA_PREFIX="${TESSDATA_PREFIX:-$HOME/.local/share/tessdata}"
# place frk.traineddata (+ deu) in TESSDATA_PREFIX first
pdfx --version
```

### System packages (examples)

```bash
# Fedora
sudo dnf install tesseract tesseract-langpack-deu ocrmypdf poppler-utils python3
pip install --user pymupdf

# Debian/Ubuntu
sudo apt install tesseract-ocr tesseract-ocr-deu tesseract-ocr-frk \
  ocrmypdf poppler-utils python3 python3-pip
pip install --user pymupdf

# macOS (Homebrew)
brew install tesseract tesseract-lang ocrmypdf poppler python3
pip3 install --user pymupdf
```

Full matrix (runtime vs optional, tessdata tips): **`DEPENDENCIES.md`**.

---

## Copy-paste commands

```bash
# Inspect (quality gate — always start here)
pdfx FILE.pdf --inspect
# → text_quality, recommend, plate_page_candidates

# Born-digital text layer
pdfx FILE.pdf --mode digital --pages 1-5

# Auto (quality-aware; refuses garbled Google layers)
pdfx FILE.pdf

# Scan / photocopy
pdfx FILE.pdf --ocr --mode scan --pages 1-10

# Fraktur / blackletter PRINT (default engine: ocrmypdf)
pdfx FILE.pdf --mode fraktur --pages 8-20 --out out.txt

# Fraktur QA path (pdftoppm + tesseract @ 300 DPI)
pdfx FILE.pdf --mode fraktur --engine images --dpi 300 --pages 13-16 --out qa.txt

# Chunked Fraktur batch
pdfx-batch-fraktur FILE.pdf ./extract/fraktur 20 ocrmypdf 1 100

# Craft-term metrics on an extract
pdfx-metrics ./extract/fraktur/chunk_001-020.txt --json

# Complex layout (needs marker in PATH or $PDFX_HOME/.venv)
pdfx FILE.pdf --mode marker --pages 1-3

# Kurrent / Sütterlin hand (needs kraken + local mlmodel)
pdfx PAGE.png --mode kurrent

# Folder crawl
pdfx DIR --crawl
```

---

## Route table

| Kind | Command |
|------|---------|
| Inspect | `pdfx FILE --inspect` → `text_quality` + `recommend` + `plate_page_candidates` |
| Born-digital | `pdfx FILE --mode digital --pages 1-5` |
| Auto | `pdfx FILE` or `--mode auto` |
| Complex layout | `pdfx FILE --mode marker --pages 1-3` |
| Scan | `pdfx FILE --ocr --mode scan` |
| Fraktur print | `pdfx FILE --mode fraktur --pages 8-20` |
| Fraktur QA | add `--engine images --dpi 300` |
| Kurrent hand | `pdfx FILE --mode kurrent --pages 1-2` |
| Folder | `pdfx DIR --crawl` |
| Papers index | add `--index-paper` |
| Batch | `pdfx-batch-fraktur PDF OUT 20 ocrmypdf [start] [end]` |
| Metrics | `pdfx-metrics EXTRACT.txt --json` |

### Google Fraktur trap

If `--inspect` says `kind: digital` but `text_quality.label: garbled` → **do not**
trust the embedded layer. Use `--mode fraktur`. Google Books Fraktur dumps can
look dense and “digital” while being unreadable garbage.

Gates (Dachdecker control corpus — methodology only, book not shipped):

| Gate | Result |
|------|--------|
| A rear smoke | PASS — fraktur recovers craft DE |
| B engine bakeoff | **ocrmypdf default** (~2.6× faster than images; craft tied) |
| C 20-page chunk | PASS — density holds; batch-ready |

Details: `skill/references/CONTROL_GATES.md`.

**Locked defaults in 0.3.0** (from 0.2.2 gates): Fraktur `--engine auto` →
**ocrmypdf**; QA → `--engine images`; chunk size **20**.

---

## Mode header example

Stamp extracts so later sessions know the route:

```
# pdfx-extract
# source: book.pdf
# mode: fraktur
# engine: ocrmypdf
# pages: 8-20
# inspect: kind=digital label=garbled → forced fraktur
# pdfx: 0.3.0
```

---

## Edge cases

| Situation | What to do |
|-----------|------------|
| `kind: digital` + `label: garbled` | `--mode fraktur` (never index digital layer) |
| `label: mixed` | Spot-read sample pages; often still force OCR |
| `TESSDATA_PREFIX` wrong | Must be dir **containing** `frk.traineddata`, not parent |
| Large book full OCR | Always `--pages`; batch in 20-page chunks |
| Marker GPU/Docker fails | Expected; use marker fast / CPU or skip marker |
| Kurrent on Fraktur **print** | Wrong tool — use `frk`, not kraken |
| Kraken on modern print | Garbage — expected |
| Empty text + images | Plate zone — see Infographics |
| Google watermark pages | Do **not** index as content |
| No `frk.traineddata` | Fraktur path fails — install tessdata (DEPENDENCIES.md) |
| PyMuPDF in closed product | AGPL or Artifex commercial — see ATTRIBUTION.md |
| macOS brew tessdata path | Check `$(brew --prefix)/share/tessdata` or user prefix |

---

## Infographics / plates

When text is empty but images exist → **plate zone**. Do not rely on plate OCR
alone.

1. `pdfx FILE --inspect` → read **`plate_page_candidates`**
2. OCR **body** for `Fig.` / `Taf.` citations (`--mode fraktur` / scan)
3. Render candidates @ **200 dpi** (`pdftoppm -r 200` or `--render-dir`)
4. `vision_analyze` hard pages (roman numerals, labels)
5. Build a local `plates_index.json` + small `plates_search.py` (pattern guide)
6. Use glyph template INDEX for blackletter caption QA

Full guide: **`references/INFOGRAPHICS.md`**  
(also `skill/references/INFOGRAPHICS.md` after skill install).

Glyph templates catalog (binaries optional/local):  
`skill/references/fraktur-templates/INDEX.md`

---

## Environment

| Var | Meaning |
|-----|---------|
| `PDFX_HOME` / `PDFX_ROOT` | Install root (venv + models) |
| `TESSDATA_PREFIX` | Directory containing `*.traineddata` |
| `PDFX_KRAKEN_MODELS` | Override HTR model directory |
| `PDFX_DPI` | Batch render DPI (default 300) |

---

## Layout

```
pdfx-hermes/
  VERSION                 # 0.3.0
  MANIFEST.txt
  LICENSE                 # MIT (wrapper)
  NOTICE                  # third-party banner
  ATTRIBUTION.md          # full credits
  DEPENDENCIES.md         # runtime vs optional
  CHANGELOG.md
  README.md
  PACKAGE_NOTES.md
  INSTALL.sh
  pdfx.py
  pdfx-batch-fraktur.sh
  pdfx_metrics.py
  references/
    INFOGRAPHICS.md       # plates / figures workflow
  skill/
    SKILL.md              # Hermes portable skill (pdfx)
    references/
      CONTROL_GATES.md
      INFOGRAPHICS.md
      fraktur-templates/INDEX.md
    scripts/              # batch + metrics copies
```

---

## Hermes skill

```bash
./INSTALL.sh --skill
# or:
cp -a skill ~/.hermes/skills/productivity/pdfx
# hermes-agent optional-skills stage:
#   optional-skills/productivity/pdfx/
```

Skill name: **`pdfx`**. Load with `skill_view(name='pdfx')` after install
(new session if the loader cached an older copy).

---

## Honesty

- Kurrent models on **modern print** look like garbage — expected.
- Fraktur **print** → tesseract `frk`, not kraken.
- Real Kurrent pages → `--mode kurrent`.
- Marker GPU/Docker is optional and often unavailable.
- No Transkribus / cloud OCR in this stack.
- Control-corpus books and foundry specimen **images** are not in the default tarball.
- 3-agent blind compare + CEO synthesis locked Fraktur defaults (see CONTROL_GATES).

---

## Docs map

| File | Read when |
|------|-----------|
| `DEPENDENCIES.md` | Installing on Fedora / Debian / macOS |
| `ATTRIBUTION.md` | Credits, AGPL note, corpus policy |
| `NOTICE` / `LICENSE` | Legal short form |
| `references/INFOGRAPHICS.md` | Plates / figures |
| `skill/references/CONTROL_GATES.md` | Why ocrmypdf is default |
| `PACKAGE_NOTES.md` | Pre-public checklist |

## Verification

```bash
pdfx --version                    # pdfx 0.3.0
pdfx FILE.pdf --inspect           # text_quality + plate_page_candidates
tesseract --list-langs | grep frk
pdfx FILE.pdf --mode fraktur --pages 1-2 --out /tmp/t.txt
```
