#!/usr/bin/env bash
# INSTALL.sh — install pdfx CLI + optional Hermes skill (no model weights).
# Usage:
#   ./INSTALL.sh              # copy to ~/.local/share/pdfx + symlink CLI
#   ./INSTALL.sh --dry-run    # report only
#   ./INSTALL.sh --skill      # also install skill into ~/.hermes/skills/
#   ./INSTALL.sh --version    # print package version and exit
set -euo pipefail

DRY=0
INSTALL_SKILL=0
for arg in "$@"; do
  case "$arg" in
    --dry-run|-n) DRY=1 ;;
    --skill) INSTALL_SKILL=1 ;;
    --version|-V)
      PKG_DIR="$(cd "$(dirname "$0")" && pwd)"
      tr -d '[:space:]' <"${PKG_DIR}/VERSION" 2>/dev/null || echo unknown
      exit 0
      ;;
    -h|--help)
      sed -n '2,10p' "$0"
      exit 0
      ;;
    *)
      echo "unknown arg: $arg (try --help)" >&2
      exit 2
      ;;
  esac
done

PKG_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION="$(tr -d '[:space:]' <"${PKG_DIR}/VERSION" 2>/dev/null || echo unknown)"
BIN_DIR="${HOME}/.local/bin"
SHARE_DIR="${HOME}/.local/share/pdfx"
SKILL_DST="${HERMES_HOME:-$HOME/.hermes}/skills/productivity/pdfx"
TESSDATA_USER="${HOME}/.local/share/tessdata"

# Version consistency: VERSION file vs pdfx.py __version__
PY_VER="$(python3 -c "import re,pathlib; t=pathlib.Path(r'''${PKG_DIR}/pdfx.py''').read_text(); m=re.search(r'__version__\s*=\s*[\"\\']([^\"\\']+)', t); print(m.group(1) if m else '')" 2>/dev/null || true)"
if [[ -n "$PY_VER" && "$PY_VER" != "$VERSION" ]]; then
  echo "ERROR: VERSION=${VERSION} but pdfx.py __version__=${PY_VER}" >&2
  exit 1
fi

run() {
  if [[ "$DRY" -eq 1 ]]; then
    echo "[dry-run] $*"
  else
    eval "$@"
  fi
}

echo "=== pdfx-hermes ${VERSION} install ==="
echo "package: ${PKG_DIR}"
[[ "$DRY" -eq 1 ]] && echo "(dry-run mode — no files will change)"

# --- dependency checks ---
need=()
warn=()
for cmd in python3 tesseract ocrmypdf pdftoppm; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "OK  $cmd → $(command -v "$cmd")"
  else
    need+=("$cmd")
    echo "MISS $cmd"
  fi
done

# pymupdf required for --inspect / digital
if python3 -c "import fitz" 2>/dev/null; then
  echo "OK  pymupdf (fitz)"
else
  warn+=("pymupdf (pip install pymupdf) — needed for --mode digital / --inspect")
  echo "WARN pymupdf not importable"
fi

# tessdata frk
frk_ok=0
for td in "${TESSDATA_PREFIX:-}" "$TESSDATA_USER" \
  /usr/share/tesseract-ocr/5/tessdata \
  /usr/share/tesseract-ocr/4.00/tessdata \
  /usr/share/tessdata; do
  [[ -z "$td" ]] && continue
  if [[ -f "${td}/frk.traineddata" ]]; then
    echo "OK  frk.traineddata in $td"
    frk_ok=1
    break
  fi
done
if [[ "$frk_ok" -eq 0 ]]; then
  warn+=("tessdata frk (Fraktur) missing — place frk.traineddata in ~/.local/share/tessdata")
  echo "WARN frk.traineddata not found"
  echo "     tip: mkdir -p ~/.local/share/tessdata"
  echo "          # download frk.traineddata from tesseract tessdata_best or tessdata_fast"
  echo "          # export TESSDATA_PREFIX=\$HOME/.local/share/tessdata"
fi

# deu recommended
deu_ok=0
for td in "${TESSDATA_PREFIX:-}" "$TESSDATA_USER" /usr/share/tesseract-ocr/5/tessdata /usr/share/tessdata; do
  [[ -z "$td" ]] && continue
  [[ -f "${td}/deu.traineddata" ]] && deu_ok=1 && break
done
[[ "$deu_ok" -eq 0 ]] && warn+=("deu.traineddata recommended for German OCR")

if [[ ${#need[@]} -gt 0 ]]; then
  echo ""
  echo "Install missing system packages (example Fedora):"
  echo "  sudo dnf install tesseract tesseract-langpack-deu ocrmypdf poppler-utils"
  echo "Debian/Ubuntu:"
  echo "  sudo apt install tesseract-ocr tesseract-ocr-deu tesseract-ocr-frk ocrmypdf poppler-utils"
fi

# --- install layout ---
echo ""
echo "--- install files ---"
run "mkdir -p $(printf %q "$BIN_DIR") $(printf %q "$SHARE_DIR")"
run "cp -a $(printf %q "$PKG_DIR/pdfx.py") $(printf %q "$SHARE_DIR/pdfx.py")"
run "cp -a $(printf %q "$PKG_DIR/pdfx-batch-fraktur.sh") $(printf %q "$SHARE_DIR/pdfx-batch-fraktur.sh")"
run "cp -a $(printf %q "$PKG_DIR/pdfx_metrics.py") $(printf %q "$SHARE_DIR/pdfx_metrics.py")"
# optional reference docs into share (no JPGs)
if [[ -d "$PKG_DIR/skill/references" ]]; then
  run "mkdir -p $(printf %q "$SHARE_DIR/references")"
  run "cp -a $(printf %q "$PKG_DIR/skill/references/.") $(printf %q "$SHARE_DIR/references/")"
fi
run "chmod +x $(printf %q "$SHARE_DIR/pdfx.py") $(printf %q "$SHARE_DIR/pdfx-batch-fraktur.sh") $(printf %q "$SHARE_DIR/pdfx_metrics.py")"
run "ln -sfn $(printf %q "$SHARE_DIR/pdfx.py") $(printf %q "$BIN_DIR/pdfx")"
run "ln -sfn $(printf %q "$SHARE_DIR/pdfx-batch-fraktur.sh") $(printf %q "$BIN_DIR/pdfx-batch-fraktur")"
run "ln -sfn $(printf %q "$SHARE_DIR/pdfx_metrics.py") $(printf %q "$BIN_DIR/pdfx-metrics")"

# PDFX_HOME hint file
if [[ "$DRY" -eq 1 ]]; then
  echo "[dry-run] write $SHARE_DIR/env.sh"
  echo "[dry-run] write $SHARE_DIR/VERSION"
else
  cat >"${SHARE_DIR}/env.sh" <<EOF
# source me or export in shell profile
export PDFX_HOME="${SHARE_DIR}"
# Tessdata must be the directory that contains *.traineddata
# export TESSDATA_PREFIX="\${HOME}/.local/share/tessdata"
EOF
  echo "$VERSION" >"${SHARE_DIR}/VERSION"
  echo "wrote ${SHARE_DIR}/env.sh"
fi

if [[ "$INSTALL_SKILL" -eq 1 ]]; then
  echo "--- Hermes skill → ${SKILL_DST} ---"
  run "mkdir -p $(printf %q "$(dirname "$SKILL_DST")")"
  run "rm -rf $(printf %q "$SKILL_DST")"
  run "cp -a $(printf %q "$PKG_DIR/skill") $(printf %q "$SKILL_DST")"
fi

echo ""
echo "=== done ==="
if [[ "$DRY" -eq 1 ]]; then
  echo "(dry-run only — no files changed)"
else
  echo "CLI: ${BIN_DIR}/pdfx  (ensure ~/.local/bin is on PATH)"
  echo "PDFX_HOME → ${SHARE_DIR}"
  echo "Try:  pdfx --version  OR  pdfx --help"
  if [[ -x "${BIN_DIR}/pdfx" ]]; then
    "${BIN_DIR}/pdfx" --version >/dev/null 2>&1 && echo "smoke: pdfx --version OK ($VERSION)" \
      || echo "smoke: pdfx --version failed (deps?)"
    "${BIN_DIR}/pdfx" -h >/dev/null 2>&1 && echo "smoke: pdfx -h OK" \
      || echo "smoke: pdfx -h failed"
  fi
fi

# Always print mode-header smoke one-liner (docs + post-install reminder)
echo ""
echo "Mode-header smoke (after PATH + deps):"
echo "  pdfx BOOK.pdf --inspect"
echo "  # expect JSON keys: kind, pages, text_quality{label,score}, recommend"
echo "  # Google Fraktur trap: kind=digital + text_quality.label=garbled → use --mode fraktur"
echo "  pdfx BOOK.pdf --mode auto --pages 1-2 2>&1 | head -1"
echo "  # stderr mode-header: # auto → mode=… kind=… quality=… recommend=…"

if [[ ${#warn[@]} -gt 0 ]]; then
  echo ""
  echo "Warnings:"
  for w in "${warn[@]}"; do echo "  - $w"; done
fi
if [[ ${#need[@]} -gt 0 ]]; then
  echo ""
  echo "Missing required commands: ${need[*]}"
  # dry-run still exits 0 so CI can inspect plan; real install fails hard
  if [[ "$DRY" -eq 0 ]]; then
    exit 1
  fi
fi
exit 0
