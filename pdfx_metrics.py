#!/usr/bin/env python3
"""Craft-term + Fraktur diplomatic metrics for an extract file."""
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


def analyze(text: str, terms: list[str]) -> dict:
    counts = {t: len(re.findall(re.escape(t), text, re.I)) for t in terms}
    # also count long-s variants of craft stems if plain miss (e.g. Schiefer rare with ſ)
    letters = len(re.findall(r"[A-Za-zÄÖÜäöüßſ]", text))
    nonspace = len(re.findall(r"\S", text)) or 1
    long_s = text.count("ſ")
    # whitespace merge proxy: very long tokens
    tokens = re.findall(r"\S+", text)
    long_tok = sum(1 for t in tokens if len(t) >= 24)
    return {
        "chars": len(text),
        "letter_ratio": round(letters / nonspace, 3),
        "long_s_count": long_s,
        "long_s_per_1k_letters": round(1000.0 * long_s / max(1, letters), 2),
        "soft_hyphen_count": text.count("⸗") + text.count("\u00ad"),
        "long_token_ge24": long_tok,
        "craft_counts": counts,
        "craft_distinct": sum(1 for v in counts.values() if v > 0),
        "craft_total": sum(counts.values()),
        "diplomatic_policy": "keep_long_s_in_canonical_extract; use pdfx_normalize for search sidecar",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    text = Path(args.path).read_text(encoding="utf-8", errors="replace")
    obj = {"path": str(args.path), **analyze(text, DEFAULT_TERMS)}
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        print(
            f"{args.path}: chars={obj['chars']} craft_distinct={obj['craft_distinct']} "
            f"total={obj['craft_total']} ſ={obj['long_s_count']} "
            f"ſ/1k={obj['long_s_per_1k_letters']}"
        )
        for k, v in sorted(obj["craft_counts"].items(), key=lambda kv: -kv[1]):
            if v:
                print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
