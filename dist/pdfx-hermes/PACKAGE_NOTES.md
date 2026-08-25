# PACKAGE_NOTES — pdfx-hermes 0.3.0

What remains before a public push to Hermes fellows / optional-skills.

## Ship checklist (this tree)

- [x] Portable `pdfx.py` (no machine-local home paths; `PDFX_HOME`, `TESSDATA_PREFIX`)
- [x] `INSTALL.sh` dry-runnable; VERSION ↔ `__version__` check; symlinks `~/.local/bin/pdfx*`
- [x] Skill frontmatter ≤60-char description + platforms linux/macos
- [x] CONTROL_GATES.md (A/B/C Dachdecker lessons)
- [x] INFOGRAPHICS.md (plates / figures workflow + house example clearly marked)
- [x] ATTRIBUTION.md, DEPENDENCIES.md, NOTICE, LICENSE (MIT wrapper)
- [x] Batch + metrics scripts
- [x] MANIFEST + VERSION **0.3.0**
- [x] Inspect emits `plate_page_candidates`
- [x] No `.venv`, no model weights, no secrets, no specimen JPGs in archive

## Still on the human before “public”

1. **tessdata `frk`** — not redistributed. See DEPENDENCIES.md per-distro.
2. **No Kraken weights** — operator-installed under `$PDFX_HOME/models/kraken/`.
3. **Marker optional** — CPU/fast; do not assume nvidia Docker.
4. **related_skills** — optional-skills copy lists skills that exist upstream
   (`ocr-and-documents`, `pdf`).
5. **Tests** — add `tests/skills/test_pdfx_skill.py` (frontmatter + path hygiene)
   before merging to hermes-agent main.
6. **Docs regen** — if landing in hermes-agent optional-skills, run website skill
   docs generator with scope discipline.
7. **macOS smoke** — `pdftoppm` / `tesseract` Homebrew paths once before advertising.
8. **House symlink** — this house may keep `~/.local/bin/pdfx` → house `pdfx.py`
   until deliberately cut over to `~/.local/share/pdfx/`.
9. **Upstream merge** — portable discovery + plate candidates should merge back
   into house source of truth before next tag.
10. **Tarball rebuild** — `tar czf pdfx-hermes-0.3.0.tar.gz -C dist pdfx-hermes`
    after final tree freeze; verify MANIFEST file list.

## Not in package (by design)

| Item | Why |
|------|-----|
| `.venv` / `.venv-kraken` | Host-specific; large |
| `models/kraken/*.mlmodel` | Weight license + size |
| tessdata `*.traineddata` | Upstream tessdata; distro packages |
| Secrets / API keys | None used |
| Full Dachdecker corpus | Third-party book; gates + INFOGRAPHICS pattern only |
| Fraktur specimen JPGs | Foundry samples; INDEX only |

## Suggested public install blurb

```bash
tar xzf pdfx-hermes-0.3.0.tar.gz && cd pdfx-hermes
./INSTALL.sh --skill
export PATH="$HOME/.local/bin:$PATH"
export TESSDATA_PREFIX="$HOME/.local/share/tessdata"   # after placing frk+deu
pdfx --version
pdfx book.pdf --inspect
```

## Version map

| Artifact | Version |
|----------|---------|
| Tarball / CLI package | **0.3.0** |
| Portable skill in package | **0.3.0** |
| House skill `pdf-extract-ocr` | **0.3.0** (points at complete package) |
| hermes-agent optional-skills `pdfx` | **0.3.0** (synced from package skill/) |
