# PACKAGE_NOTES — pdfx-hermes 0.2.2

What remains before a public push to Hermes fellows / optional-skills.

## Ship checklist (this tarball)

- [x] Portable `pdfx.py` (no `/home/...` paths; `PDFX_HOME`, `TESSDATA_PREFIX`)
- [x] `INSTALL.sh` dry-runnable; symlinks `~/.local/bin/pdfx`
- [x] Skill frontmatter ≤60-char description + platforms
- [x] CONTROL_GATES.md (A/B/C Dachdecker lessons)
- [x] Batch + metrics scripts (no venv hardcode to a single user tree)
- [x] MANIFEST + VERSION 0.2.2
- [x] No `.venv`, no model weights, no secrets in archive

## Still on the human before “public”

1. **tessdata `frk`** — not redistributed here. Document per-distro:
   - Debian/Ubuntu: `apt install tesseract-ocr-frk` when packaged
   - Else: download `frk.traineddata` from tesseract `tessdata_best` or `tessdata_fast` into `~/.local/share/tessdata`
   - Always set `TESSDATA_PREFIX` to that **directory** (not its parent)
2. **No Kraken weights** — HTR models stay operator-installed under `$PDFX_HOME/models/kraken/` or `~/.local/share/htrmopo/`. Do not vendor `.mlmodel` blobs without license review.
3. **Marker optional** — not required for Fraktur/scan path. If documented, pin install to CPU/`--mode fast`; do not assume nvidia Docker.
4. **related_skills** — optional-skills copy should only list skills that exist in the target hermes-agent tree (`ocr-and-documents`, `pdf`). Drop user-local-only names on PR.
5. **Tests** — add `tests/skills/test_pdfx_skill.py` (frontmatter + path hygiene) before merging to hermes-agent main.
6. **Docs regen** — if landing in hermes-agent optional-skills, run website skill docs generator with scope discipline.
7. **License pass** — confirm MIT OK for pdfx wrapper; third-party CLIs (tesseract, ocrmypdf, kraken, marker) remain their own licenses.
8. **macOS** — platforms include macos; smoke `pdftoppm`/`tesseract` Homebrew paths once before advertising.
9. **House symlink** — this house may keep `~/.local/bin/pdfx` → `~/src/pdf-extract/pdfx.py` until deliberately cut over to `~/.local/share/pdfx/`.
10. **Upstream house source** — `~/src/pdf-extract/pdfx.py` may still have machine-local ROOT; portable copy lives in `dist/pdfx-hermes/`. Consider merging portable discovery back into source of truth before next tag.

## Not in package (by design)

| Item | Why |
|------|-----|
| `.venv` / `.venv-kraken` | Host-specific; large |
| `models/kraken/*.mlmodel` | Weight license + size |
| tessdata `*.traineddata` | Upstream tessdata; distro packages |
| Secrets / API keys | None used |
| Full Dachdecker corpus | Copyrighted book; gates summary only |

## Suggested public install blurb

```bash
tar xzf pdfx-hermes-0.2.2.tar.gz && cd pdfx-hermes
./INSTALL.sh --skill
export PATH="$HOME/.local/bin:$PATH"
export TESSDATA_PREFIX="$HOME/.local/share/tessdata"   # after placing frk+deu
pdfx book.pdf --inspect
```

## Version map

| Artifact | Version |
|----------|---------|
| Tarball / CLI package | 0.2.2 |
| Portable skill in package | 0.2.2 |
| House skill `pdf-extract-ocr` | 0.2.3 (points at package + HOUSE.md) |
