# Strengths to steal → UnbrokenOCR adoption

From 2018 open Fraktur cluster (GT4HistOCR · Archiscribe · chreul/Calamari paper).  
Only items that **bulletproof or enhance** the product are adopted. Speculative engine swaps stay optional.

| # | Strength (research) | Bulletproof / enhance? | Adoption (0.3.1) | Skip reason if any |
|---|---------------------|------------------------|------------------|--------------------|
| 1 | **Line-image GT** is the right eval currency | **Yes** — stops lying with page-level vibes | `pdfx_cer.py` — CER on PNG+TXT pairs; hold out by work/year (docstring) | Full GT4HistOCR download not required for product |
| 2 | **Mixed real-data** models beat synthetic-only | Indirect | Keep Gate B default; optional future Calamari spike only if CER harness shows gap | 2018 TF1 weights not default |
| 3 | **Diplomatic long‑s** + separate search fold | **Yes** — matches house Dachdecker sidecar; prevents lost recall | `pdfx_normalize.py`; `pdfx --search-sidecar`; metrics `long_s_*` | |
| 4 | **Transcription rules ≠ linguistics** | **Yes** — docs + policy string in metrics | STRENGTHS + skill note; canonical extract keeps ſ | |
| 5 | Open **CC-BY / MIT** citation culture | **Yes** — public path hygiene | `ATTRIBUTION.md` research cluster section | |
| 6 | Archiscribe **ſt / ist** Fraktur heuristic | **Yes** — inspect signal | `inspect.fraktur_signals` (long_s, st clusters, mangled_st, likely_fraktur_print) | |
| 7 | Paper CER &lt;1% with Calamari | Not yet | Track only — needs modern model + binarize + line seg | Bitrot / ops cost |
| 8 | Binary line input for their models | Later | Document in SYNTHESIS; no forced binarize on default ocrmypdf path | Default path stays ops-simple |
| 9 | ABBYY line boxes for fair engine compare | N/A product | CER harness assumes pre-cropped lines (archiscribe) | We still own page→line via ocrmypdf |
| 10 | Plates / Google garbage trap | **Already ours** | UnbrokenOCR differentiator — research cluster lacks this | |

## Product rules locked by this pass

1. Canonical library text: **keep ſ** when OCR emits it.  
2. Always offer **search sidecar** (ſ→s) for grep/index.  
3. **Inspect** exposes `fraktur_signals` + plates + quality (one JSON brain).  
4. **Eval**: craft metrics **and** line CER when GT pairs exist.  
5. Default engine remains **ocrmypdf + frk** until CER bakeoff dethrones it.  
6. No hermes upstream until bulletproof.

## Version

UnbrokenOCR / pdfx **0.3.1** — strengths adoption pass.
