# SOURCE 2 — jbaiter/archiscribe-corpus

**Status:** Independent deep analysis for UnbrokenOCR (no multi-agent coordination)  
**Analyzed:** 2026-08-25  
**Primary repo:** https://github.com/jbaiter/archiscribe-corpus  
**Companion tool:** https://github.com/jbaiter/archiscribe · site (historical): https://archiscribe.jbaiter.de  
**Local raw mirror:** `research/raw/archiscribe-README.md`

---

## 1. What is Archiscribe?

**Archiscribe** is two things:

1. **A crowdsourcing web app** (`jbaiter/archiscribe`, Go, MIT) that samples line crops from Internet Archive / Archive.org 19th-century German books and lets volunteers type diplomatic ground-truth transcriptions.[2][3]
2. **A published corpus** (`jbaiter/archiscribe-corpus`) — the Git-backed dump of those line images + transcriptions, aimed at “as much diverse OCR ground truth for 19th Century German prints as possible.”[1]

It was built around the BBAW OCR Workshop (Berlin, Sep 2017) and is described in Springmann, Reul, Dipper & Baiter (2018) as a peer corpus *alongside* (not inside) GT4HistOCR.[3][4]

### Corpus size (canonical README numbers)

| Metric | Value |
|--------|------:|
| Line pairs (PNG + TXT) | **4 255**[1] |
| Works / volumes | **112**[1] |
| Calendar span | **73 years** (years present: 1800–1897, not every year filled)[1] |
| Mean lines / work | ~38 |
| Decade coverage | ~380–505 lines per decade 1800s–1890s (deliberately even)[1] |

Paper snapshot (Aug 2018 access note): **4 145 lines / 109 works / 72 years** — the GitHub tree is slightly larger (post-paper growth + late-2018 unicode fixes).[3][1]

### Languages, scripts, period

| Axis | Content |
|------|---------|
| **Language** | German (print prose, journalism, scholarship, fiction, law, etc.)[1][2] |
| **Script / type** | **Printed Fraktur / blackletter** (19th c.). **Not Kurrent / handwriting.**[1][2] |
| **Antiqua** | Possible mixed quotes/inserts (paper notes real pages can mix faces); sampling heuristic targets Fraktur |
| **Period** | 1800–1900 sampling window; works catalogued 1800–1897 |
| **Source scans** | Internet Archive items (many Google Books `bub_gb_*` IDs) via IIIF |

**Fraktur heuristic (tool):** download Archive.org OCR text; look for the token that Antiqua-trained engines produce for **ſt** in *ist* (classic Fraktur OCR fail). False positives (Antiqua with long‑s) → re-roll volume.[3]

**Not covered:** manuscript Kurrent/Sütterlin, incunabula, Latin-only runs, full-page layout GT, plate/Tafel graphics.

### Annotation / data layout

```
archiscribe-corpus/
  LICENSE.md                 # CC BY 4.0 full text
  README.md                  # stats + works table (Archive.org + IIIF links)
  transcriptions/
    <YYYY>/                  # publication year folders
      <archive_id>.json      # work metadata + line IIIF URLs
      <archive_id>_<lineid>.png
      <archive_id>_<lineid>.txt
```

**Tree inventory (master, API):** 8 624 blobs — **4 255 PNG + 4 255 TXT + 112 JSON + 2 MD**.[1]

**Per-line pair**

- `*.png` — single printed line crop (from Archive.org IIIF; ABBYY line boxes reused).
- `*.txt` — UTF-8 diplomatic transcription (one line + newline). **Not** `*.gt.txt` naming (unlike OCRopus/GT4HistOCR convention), but same logical pairing: stem-matched image/text.

**Observed diplomatic glyphs (samples):**

- Long s: `ſ` (U+017F)
- Combining umlaut (historical spelling): `oͤ` etc. (U+0364)
- Soft hyphen / line continuation: `⸗` (U+2E17)
- Period punctuation/quotes: `«»„”—, ∴`

Example GT: `hen, dieſes bey dem Verluſte der einzelnen gewinnt. Mit welchem`

**Per-work JSON** (`title`, `year`, `id`, `manifest`, `lines[]`):

Each line entry has `id`, plus IIIF URLs for `line`, `previous`, `next` (context for hard cases in the UI).

**Transcription rules:** simplified **Deutsches Textarchiv (DTA)** guidelines shown to first-time contributors.[3][7]

**No releases / no Git tags** on the corpus repo; data lives only as Git history on `master`.

---

## 2. How to use: training / eval vs reference-only

### Direct training / evaluation (designed use)

Springmann et al. single out Archiscribe as **already line-aligned** and “directly usable for OCR model training,” unlike OCR-D PAGE/ALTO dumps that need zone→line cutting.[3]

Practical recipe:

1. Clone or sparse-checkout `transcriptions/`.
2. Treat each stem as `(image.png, label.txt)` — rename to `.gt.txt` if feeding OCRopy/Calamari/Kraken pipelines that expect that suffix.
3. Hold out by **work id** or **year band**, not random lines only (lines within a work share typeface/scan quality).
4. Metrics: classic **CER / WER** (character/word error) against the diplomatic TXT; optionally normalize long‑s / hyphenation for a “modernized” secondary score (UnbrokenOCR product search uses ſ→s sidecars — keep both).

Downstream practice: Calamari 19th-c. Fraktur models have been described as trained on GT4HistOCR **plus** Archiscribe and other free Fraktur sources.[8]

### Reference-only / UnbrokenOCR product path (no retrain)

Even without training:

- **Gold line bank** for CER smoke tests of `pdfx --mode fraktur` / tesseract `frk` / ocrmypdf vs house engines.
- **Character inventory** for quality gates (expect `ſ`, historical umlauts, `⸗` line-break hyphens).
- **Decade diversity check** — sample lines from early vs late 19th c. when tuning thresholds.
- **Provenance links** — each work has Archive.org + IIIF; useful to re-fetch full pages if line crops are too tight for layout QA.

### Not a drop-in for full-book product eval

Lines are **random samples within volumes**, not contiguous pages. You cannot reconstruct a whole book or run plate/Tafel gates on this corpus alone.

---

## 3. Strengths (esp. UnbrokenOCR quality gates / metrics)

| Strength | Why it matters for UnbrokenOCR |
|----------|--------------------------------|
| **True Fraktur print GT** | Matches house `fraktur` route (not Kurrent); aligns with Google Books / IA scan world UnbrokenOCR already fights. |
| **Line image ↔ text pairs** | Immediate CER harness without PAGE XML surgery — Gate A/B smoke can score engines, not only craft-stem heuristics. |
| **Diplomatic long‑s** | Validates canonical long‑s product files vs ſ→s search sidecars (gate: both exist; CER on canonical). |
| **Even 19th-c. decade spread** | Reduces “one typeface decade” bias when sampling eval subsets. |
| **IA / Google-Books DNA** | Same ABBYY-bad / layout-ok pathology described in the paper mirrors the UnbrokenOCR “digital garbled → force Fraktur” trap.[3] |
| **CC BY 4.0** | Clear reuse for research, metrics docs, and (with attribution) model training.[1][6] |
| **Modest size** | Full clone is practical for CI (~**170 MiB** GitHub `size`; ~**178 MB** blob sum) — not multi‑GB GT4HistOCR. |
| **No auth wall on original tool** | Historical crowdsource design; Git history shows review commits (“Fix unicode mistakes”).[1] |
| **Cited in German OCR ecosystem** | Anchors house practice to DTA-style transcription + Springmann/Reul line-GT tradition.[3][4][8] |

### Concrete metric hooks for house gates

Suggested additions (orthogonal to craft_stem gates in `ocr-quality-gates`):

1. **Gate-A′ CER microbench:** 50–100 Archiscribe lines (stratified by decade) → report mean CER for `frk` / ocrmypdf / images engine.  
2. **Long‑s retention rate:** fraction of GT `ſ` recovered (not collapsed to `s`/`f`).  
3. **Hyphenation symbol check:** presence/handling of `⸗` vs ASCII `-`.  
4. **Confusable set:** `ſ/f`, `i/j`, umlaut forms — error confusion matrix on the microbench.  
5. **Attribution fixture** for fellow packages: cite corpus when shipping benchmark numbers.

---

## 4. Caveats

| Caveat | Detail |
|--------|--------|
| **Clone / disk** | GitHub repo `size` ≈ **173 987 KiB (~170 MiB)**; blob payload ≈ **178 MB**. Full history clone may be larger. **No release tarballs.** Do **not** LFS-surprise — PNGs are ordinary blobs (~15–40 KB typical). |
| **License** | **CC BY 4.0** on corpus (`LICENSE.md`).[1][6] Attribution required; not public domain. Tool code is **MIT**.[2] IA underlying scans have their own rights/status — GT text+crops are what this license covers. Paper also states CC-BY 4.0 for the Archiscribe data.[3] |
| **Maintenance** | **Stale.** Last corpus push **2018-12-31** (“Fix more unicode mistakes”).[1] Tool last push **2018-02-22**.[2] Site `archiscribe.jbaiter.de` returned **404** at analysis time. Not archived flag, but effectively frozen. |
| **Crowdsource quality** | No login; paper says vandalism “not been an issue so far,” with a review UI + Git revert path.[3] Residual unicode mistakes were still being fixed end-2018 — treat as **good-not-perfect** GT. |
| **Scale** | **4.2k lines** is small vs GT4HistOCR (~313k) or DTA19 Fraktur (~244k lines in paper Table 6).[3][5] Fine for eval microbench / domain add-on; weak as sole modern trainer. |
| **Not in GT4HistOCR Zenodo bundle** | Separate corpus; don’t expect it inside the Zenodo GT4HistOCR record.[5] |
| **Line-only** | No page XML, reading order, tables, or **plates/Tafeln** — zero help for UnbrokenOCR plate index path. |
| **Segmentation inherited from ABBYY** | Bad crops / merged lines possible when IA layout fails; GT assumes that segmentation. |
| **Naming vs toolchain** | `.txt` not `.gt.txt`; no official train/val/test split files. |
| **Kurrent gap** | Does not exercise `kurrent` mode. |
| **Dependency if recreating pipeline** | Original flow needs Archive.org search + IIIF; for *using* the frozen corpus you only need Git + image/OCR tools. |

### Overlap with German historical OCR practice

| Practice | Archiscribe relationship |
|----------|---------------------------|
| **DTA transcription guidelines** | Explicit simplified DTA rules for contributors.[3][7] |
| **GT4HistOCR / Springmann–Reul line** | Same paper family; Archiscribe is the crowd IA Fraktur sibling, not a GT4HistOCR subfolder.[3][4][5] |
| **OCR-D** | Contrasted in paper: OCR-D needs PAGE/ALTO→line extraction; Archiscribe already line-paired.[3] |
| **Tesseract `frk` / LSTM training culture** | Line pairs match Tesseract 4+ / OCRopy / Calamari training shape.[3][8] |
| **Internet Archive + Google Books Fraktur** | Core sampling domain — same messy scans UnbrokenOCR routes off digital layers. |
| **Calamari Fraktur19 models** | Community training notes list Archiscribe among free Fraktur GT sources.[8] |
| **OCR-D / IMPACT / RIDGES** | Broader DE ecosystem; Archiscribe is lighter-weight crowd IA slice, not a DFG module. |

---

## 5. UnbrokenOCR implications (actionable)

| Priority | Implication |
|----------|-------------|
| **High — eval microbench** | Add optional `archiscribe` CER fixture (subset clone or vendored 100-line sample) under quality gates; score engines before Gate C full chunks. **Do not ship multi‑GB weights/corpora in fellow tarball** (package policy). |
| **High — long‑s product policy** | GT confirms diplomatic `ſ` is the right canonical form; keep ſ→s **sidecar** for `rg`, never replace canonical. |
| **Medium — decade sampling** | When CEO multi-agent compares engines, pick Archiscribe lines from ≥3 decades to avoid overfit to one face. |
| **Medium — Google trap narrative** | Paper’s ABBYY-bad-on-Fraktur / good-segmentation story is citable justification for inspect→fraktur override.[3] |
| **Low — training** | Full fine-tune on 4k lines alone is optional; if training, merge with larger Fraktur GT (GT4HistOCR DTA19 / other) and attribute CC BY. |
| **Out of scope** | Plates, Kurrent, full-page layout, living crowdsource (site down). |
| **Clone guidance** | Prefer `git clone --depth 1` (~170 MiB class) or sparse `transcriptions/1848` smoke only. **Do not download multi‑GB** unless expanding beyond this source. No official release assets. |

### Suggested attribution blurb (metrics docs)

> Line-level Fraktur evaluation samples from Baiter Archiscribe corpus (CC BY 4.0), https://github.com/jbaiter/archiscribe-corpus; method described in Springmann et al., JLCL 33(1), 2018.

---

## 6. Clone size estimate (no bulk download performed)

| Estimate | Value | Source |
|----------|------:|--------|
| GitHub API `size` | 173 987 KiB ≈ **169.9 MiB** | GitHub repo metadata[1] |
| Sum of blob sizes (tree) | **178 215 478 bytes ≈ 178.2 MB** | recursive git tree API[1] |
| Release assets | **none** | releases API length 0[1] |
| Shallow clone expectation | ~**170–200 MB** disk order | derived (not executed full clone) |

Analysis used: GitHub API, `raw.githubusercontent.com` samples (JSON/TXT only), arXiv PDF text extract — **no multi‑GB fetch**.

---

## 7. Strengths / Caveats / Implications (one-screen)

### Strengths
- Ready **Fraktur line GT** (4 255 pairs), DTA-flavored diplomatic Unicode including **ſ**.  
- **Even 19th-c. coverage**, IA/Google-Books scan domain.  
- **CC BY 4.0**, small enough for CI (~170 MiB).  
- Documented method + ecosystem uptake (Springmann 2018; Calamari notes).

### Caveats
- **Frozen since 2018**; crowdsource site down; small vs GT4HistOCR.  
- Line-only (no pages/plates); ABBYY boxes; residual GT noise.  
- Attribution required; not Kurrent.

### UnbrokenOCR implications
- Best as **CER / long‑s microbench** and narrative support for Fraktur routing — not as sole trainer or plate corpus.  
- Aligns gates with German historical OCR norms (DTA glyphs, line CER).  
- Keep out of default fellow package payload; optional dev/eval clone only.

---

## Sources

[1] https://github.com/jbaiter/archiscribe-corpus — jbaiter/archiscribe-corpus (GitHub)  
[2] https://github.com/jbaiter/archiscribe — jbaiter/archiscribe transcription app  
[3] https://arxiv.org/pdf/1809.05501 — Springmann et al. 2018 GT4HistOCR (arXiv PDF)  
[4] https://jlcl.org/article/view/220 — JLCL 33(1) Ground Truth Fraktur/Latin  
[5] https://zenodo.org/records/1344132 — GT4HistOCR Zenodo record  
[6] https://creativecommons.org/licenses/by/4.0 — CC BY 4.0  
[7] http://www.deutschestextarchiv.de/doku/basisformat/transkription.html — DTA transcription guidelines  
[8] https://github.com/Calamari-OCR/calamari_models/issues/3 — Calamari fraktur models cite archiscribe  

**Ledger:** `research/sources/.ledger_02_archiscribe.json`  
**Evidence quotes:** attached for [1] (README size/goal) and [3] (directly usable; ABBYY segmentation note).
