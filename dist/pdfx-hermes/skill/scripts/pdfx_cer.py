#!/usr/bin/env python3
"""Line-level CER against ground-truth pairs (Archiscribe / GT4HistOCR style).

UnbrokenOCR strength-to-steal: line-image GT is the right eval currency
(Springmann et al. 2018; archiscribe-corpus). Hold out by work/year, not
only random lines.

Layouts supported:
  - Archiscribe:  stem.png + stem.txt  (or .gt.txt)
  - OCRopus-ish:  stem.png + stem.gt.txt
  - Dir of pairs; optional --hyp-dir of OCR hypotheses named like stems.txt

Examples:
  pdfx_cer.py /path/to/archiscribe/transcriptions/1833 --limit 50
  pdfx_cer.py pairs/ --hyp-dir ocr_out/ --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    # two-row DP
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            ins, delete, sub = cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def normalize_diplomatic(s: str, fold_long_s: bool) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n").strip()
    # strip trailing newline only; keep internal spaces (whitespace is a real error mode)
    if fold_long_s:
        s = s.replace("ſ", "s")
    return s


def find_pairs(root: Path) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    if root.is_file():
        return pairs
    pngs = sorted(root.rglob("*.png"))
    for png in pngs:
        stem = png.with_suffix("")
        for cand in (stem.with_suffix(".gt.txt"), stem.with_suffix(".txt"), Path(str(stem) + ".gt.txt")):
            if cand.is_file():
                pairs.append((png, cand))
                break
    return pairs


def main() -> None:
    ap = argparse.ArgumentParser(description="CER on line GT pairs (UnbrokenOCR eval)")
    ap.add_argument("gt_root", type=Path, help="Dir with line PNG+TXT pairs (or work year folder)")
    ap.add_argument("--hyp-dir", type=Path, default=None, help="OCR hypotheses: same stems as .txt")
    ap.add_argument("--hyp-suffix", default=".txt", help="Hypothesis file suffix (default .txt)")
    ap.add_argument("--fold-long-s", action="store_true", help="Secondary score with ſ→s on both sides")
    ap.add_argument("--limit", type=int, default=0, help="Max pairs (0=all); useful smoke")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = args.gt_root.expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    pairs = find_pairs(root)
    if not pairs:
        raise SystemExit(f"no png+txt pairs under {root}")
    if args.limit and args.limit > 0:
        pairs = pairs[: args.limit]

    rows = []
    total_edits = 0
    total_refs = 0
    total_edits_fold = 0
    missing_hyp = 0

    for png, gt_path in pairs:
        ref = normalize_diplomatic(gt_path.read_text(encoding="utf-8", errors="replace"), False)
        hyp_path = None
        if args.hyp_dir:
            hyp_path = args.hyp_dir.expanduser().resolve() / (png.stem + args.hyp_suffix)
            if not hyp_path.is_file():
                # try relative stem path under hyp-dir
                rel = png.relative_to(root)
                hyp_path = args.hyp_dir.expanduser().resolve() / rel.with_suffix(args.hyp_suffix)
            if not hyp_path.is_file():
                missing_hyp += 1
                continue
            hyp = normalize_diplomatic(hyp_path.read_text(encoding="utf-8", errors="replace"), False)
        else:
            # self-CER sanity: ref vs ref → 0; still useful to inventory
            hyp = ref

        ed = levenshtein(ref, hyp)
        n = max(1, len(ref))
        total_edits += ed
        total_refs += len(ref)
        row = {
            "image": str(png),
            "gt": str(gt_path),
            "ref_len": len(ref),
            "edits": ed,
            "cer": round(ed / n, 4),
        }
        if args.fold_long_s:
            rf = normalize_diplomatic(ref, True)
            hf = normalize_diplomatic(hyp, True)
            ef = levenshtein(rf, hf)
            total_edits_fold += ef
            row["cer_fold_long_s"] = round(ef / max(1, len(rf)), 4)
        rows.append(row)

    if not rows:
        raise SystemExit(f"no scored pairs (missing_hyp={missing_hyp})")

    micro_cer = total_edits / max(1, total_refs)
    out = {
        "gt_root": str(root),
        "pairs_found": len(pairs),
        "pairs_scored": len(rows),
        "missing_hyp": missing_hyp,
        "chars_ref": total_refs,
        "edits": total_edits,
        "cer_micro": round(micro_cer, 6),
        "cer_macro_mean": round(sum(r["cer"] for r in rows) / len(rows), 6),
        "note": "Hold out by work/year when splitting train/eval (archiscribe practice).",
    }
    if args.fold_long_s:
        out["cer_micro_fold_long_s"] = round(total_edits_fold / max(1, total_refs), 6)
    if args.json:
        out["per_line"] = rows[:200]
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(
            f"CER micro={out['cer_micro']:.4f} macro={out['cer_macro_mean']:.4f} "
            f"lines={out['pairs_scored']}/{out['pairs_found']} missing_hyp={missing_hyp} "
            f"chars={total_refs}"
        )
        if args.fold_long_s:
            print(f"CER micro (ſ→s both)={out['cer_micro_fold_long_s']:.4f}")
        worst = sorted(rows, key=lambda r: -r["cer"])[:5]
        if worst and (args.hyp_dir or True):
            print("worst lines:")
            for r in worst:
                if r["cer"] > 0 or args.hyp_dir:
                    print(f"  {r['cer']:.3f}  {Path(r['image']).name}")


if __name__ == "__main__":
    main()
