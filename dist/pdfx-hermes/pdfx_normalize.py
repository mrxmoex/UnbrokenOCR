#!/usr/bin/env python3
"""Diplomatic Fraktur extract helpers: keep canonical long‑s, emit search sidecar.

Policy (GT4HistOCR / Archiscribe / UnbrokenOCR):
  - Canonical library extract KEEPS ſ (diplomatic)
  - Search/grep sidecar folds ſ→s (and light hyphen normalizations)
  - Never index garbled Google digital layers as the library text

Usage:
  pdfx_normalize.py extract.txt                  # writes extract.search.txt
  pdfx_normalize.py extract.txt -o out.search.txt
  pdfx_normalize.py extract.txt --stats
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def fold_for_search(text: str) -> str:
    # long s → s (primary)
    t = text.replace("ſ", "s").replace("ſ".upper() if False else "ſ", "s")
    # soft hyphen / double hyphen used as line join in diplomatic GT
    t = t.replace("⸗", "-").replace("\u00ad", "")
    return t


def stats(text: str) -> dict:
    letters = len(re.findall(r"[A-Za-zÄÖÜäöüßſ]", text))
    return {
        "chars": len(text),
        "long_s": text.count("ſ"),
        "soft_hyphen": text.count("⸗") + text.count("\u00ad"),
        "long_s_per_1k_letters": round(1000.0 * text.count("ſ") / max(1, letters), 2),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Fraktur search sidecar (ſ→s)")
    ap.add_argument("path", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=None)
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    p = args.path.expanduser().resolve()
    if not p.is_file():
        raise SystemExit(f"missing: {p}")
    raw = p.read_text(encoding="utf-8", errors="replace")
    st = stats(raw)
    folded = fold_for_search(raw)
    if args.stats and not args.out:
        print(json.dumps(st, indent=2) if args.json else st)
        return
    out = args.out
    if out is None:
        # foo.txt → foo.search.txt ; foo_fraktur.txt → foo_fraktur.search.txt
        out = p.with_name(p.stem + ".search" + p.suffix)
    out = out.expanduser().resolve()
    out.write_text(folded, encoding="utf-8")
    meta = {**st, "out": str(out), "folded_chars": len(folded)}
    if args.json:
        print(json.dumps(meta, indent=2))
    else:
        print(f"wrote {out} (ſ={st['long_s']} → search fold)")


if __name__ == "__main__":
    main()
