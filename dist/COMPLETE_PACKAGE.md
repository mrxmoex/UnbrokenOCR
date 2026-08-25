# COMPLETE PACKAGE — UnbrokenOCR / pdfx-hermes 0.3.0


**One-page handoff for the human.**  
Ship file: `~/src/pdf-extract/dist/pdfx-hermes-0.3.0.tar.gz` (~30 KB).

## What shipped

Local **PDF extract + OCR** toolkit for Hermes fellows. No cloud, no model weights, no book corpus.

| Piece | What it does |
|-------|----------------|
| `pdfx` | One CLI: inspect → digital / scan / Fraktur / optional marker / Kurrent |
| `pdfx-batch-fraktur` | 20-page chunk overnight path (default engine **ocrmypdf**) |
| `pdfx-metrics` | Craft-term / long‑s density on extracts |
| Hermes skill `pdfx` | Portable skill + CONTROL_GATES + INFOGRAPHICS + template INDEX |
| `INSTALL.sh` | Dry-run, dep check, `~/.local/share/pdfx` + bin symlinks, optional `--skill` |

**0.3.0 vs 0.2.2:** mode-detect header + edge_flags + plates sidecar;  full legal set (LICENSE/NOTICE/ATTRIBUTION/DEPENDENCIES/CHANGELOG), INSTALL polish (`--version`, version gate, mode-header smoke blurb), INFOGRAPHICS map, path-clean portable Python (works without a house `.venv`), release checklist.

## How to give fellows

```bash
# 1. Send the tarball only (not the house src tree)
scp dist/pdfx-hermes-0.3.0.tar.gz fellow:

# 2. Fellow:
tar xzf pdfx-hermes-0.3.0.tar.gz && cd pdfx-hermes
./INSTALL.sh --dry-run          # sanity
./INSTALL.sh --skill            # CLI + Hermes skill
export PATH="$HOME/.local/bin:$PATH"
pip install --user pymupdf      # if needed
# place frk.traineddata (+ deu) → ~/.local/share/tessdata
export TESSDATA_PREFIX="$HOME/.local/share/tessdata"
pdfx book.pdf --inspect
```

Hermes: new session → `skill_view(name='pdfx')`.

## Plate + template story

1. **Inspect first.** Google Fraktur dumps often report `kind: digital` with **`text_quality.label: garbled`**. Do not index that layer — route `--mode fraktur`.
2. **Plates** (optional): render hard pages for vision QA; not required for OCR.
3. **Templates** (optional): clean Fraktur alphabet/foundry charts for glyph disambiguation (long‑s, I/J/T, ß).  
   Public package ships **`INDEX.md` only** — no JPGs (third-party specimens).  
   Fellows drop their own charts under `$PDFX_HOME/references/fraktur-templates/` using the INDEX names.
4. **Gates A/B/C** (Dachdecker): rear smoke PASS · ocrmypdf ~2.6× faster than images at tied craft · 20-page chunks hold density. Defaults locked accordingly.

## Success criteria (met)

- [x] `pdfx-hermes-0.3.0.tar.gz` exists  
- [x] `INSTALL.sh --dry-run` OK  
- [x] No accidental `/home/…` secrets in skill/CLI  
- [x] Inspect smoke on Dachdecker part2 → garbled + `ocr-fraktur-or-scan`  
- [x] This one-pager written  

## Pointers

| Doc | Use |
|-----|-----|
| `README.md` | Commands + route table |
| `RELEASE_CHECKLIST.md` | Checked ship gates |
| `skill/references/CONTROL_GATES.md` | Why defaults are what they are |
| `skill/references/INFOGRAPHICS.md` | Terminal route map |
| `DEPENDENCIES.md` | What fellows must install on the host |
