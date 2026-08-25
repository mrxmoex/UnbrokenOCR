# SOURCE 3 — chreul/19th-century-fraktur-OCR

**Repo:** https://github.com/chreul/19th-century-fraktur-OCR  
**Owner:** Christian Reul (`chreul`) et al. (Würzburg / OCR-D lineage)  
**One-liner:** Frozen 2018 release of **Calamari + OCRopus mixed models** for German **19th-century Fraktur**, with a small codec-adaptation GT slice.  
**Analyzed:** 2026-08-25 · independent UnbrokenOCR source note  
**Default branch:** `master` · **last push:** 2018-10-10 · **created:** 2018-09-25 · stars/forks ~8/5  
**License:** MIT (Copyright 2018)[1][3]

---

## 1. What the repo is

Not an OCR application and not a full training pipeline. It is a **model zoo + adaptation sample set** that accompanies the DHd 2019 / arXiv paper *State of the Art Optical Character Recognition of 19th Century Fraktur Scripts using Open Source Engines* (Reul, Springmann, Wick, Puppe, 2018).[2][4][5]

README states purpose clearly: OCRopus/Calamari **mixed models** for recognizing (German) 19th century Fraktur; apply to **binary** line images; optional fine-tune from the shipped ≤50 lines/book GT.[2]

There is **no application code** in-tree (no `setup.py`, no predict scripts, no Dockerfile). Engines are external: **Calamari** and **OCRopus (ocropy)**.

---

## 2. Artifacts that ship

### 2.1 Layout

```
LICENSE                 # MIT
README.md               # short usage + bibtex
models/
  calamari/
    ensemble_best/      # 5 voters: 0..4.ckpt.{data,index,json,meta} + checkpoint
    single_best/        # 1 model: 0.ckpt.* + checkpoint
  ocropus/
    single_best.pyrnn.gz
data/
  ref_AS/               # 99 book folders (mostly *goog / bub_gb_* IDs)
  ref_BA/               # 37 dated literary works (1802–1898)
  ref_JZE/              # 8 sets (Breslau, Menzel, Kiel, Frapan, Köln, Gartenlaube, Munzinger, Peters)
```

Repo API size ~266 MB; **model blobs alone ~387 MB** (git tree sizes). Weights are real binary objects on `raw.githubusercontent.com` (HTTP 200, full `Content-Length`) — not broken Git-LFS pointers as of 2026-08-25.

### 2.2 Models (weights)

| Artifact | Format | Approx size | Role |
|----------|--------|-------------|------|
| `models/calamari/ensemble_best/{0-4}.ckpt.*` | Calamari **TF1-style** checkpoint quartet (`.data-00000-of-00001`, `.index`, `.meta`, `.json`) | ~5 × (24.3 MB data + 24.4 MB meta) | **Best quality** — 5-model voting ensemble[2] |
| `models/calamari/single_best/0.ckpt.*` | same | ~48.7 MB | Faster single model; README: slightly better than any one ensemble member[2] |
| `models/ocropus/single_best.pyrnn.gz` | OCRopus/clstm `pyrnn` | **~94.9 MB** | Shallow LSTM baseline for ocropy `ocropus-rpred` |

**Calamari network (from `single_best/0.ckpt.json`):** line height 48; CNN 40→pool→60→pool→**LSTM 200**; dropout 0.5; Adam; **101-class codec**; early-stop best accuracy ~0.9948 on their val split; training path leaked in JSON (`…/fraktur/models/single_bin_finalFromAllFromSynthFromPT`). Backend is the **2018 Calamari / TensorFlow 1.x** checkpoint layout (not modern SavedModel).

**Codec (actual JSON charset, 101 slots including blank + `\n`):** keeps **long s `ſ`**, `ß`, umlauts `äöüÄÖÜ`, accents `àèé`, `§«»`, double hyphen `⸗`, dashes, and combining e `ͤ`. Paper describes a **93-character design codec** with rules: keep long s; resolve ligatures except ß; regularize umlauts/quotes/hyphens/r-rotunda; **map capital I and J → J**.[5] Sample GT confirms diplomatic long-s: e.g. `zuſammengefloſſen`, `Reſtauration`, `daſelbſt`.

### 2.3 Data (not full training corpus)

- **~5,681 line pairs** (`*.png` + `*.gt.txt`), **144 books/sources**, **max 50 lines per book** (observed min/avg/max ≈ 3 / 39.5 / 50).[1][2]
- Purpose: **codec / transcription-guideline adaptation** and warm-start fine-tune (`calamari --weights` / `ocropus --load`), **not** full retrain.[2]
- Corpora labels in tree:
  - **ref_AS** — large Archiscribe-style / Google Books ID set (99)
  - **ref_BA** — literary Fraktur 1802–1898 (37)
  - **ref_JZE** — material aligned with jze Fraktur OCRopus work (8)[14]
- Full training data for the paper models is **GT4HistOCR** (+ related Fraktur19 sources), not duplicated here: **313,173** line pairs, CC-BY 4.0 on Zenodo.[6][7][13]

### 2.4 Code / scripts

**None.** Inference and training require installing Calamari or ocropy yourself.

### 2.5 License

MIT — free reuse of weights and sample GT in UnbrokenOCR-style stacks, with copyright notice retention.[3]

---

## 3. Papers linked

| Ref | Citation | Role |
|-----|----------|------|
| [1] in README | Reul et al. 2018 — arXiv:**1810.03436** — DHd 2019 submission | Evaluation + claim that these models beat ABBYY on 19th-c Fraktur mixed recognition[4][5] |
| [2] in README | Springmann et al. 2018 — arXiv:**1809.05501** / JLCL 33(1) | **GT4HistOCR** description; full training data download pointer[6][7][13] |

### Headline results (1810.03436)[4][5]

- Task: **mixed models** (no book-specific train) on unseen 19th-c books, journals, dictionary — **20 eval sets**, lines pre-segmented (ABBYY lines used for fair engine compare).
- Engines compared: **ABBYY** (commercial Fraktur), **Tesseract**, **OCRopus**, **Calamari** (self-trained mixed).
- Real-data mixed training ≫ mostly-synthetic Fraktur models (e.g. FRK vs OCRo discussion in paper).
- **Calamari voting** best: average **CER &lt; 1%**; ~**70%** relative CER reduction vs ABBYY without voting, ~**78%** with voting (paper averages over 20 sets).[4][5]
- CER still **highly variable** by scan/font (Calamari voted range cited ~0.01%–4.75%; ABBYY ~0.01%–26.54%).
- Dominant residual errors: **whitespace** merge/split (historical word spacing).
- Training recipe (Table 1 narrative): multi-century pretrain → synthetic Fraktur fonts → real 19th-c Fraktur → **final refine ≤50 lines/book** to fight imbalance (some books 10k+ GT lines).[5]

Related successor context (not this repo): Calamari-OCR/`calamari_models` ships **`fraktur_19th_century`** (and `fraktur_historical*`) as a maintained ensemble; chreul notes training from GT4HistOCR DTA19 + Archiscribe + jze data, pretrain + DA + 50-line cap + 3px pad.[8][9]

---

## 4. Relation to Tesseract / OCRopus / Calamari / others

| Engine | Relation to this source |
|--------|-------------------------|
| **Calamari** | **Primary.** CNN-LSTM + optional voting; weights in-repo are Calamari 2018 checkpoints.[1][2][10] |
| **OCRopus / ocropy** | Second-class citizen: one `pyrnn.gz`; paper baseline. Upstream **ocropus/ocropy is archived** (last push ~2021-05).[12] Python 2 / clstm era. |
| **Tesseract** | **Compared in paper only** — no `.traineddata` here. Tesseract 4 LSTM Fraktur models of that era were largely **synthetic-font** trained; paper argues real-data Calamari mixed models win.[5][7] |
| **ABBYY** | Commercial baseline beaten on average CER in paper; also used as **line segmenter** for eval fairness.[5] |
| **Kraken** | Unrelated lineage (not used here). |
| **OCR-D / calamari_models** | Institutional successor path: modern SavedModel ensembles including `fraktur_19th_century`.[8][11] |

**Pipeline shape:** line-image → recognizer. **Page layout / deskew / line find are out of scope.** Paper and calamari_models docs assume **OCRopus `nlbin`-style binary** inputs for best match.[2][8]

---

## 5. Strengths for 19th-c Fraktur (Dachdecker-era print)

Relevant to UnbrokenOCR control material (*Der vollkommene Dachdecker* / Matthaey-class mid–late 19th-c craft print):

1. **Domain match:** Explicitly **German 19th-century Fraktur mixed model**, not generic blackletter or early modern only.[1][4]
2. **Measured SOTA (2018 open source):** CER often well under 1% on clean lines; large average gain over ABBYY/Tesseract/OCRopus of that generation.[4][5]
3. **Real-data training** (GT4HistOCR DTA19-heavy + other Fraktur19), not synthetic-only — better type-realism (long s, ch, etc.).[5][7]
4. **Diplomatic codec:** long **ſ**, ß, umlauts, historical punctuation — aligns with UnbrokenOCR “keep canonical long‑s + ſ→s sidecar” policy.
5. **Voting ensemble** available when quality &gt; speed.
6. **Adaptation path:** ≤50 lines/book sample GT + warm-start flags for house transcription conventions.[2]
7. **MIT weights**, downloadable offline without cloud API.[1][3]
8. **Binary-print focus** matches many Google Books / library scans after binarization (with the usual nlbin caveats).

---

## 6. Caveats (bitrot, versions, reproducibility in 2026)

| Risk | Detail |
|------|--------|
| **Frozen 2018** | Only 3 commits; no maintenance since 2018-10-10.[1] |
| **No inference code** | Must bring your own Calamari/ocropy + line segmentation + binarization. |
| **Calamari checkpoint generation gap** | Shipped files are **TF1 `.ckpt` + sidecar `.json`** (old Calamari). Current Calamari **v2.3.x** (2024) uses **TensorFlow SavedModel**, TF≤2.15, checkpoint format version bumps; GPL-3 effective for modern Calamari.[10][11] **Do not expect `pip install calamari-ocr` (latest) to load these weights without a converter or a pinned old environment.** |
| **Prefer successor weights for greenfield** | `Calamari-OCR/calamari_models` → `fraktur_19th_century/` (5× SavedModel voters, modern `version` field) is the 2026-practical twin of this research release.[8][9] |
| **OCRopus path is bitrot-hard** | `ocropy` archived; Python 2 / native clstm; `pyrnn.gz` not useful in UnbrokenOCR’s current Python 3 stack without a museum venv.[12] |
| **Binary-only training** | Greyscale or colour lines without matching binarization **degrade** results; README insists on binary.[2] |
| **Line-level only** | Needs a line segmenter (ocropy, kraken, ABBYY, ocrmypdf/tesseract layout, custom). Wrong line crops destroy CER even with perfect weights. |
| **Eval lines were “well segmented”** | Paper CERs are **not** end-to-end page CER including layout failure.[5] |
| **Codec quirks** | I/J collapse to **J**; ligatures mostly expanded; may disagree with other GT guidelines — fine-tune sample data exists for a reason.[5] |
| **No language model / dictionary** | Paper notes ABBYY’s post-processing advantage; Calamari/OCRopus here are pure optical.[5] |
| **Whitespace errors dominate** | Craft manuals with irregular spacing, tables, and Tafeln will still need post-rules / gates.[5] |
| **Plates / figures** | Out of scope — same as UnbrokenOCR’s separate plate path. |
| **Reproducibility of training** | Full train needs GT4HistOCR + multi-stage recipe; this repo alone cannot reproduce training from scratch.[2][13] |
| **GPU/TF pin hell** | Old Calamari stacks want historical TF1 + CUDA; painful on 2026 Fedora without containers. |
| **Not Tesseract-drop-in** | Cannot point `TESSDATA_PREFIX` / ocrmypdf at these files. |

### Weights availability (2026 check)

- GitHub raw downloads for `0.ckpt.data-00000-of-00001` (~24 345 544 bytes) and `single_best.pyrnn.gz` (~94 871 323 bytes) **succeed**.
- Full clone is large (~hundreds of MB) but straightforward.
- No auth / cloud license server.

---

## 7. Can UnbrokenOCR call any of this today without cloud?

### Short answer

| Path | Offline? | Practical for UnbrokenOCR 0.3 / `pdfx` today? |
|------|----------|-----------------------------------------------|
| Use **these** 2018 Calamari `.ckpt` as-is | Yes, if weights + old Calamari env local | **No as default** — format/env mismatch with house stack (ocrmypdf/tesseract + optional kraken) |
| Use **OCRopus `pyrnn`** | Yes in theory | **No** — archived Python 2 stack |
| Use **modern `calamari_models/fraktur_19th_century`** (same research line) | Yes | **Possible optional engine** — still needs Calamari 2.x + line bin pipeline; not wired in `pdfx` today |
| Sample `data/**` GT | Yes | Yes — useful for **quality gates / codec tests / fine-tune experiments**, not production OCR |
| Paper numbers as acceptance priors | N/A | Yes — cite as optimistic **line-CER** ceiling on clean 19th-c Fraktur |

### House stack reality (UnbrokenOCR)

- Fraktur default: **ocrmypdf** (Tesseract), inspect/gates, batch windows; Kurrent via **kraken**; no Calamari dependency in `STACK.md` / package policy (no huge weights in fellow tarball).
- Therefore: this source is **research / optional backend / GT reference**, not a one-line `pdfx --engine chreul` today.

### If UnbrokenOCR ever wires Calamari (local-only design sketch)

1. Prefer **`calamari_models` `fraktur_19th_century`** (SavedModel) over 2018 chreul ckpts unless a validated converter exists.[8][11]
2. Pipeline: page → deskew → **binarize (nlbin-like)** → line seg → `calamari-predict` ensemble → join lines → existing ſ→s sidecar + Gates A/B/C.
3. Keep behind optional extra / separate venv; **do not** ship 300+ MB weights in the public fellow tarball (package policy).
4. Benchmark on Dachdecker control pages against current ocrmypdf Fraktur before any default switch; paper CERs are line-oracle optimistic.
5. MIT on chreul weights is package-friendly; confirm **Calamari engine** license (modern GPL-3) separately if bundling the engine.[11]

### Direct answer to “call any of this without cloud?”

- **Download weights + run offline:** **yes** (GitHub/Zenodo).
- **Call from current `pdfx` with zero new deps:** **no**.
- **Closest zero-cloud value today:** (a) cite performance priors, (b) use sample GT for metrics/harness, (c) optional future Calamari backend using **successor** `fraktur_19th_century` models rather than fighting TF1 checkpoints.

---

## 8. Strengths (summary)

- Domain-true **19th-c German Fraktur mixed** models with published sub-1% average line CER and large gains over 2018 ABBYY/Tesseract/OCRopus.[4][5]
- Ships **ensemble + single** Calamari and OCRopus weights under **MIT**, still downloadable in 2026.[1][2][3]
- Codec preserves **ſ** and period punctuation; adaptation GT included.[2][5]
- Anchored in **GT4HistOCR / DTA19** real print, not synthetic-only.[6][7][13]
- Clear binary-line operating point and fine-tune story.[2]

## 9. Caveats (summary)

- **2018 freeze**; no app code; **old Calamari TF1 checkpoints** vs 2024–2026 Calamari SavedModel.[1][11]
- **OCRopus path effectively dead** for modern Python.[12]
- Line-segmented binary eval ≠ full PDF product CER; whitespace and layout still hurt.[5]
- Not integrated with UnbrokenOCR’s ocrmypdf/kraken routes; optional only.

## 10. UnbrokenOCR implications

1. **Do not** make chreul 2018 ckpts the default Fraktur engine without a maintained Calamari runtime and line pipeline.
2. **Do** treat Reul et al. 2018 + this repo as the canonical citation that **open mixed Fraktur models can beat commercial engines on 19th-c print** when trained on real GT.[4][5]
3. **Do** keep long‑s-aware evaluation; this codec is a reference for gate metrics.
4. **If** adding a Calamari experiment track: target `calamari_models/fraktur_19th_century` first; use chreul repo as historical artifact + sample `data/` only.[8]
5. **Dachdecker-era** body text is in-domain; **Tafeln/plates** still need the separate plate/vision path.
6. Package/ATTRIBUTION: MIT notice if redistributing weights; prefer linking GitHub over bundling.

---

## 11. Cite

Primary:

- Reul, C., Springmann, U., Wick, C., & Puppe, F. (2018). *State of the Art Optical Character Recognition of 19th Century Fraktur Scripts using Open Source Engines.* arXiv:1810.03436. https://arxiv.org/abs/1810.03436 [4][5]
- Springmann, U., Reul, C., Dipper, S., & Baiter, J. (2018). *Ground Truth for training OCR engines on historical documents in German Fraktur and Early Modern Latin.* arXiv:1809.05501 / JLCL 33(1). https://arxiv.org/abs/1809.05501 [6][7]
- Reul, C. (2018). *19th-century-fraktur-OCR* (GitHub, MIT). https://github.com/chreul/19th-century-fraktur-OCR [1][2][3]

Related:

- GT4HistOCR — Zenodo https://zenodo.org/records/1344132 [13]
- Calamari — https://github.com/Calamari-OCR/calamari [10]
- calamari_models (incl. `fraktur_19th_century`) — https://github.com/Calamari-OCR/calamari_models [8][9]
- ocropy (archived) — https://github.com/ocropus/ocropy [12]
- jze Fraktur OCRopus model — https://github.com/jze/ocropus-model_fraktur [14]

---

## Sources

[1] https://github.com/chreul/19th-century-fraktur-OCR  
[2] https://raw.githubusercontent.com/chreul/19th-century-fraktur-OCR/master/README.md  
[3] https://raw.githubusercontent.com/chreul/19th-century-fraktur-OCR/master/LICENSE  
[4] https://arxiv.org/abs/1810.03436  
[5] https://arxiv.org/pdf/1810.03436.pdf  
[6] https://arxiv.org/abs/1809.05501  
[7] https://arxiv.org/pdf/1809.05501.pdf  
[8] https://github.com/Calamari-OCR/calamari_models  
[9] https://github.com/Calamari-OCR/calamari_models/issues/3  
[10] https://github.com/Calamari-OCR/calamari  
[11] https://github.com/Calamari-OCR/calamari/releases  
[12] https://github.com/ocropus/ocropy  
[13] https://zenodo.org/records/1344132  
[14] https://github.com/jze/ocropus-model_fraktur  

---

*Ledger: `/home/mrxmoex/src/pdf-extract/research/sources/.ledger_03_chreul.json`*  
*Local paper dumps also under `research/raw/1810.03436.*`, `research/raw/chreul-README.md`.*
