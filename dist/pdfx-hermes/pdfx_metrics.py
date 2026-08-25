#!/usr/bin/env python3
"""Craft-term + rough quality metrics for a Fraktur extract file."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_TERMS = [
    "Dach",
    "Schiefer",
    "Ziegel",
    "Latte",
    "Matthaey",
    "Blech",
    "Stroh",
    "Bauherr",
    "Seil",
    "Leiter",
    "Fahrstuhl",
    "Lenkhaken",
    "Vorwort",
    "Thurm",
    "Forst",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    text = Path(args.path).read_text(encoding="utf-8", errors="replace")
    counts = {t: len(re.findall(re.escape(t), text, re.I)) for t in DEFAULT_TERMS}
    letters = len(re.findall(r"[A-Za-zÄÖÜäöüßſ]", text))
    nonspace = len(re.findall(r"\S", text)) or 1
    long_s = text.count("ſ")
    obj = {
        "path": str(args.path),
        "chars": len(text),
        "letter_ratio": round(letters / nonspace, 3),
        "long_s_count": long_s,
        "craft_counts": counts,
        "craft_distinct": sum(1 for v in counts.values() if v > 0),
        "craft_total": sum(counts.values()),
    }
    if args.json:
        print(json.dumps(obj, indent=2))
    else:
        print(f"{args.path}: chars={obj['chars']} craft_distinct={obj['craft_distinct']} total={obj['craft_total']} ſ={long_s}")
        for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
            if v:
                print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
