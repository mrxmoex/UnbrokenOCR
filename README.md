# UnbrokenOCR

Fraktur = *(Knochen‑)Bruch* — broken script vs Antiqua.  
**UnbrokenOCR** = local PDF/OCR pipeline that doesn’t snap on blackletter.

**CLI:** `pdfx` · **Status:** WIP public · **Not** for hermes-agent upstream yet.

```bash
# quick
python3 pdfx.py book.pdf --inspect
python3 pdfx.py book.pdf --mode fraktur --pages 1-20 --out out.txt --search-sidecar
```

| Path | What |
|------|------|
| `pdfx.py` | main CLI |
| `dist/pdfx-hermes/` | shippable package tree |
| `dist/UnbrokenOCR-0.3.1.tar.gz` | tarball |
| `research/` | GT4HistOCR / archiscribe notes |
| `PROJECT.md` | project lock |
| `NO_UPSTREAM_PUSH.md` | no Nous/hermes-agent PR until bulletproof |

License: MIT wrapper — see `dist/pdfx-hermes/LICENSE` + `ATTRIBUTION.md`.  
Authors: **m (MrxHermesx)** + Hermes Agent fleet under human direction.
