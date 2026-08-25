# DEPENDENCIES — pdfx-hermes 0.3.0

Runtime vs optional matrix. This package ships **wrapper scripts only** — no
model weights, no tessdata binaries, no venvs.

## Matrix

| Dependency | Required for | Role | License (summary) | Notes |
|------------|--------------|------|-------------------|-------|
| **Python 3.10+** | all | CLI host | PSF | `python3` |
| **PyMuPDF** (`pymupdf`) | inspect, digital, page slice | PDF text + metadata | **AGPL-3.0 or commercial** | `import fitz` |
| **Tesseract** | scan, fraktur | OCR engine | Apache-2.0 | CLI `tesseract` |
| **tessdata `deu`** | German OCR | lang pack | Apache-2.0 | recommended |
| **tessdata `frk`** | `--mode fraktur` | Fraktur / blackletter | Apache-2.0 | **required for Fraktur** |
| **OCRmyPDF** | default fraktur/scan engine | force-OCR PDF path | MPL-2.0 | CLI `ocrmypdf` |
| **Poppler** (`pdftoppm`) | `--engine images`, plate render | PDF → PNG | GPL-2/3 | CLI `pdftoppm` |
| **marker-pdf** | `--mode marker` | layout → markdown | Apache-2.0 | optional venv |
| **Kraken** + `.mlmodel` | `--mode kurrent` | handwriting HTR | Apache-2.0 + per-model | optional; weights **not** shipped |

### Always needed for a useful Fraktur install

```
python3 + pymupdf + tesseract + frk(+deu) tessdata + ocrmypdf + pdftoppm
```

### Minimal “digital only”

```
python3 + pymupdf
```

(Inspect + born-digital extract. No OCR.)

---

## Install hints by OS

### Fedora

```bash
sudo dnf install \
  python3 python3-pip \
  tesseract tesseract-langpack-deu \
  ocrmypdf poppler-utils

# pymupdf (user or venv)
pip install --user pymupdf
# or: python3 -m venv "$PDFX_HOME/.venv" && "$PDFX_HOME/.venv/bin/pip" install pymupdf

# frk: often NOT in dnf — install traineddata manually
mkdir -p ~/.local/share/tessdata
# Download frk.traineddata from:
#   https://github.com/tesseract-ocr/tessdata_best  (or tessdata_fast)
# into ~/.local/share/tessdata/
export TESSDATA_PREFIX="$HOME/.local/share/tessdata"
```

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install \
  python3 python3-pip python3-venv \
  tesseract-ocr tesseract-ocr-deu \
  ocrmypdf poppler-utils

# frk package name when available:
sudo apt install tesseract-ocr-frk || true

pip install --user pymupdf

# If frk package missing:
mkdir -p ~/.local/share/tessdata
# place frk.traineddata here; set:
export TESSDATA_PREFIX="$HOME/.local/share/tessdata"
```

### macOS (Homebrew)

```bash
brew install tesseract tesseract-lang ocrmypdf poppler python3
pip3 install --user pymupdf

# Homebrew tessdata is usually under the tesseract prefix, e.g.:
#   $(brew --prefix)/share/tessdata
# Confirm frk exists:
ls "$(brew --prefix)/share/tessdata/frk.traineddata" 2>/dev/null \
  || echo "add frk.traineddata to TESSDATA_PREFIX"

# If frk missing, download into a user dir and:
export TESSDATA_PREFIX="$HOME/.local/share/tessdata"
mkdir -p "$TESSDATA_PREFIX"
# copy frk.traineddata (+ deu if needed) there
```

### After package INSTALL.sh

```bash
cd pdfx-hermes
chmod +x INSTALL.sh pdfx.py pdfx-batch-fraktur.sh pdfx_metrics.py
./INSTALL.sh --dry-run
./INSTALL.sh            # → ~/.local/share/pdfx + ~/.local/bin/pdfx
./INSTALL.sh --skill    # + Hermes skill
export PATH="$HOME/.local/bin:$PATH"
```

---

## Environment variables

| Variable | Meaning | Example |
|----------|---------|---------|
| `PDFX_HOME` / `PDFX_ROOT` | Install root (venvs, models) | `~/.local/share/pdfx` |
| `TESSDATA_PREFIX` | **Directory containing** `*.traineddata` | `~/.local/share/tessdata` |
| `PDFX_KRAKEN_MODELS` | HTR model directory override | `$PDFX_HOME/models/kraken` |
| `PDFX_DPI` | Batch render DPI (scripts) | `300` |

**Critical:** `TESSDATA_PREFIX` must point at the directory that **contains**
`frk.traineddata`, not the parent of `tessdata/`. Wrong parent makes tesseract
fail in confusing ways. pdfx will try to correct `…/tessdata` child if you
point at the parent and the child exists.

---

## Optional: Marker (complex layout)

```bash
export PDFX_HOME="${PDFX_HOME:-$HOME/.local/share/pdfx}"
python3 -m venv "$PDFX_HOME/.venv"
"$PDFX_HOME/.venv/bin/pip" install -U pip
"$PDFX_HOME/.venv/bin/pip" install marker-pdf pymupdf
# pdfx looks for $PDFX_HOME/.venv/bin/marker_single or marker_single on PATH
pdfx FILE.pdf --mode marker --pages 1-3
```

Prefer CPU / marker “fast” paths. GPU/Docker nvidia runtimes are **not**
assumed and often unavailable.

License: Apache-2.0 for marker project code (verify upstream LICENSE on pin).

---

## Optional: Kraken (Kurrent / hand)

```bash
export PDFX_HOME="${PDFX_HOME:-$HOME/.local/share/pdfx}"
python3 -m venv "$PDFX_HOME/.venv-kraken"
"$PDFX_HOME/.venv-kraken/bin/pip" install -U pip
"$PDFX_HOME/.venv-kraken/bin/pip" install kraken
mkdir -p "$PDFX_HOME/models/kraken"
# Place licensed .mlmodel files there yourself — not in this tarball.
# Preferred name pdfx tries first: kraken_german_finetuned.mlmodel
pdfx PAGE.png --mode kurrent
```

Engine: Apache-2.0. **Each model file has its own license** — check before
redistributing weights.

---

## Not shipped (by design)

| Item | Why |
|------|-----|
| `.venv` / `.venv-kraken` | Host-specific, large |
| `models/kraken/*.mlmodel` | Size + per-model license |
| `*.traineddata` | Upstream tessdata / distro packages |
| Full control-corpus PDFs | Third-party books; gates summary only |
| Fraktur specimen **binaries** | Foundry samples; INDEX only by default |
| Secrets / API keys | None used |

---

## Quick verification

```bash
command -v pdfx tesseract ocrmypdf pdftoppm
python3 -c "import fitz; print('pymupdf OK')"
export TESSDATA_PREFIX="${TESSDATA_PREFIX:-$HOME/.local/share/tessdata}"
tesseract --list-langs 2>&1 | grep -E 'frk|deu'
pdfx /path/to/sample.pdf --inspect
```

See also: `ATTRIBUTION.md`, `NOTICE`, `README.md`.
