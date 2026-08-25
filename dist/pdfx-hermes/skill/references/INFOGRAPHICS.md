# INFOGRAPHICS — plates, figures, and vision pages

How to handle **plates / Tafeln / figures** when a PDF is more picture than
text. Applies to technical books, lithograph plate blocks, scanned diagrams,
and “empty text layer but images present” pages.

This is a **workflow guide**. pdfx does not auto-caption every figure; it
helps you find plate zones, render them, OCR body citations, and hand hard
pages to vision.

---

## When a page is a plate zone

Treat a page as a **plate / infographic zone** when:

| Signal | Meaning |
|--------|---------|
| Text layer empty or near-empty | `chars` ≈ 0–40 on inspect |
| Images present | `images` ≥ 1 on that page |
| Body text elsewhere cites `Fig.` / `Taf.` / `Tafel` | Cross-ref map needed |
| Line art / lithograph | OCR of the plate itself is weak — expect bag-of-words only |

**Do not** index Google Books **watermark / brand** pages as content (front
matter splash, “Digitized by Google”, blank scan targets). Skip them in
indexes and search corpora.

---

## Workflow (general)

```
1. inspect          → kind, text_quality, plate_page_candidates
2. body OCR         → Fraktur/scan extract of prose (source of Fig/Taf refs)
3. render 200 dpi   → PNG dumps of candidate pages (plates are visual)
4. body Fig/Taf idx → grep / parse citations → topics per Tafel
5. vision_analyze   → hard pages (labels, roman numerals, scene captions)
6. plates_search    → local JSON index + small search CLI (pattern below)
```

### 1) Inspect — plate candidates

```bash
pdfx BOOK.pdf --inspect
# JSON includes:
#   text_quality, recommend
#   plate_page_candidates      # 1-based page numbers
#   plate_page_candidate_count
#   page_detail (first 8 pages sample: n, chars, images)
```

Filter candidates yourself:

```bash
pdfx BOOK.pdf --inspect > /tmp/insp.json

# list candidates
python3 - <<'PY'
import json
d=json.load(open("/tmp/insp.json"))
print("recommend:", d.get("recommend"))
print("candidates:", d.get("plate_page_candidates"))
print("count:", d.get("plate_page_candidate_count"))
for pg in d.get("page_detail") or []:
    print(f"  p{pg['n']}: chars={pg['chars']} images={pg['images']}")
PY
```

Heuristic inside inspect (honest limits):

- `images > 0` and `chars < 40` → strong plate candidate  
- else `images ≥ 1` and `chars < 120` → weak candidate  
- Capped list (first 80). **Not** a full layout classifier — confirm visually.

### 2) Body text first (Fig / Taf index)

Plates alone OCR poorly. **Body prose** carries `Fig. 3. Taf. XVII` style
citations. Run Fraktur (or scan) on the body range **before** trusting plate
OCR:

```bash
# example: body pages only
pdfx BOOK.pdf --mode fraktur --pages 1-200 --out extract/fraktur/body.txt

# optional searchable sidecar (long‑s → s)
python3 - <<'PY'
from pathlib import Path
p = Path("extract/fraktur/body.txt")
t = p.read_text(encoding="utf-8", errors="replace")
Path("extract/fraktur/body_search.txt").write_text(
    t.replace("\u017f", "s").replace("ſ", "s"), encoding="utf-8"
)
PY

# citation harvest
rg -n -i 'Taf(el)?\.?\s*[IVXLC0-9]+|Fig\.?\s*[0-9]' extract/fraktur/body_search.txt | head
```

Build a map: **Tafel roman/int → list of body snippets + topics**.

### 3) Render candidates @ 200 dpi

For plate blocks, **200 dpi** is usually enough for vision + light OCR and
keeps disk smaller than 300 dpi batch OCR:

```bash
mkdir -p extract/plates/render
# Poppler: -f/-l are 1-based inclusive; -r is DPI
pdftoppm -png -r 200 -f 116 -l 178 BOOK.pdf extract/plates/render/p
# → p-116.png … (naming depends on poppler version; normalize if needed)

# or via pdfx handwritten/render path for a short slice:
pdfx BOOK.pdf --mode handwritten --pages 116-120 --render-dir extract/plates/render
```

### 4) Vision on hard pages

Use Hermes `vision_analyze` on:

- Roman numeral headers (`Taf. XVII`)
- Figure callouts (`Fig. 3`, letter keys `a b c`)
- Work scenes where OCR is noise

Pair unclear glyphs with **Fraktur templates** (print labels only):

- Catalog: `skill/references/fraktur-templates/INDEX.md`
- Prefer labeled alphabet chart + period Mainzer sheet when reading
  blackletter captions on plates
- Templates are **reference-only**; default tarball ships INDEX, not JPGs

Prompt sketch:

```
Read any Tafel roman numeral and figure labels on this plate scan.
List visible tools/materials as short topic tags.
Ignore Google watermarks and library stamps.
```

### 5) `plates_search.py` pattern (local index)

Ship a **per-book** index next to renders (not inside pdfx core). Minimal
schema:

```json
{
  "book_id": "EXAMPLE",
  "plates_advertised": 34,
  "body_fraktur": "extract/fraktur/body.txt",
  "tafeln": [
    {
      "tafel": 25,
      "roman": "XXV",
      "primary_part2_page": 158,
      "primary_render": "extract/plates/render/p-158.png",
      "topics": ["Haken", "Seil", "Leiter", "Lenkhaken"],
      "body_snippets": [{"fig": "1", "context": "…"}],
      "vision_captions": ["…"]
    }
  ],
  "search_entries": []
}
```

Search CLI responsibilities (see worked example):

- Match topics / roman / weak plate OCR bag-of-words  
- Prefer `kind=tafel` over raw page hits  
- Optional `--body` grep of Fraktur sidecar  
- `--tafel XVII` detail + path to PNG  

Weak plate OCR is fine as **search spice**; **truth** = body snippets +
vision captions + page map.

---

## Mode header example (agent notes)

When writing extracts, stamp a short header so later sessions know the route:

```
# pdfx-extract
# source: BOOK.pdf
# mode: fraktur
# engine: ocrmypdf
# pages: 1-200
# dpi: n/a
# quality: inspect label=garbled → forced fraktur
# plates: candidates from inspect; renders @200dpi under extract/plates/render/
# notes: do not index Google watermark pages
```

---

## Anti-patterns

| Don't | Do instead |
|-------|------------|
| Trust plate OCR alone for craft terms | Body Fig/Taf index + vision |
| Index Google watermark / blank targets | Skip; mark `kind: frontmatter` |
| Feed Fraktur specimen JPGs into Kraken | Specimens are print QA only |
| Use 300 dpi for entire plate block overnight without need | 200 dpi for vision plates; 300 for quote-critical OCR |
| Assume `plate_page_candidates` is complete | Spot-check body “Tafeln” list vs candidates |

---

## Worked example paths (house-specific — examples only)

> **Not portable.** Paths below are an example house layout for the Dachdecker
> control corpus. Fellows should mirror the *pattern*, not the absolute paths.

Corpus: *Der vollkommene Dachdecker* (Matthaey), Google-style scan id
`AQKAAAAIAAJ` — used for gates; **not shipped** in the tarball.

Example house tree (illustrative):

```
Documents/papers/books/google/AQKAAAAIAAJ/
  parts/AQKAAAAIAAJ_pp187-366.pdf          # plate block ~p116–178 of part2
  extract/fraktur/full_book_fraktur.txt
  extract/fraktur/full_book_fraktur_search.txt   # ſ→s sidecar
  extract/plates/
    render/p-116.png …
    ocr/p-116.txt …
    plates_index.json
    plates_search.py
    PLATE_INDEX.md
    fraktur-templates/   # optional local mirror of specimens
```

Example commands (run from that book root if you have the corpus locally):

```bash
pdfx parts/AQKAAAAIAAJ_pp187-366.pdf --inspect
# read plate_page_candidates around the lithograph block

pdftoppm -png -r 200 -f 116 -l 178 \
  parts/AQKAAAAIAAJ_pp187-366.pdf extract/plates/render/p

python3 extract/plates/plates_search.py Schiefer Seil Ziegel Lenkhaken
python3 extract/plates/plates_search.py --tafel XXV
rg -n -i 'Lenkhaken|Fahrstuhl' extract/fraktur/full_book_fraktur_search.txt
```

High-value plate themes from that bakeoff (illustrative):

| Theme | Tafeln (approx.) |
|-------|------------------|
| Strohdeckung / First | I–IV |
| Ziegel / Pfannen | IX–XII, XVII |
| Schiefer | X + body |
| Lenkhaken / Fahrstuhl / Seil / Leiter | XXV–XXVII |

Gate methodology summary (no book bytes): `skill/references/CONTROL_GATES.md`.

---

## Related package docs

| Doc | Role |
|-----|------|
| `README.md` | Install, routes, edge cases |
| `DEPENDENCIES.md` | pdftoppm / tesseract / pymupdf |
| `ATTRIBUTION.md` | Credits; corpus not shipped |
| `skill/references/fraktur-templates/INDEX.md` | Glyph QA charts |
| `skill/references/CONTROL_GATES.md` | Fraktur engine defaults |

Version: pdfx-hermes **0.3.0**.
