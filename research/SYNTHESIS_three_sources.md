# UnbrokenOCR — three-source synthesis (2018 Fraktur research cluster)

**Date:** 2026-08-25 · **Steering:** CONTROL  
**Method:** three independent leaf agents + CONTROL fetch; agent 1 (paper) truncated — CONTROL note stands for 01; agents 2–3 delivered deep notes that supersede first-pass depth on GitHub sources.

| # | Source | Role | Note file |
|---|--------|------|-----------|
| 1 | [arXiv:1809.05501](https://arxiv.org/abs/1809.05501) | **GT4HistOCR** paper + 313k line GT (CC-BY-4.0) | `sources/01_arxiv_1809.05501.md` |
| 2 | [jbaiter/archiscribe-corpus](https://github.com/jbaiter/archiscribe-corpus) | Crowd **4 255** 19th‑c. Fraktur lines (CC-BY-4.0) | `sources/02_archiscribe_corpus.md` (agent) |
| 3 | [chreul/19th-century-fraktur-OCR](https://github.com/chreul/19th-century-fraktur-OCR) | Calamari/OCRopus **mixed models** + ~5.7k adapt lines (MIT) | `sources/03_chreul_19th_century_fraktur_OCR.md` (agent) |

**Companion paper (to 3):** [arXiv:1810.03436](https://arxiv.org/abs/1810.03436) — SOTA open engines on 19th‑c. Fraktur.

**People:** Springmann, Reul, Dipper, Baiter, Wick, Puppe — one open historical OCR cluster (2017–2018).

**Etymology (user):** Fraktur = *(Knochen‑)Bruch* / broken script vs Antiqua — not “looks messy.”

---

## One cluster, three layers

```
GT4HistOCR (1) ──full train GT──► Calamari mixed models (3) + paper 1810.03436
       │                                    ▲
       │                            also trained with /
       ▼                            evaluated near
Archiscribe (2) ──smaller 19th‑c. line GT──┘
```

Archiscribe is **alongside** GT4HistOCR (not a Zenodo subset); paper treats it as already line-aligned trainer/eval material. chreul `data/ref_AS` looks Archiscribe-adjacent; full train is GT4HistOCR-scale.

---

## Compare

| Dimension | (1) GT4HistOCR | (2) Archiscribe | (3) chreul models |
|-----------|----------------|-----------------|-------------------|
| Kind | Dataset paper + bulk GT | Line corpus repo | Model zoo (no app code) |
| Scale | **313 173** lines | **4 255** lines / 112 works | ~**387 MB** weights + ~**5 681** adapt pairs / 144 books |
| Era | 15th–19th c. + EM Latin | **19th c. only** | **19th c. mixed** |
| Script | Fraktur print (+ Latin) | Fraktur print **not Kurrent** | Fraktur print |
| License | CC-BY-4.0 | CC-BY-4.0 | MIT (weights); train data still CC-BY lineage |
| Layout GT | No (lines only) | No | No |
| Plates | No | No | No |
| Last activity | 2018 paper | 2018-12-31 | 2018-10-10 |
| Clone cost | Zenodo bulk (heavy) | ~**170–180 MB** git | Models dominate (~387 MB) |
| 2026 callability | GT yes | GT yes | **Hard** — TF1 `.ckpt` vs modern Calamari SavedModel; ocropy archived |

### Agent-2 extras (Archiscribe)

- Layout: `transcriptions/<year>/<ia_id>_{line}.png|.txt` + per-work JSON (IIIF)  
- Diplomatic Unicode: `ſ`, `⸗`, historical umlauts (`oͤ`) — DTA-simplified rules  
- Tool used IA **ABBYY line boxes** + IIIF; **archiscribe.jbaiter.de → 404** now  
- Fraktur volume heuristic: look for Antiqua-OCR mangling of **ſt** in *ist*  
- Hold out by **work/year**, not random lines  
- Perfect for UnbrokenOCR **CER + long‑s microbench** next to craft-term metrics  

### Agent-3 extras (chreul)

- Ensemble 5 + single Calamari + OCRopus `pyrnn.gz`; **no predict scripts in repo**  
- Codec keeps **ſ**, ß, umlauts, `⸗`; paper notes **I/J → J** regularization  
- Paper: Calamari voted avg **CER &lt;1%**, ~70–78% relative CER cut vs ABBYY on **20** pre-segmented eval sets; residual errors often **whitespace**  
- Real-data mixed ≫ synthetic-only Fraktur models of that era  
- **Binary** line input (nlbin-style); gray pdftoppm alone is unfair  
- Successor path named in literature: modern **`calamari_models` / `fraktur_19th_century`** (verify before adopting) — prefer over raw 2018 ckpt if we ever add Calamari  
- **Cannot** plug into current `pdfx` (ocrmypdf/tess/kraken) without a new engine track  

---

## Shared strengths → UnbrokenOCR

1. Line-image GT is the right **eval/train** currency  
2. Mixed real-data 19th‑c. models beat book-only / synthetic-only (their evidence)  
3. Diplomatic long‑s policy matches our **canonical extract + ſ→s search sidecar**  
4. Open licenses fit a later public release  
5. Confirms: **engine quality** is solvable; **product** is still routing, garbage-layer detection, plates  

---

## Shared caveats

1. Eight-year **bitrot** on engines/checkpoints  
2. None implement inspect → quality gate → plate index → Google digital trap  
3. Paper CER ≠ dirty Google Books + watermarks + lithograph Tafeln  
4. Line segmentation often **assumed** (ABBYY boxes in their eval) — we still own page→line  
5. Dormant sites/repos — no support contract  

---

## Position (locked for now)

| Layer | UnbrokenOCR 0.3.0 | From this research |
|-------|-------------------|--------------------|
| Detect / route / plates | **Differentiator — keep** | Not in these sources |
| Default Fraktur engine | ocrmypdf + tess `frk` (Gate B) | Stay until a Calamari spike **beats** it on Dachdecker + archiscribe CER |
| Eval | craft stems | **Add** CER on archiscribe holdout (~180 MB clone) |
| Optional engine | — | Spike modern `fraktur_19th_century` **or** legacy chreul only if env cost is low |
| Citations | — | ATTRIBUTION research subsection when packaging next |

**Verdict:** Validate engine/GT science; **do not** rewrite the product around 2018 weights. No hermes upstream push.

---

## Next experiments (when inspired)

1. Clone archiscribe-corpus → CER harness vs `pdfx --mode fraktur --engine images` on line PNGs  
2. Optional binarize flag for fair Calamari tests  
3. Cite 1809.05501 / 1810.03436 / both GitHubs in package ATTRIBUTION  
4. Only if CER gap is large: Calamari plugin design (modern models first)

## Raw

`research/raw/` — ar5iv HTML, READMEs  
