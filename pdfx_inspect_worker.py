
import json, sys, re
import pymupdf
p = sys.argv[1]
doc = pymupdf.open(p)
pages = []
text_chars = 0
# gather densest pages in first 30 (skip blank covers)
ranked = []
for i, page in enumerate(doc):
    t = page.get_text("text") or ""
    c = len(t.strip())
    text_chars += c
    pages.append({"n": i + 1, "chars": c, "images": len(page.get_images())})
    if i < 30 and c > 80:
        ranked.append((c, i, t))
ranked.sort(reverse=True)
sample_parts = [t[:1500] for _, _, t in ranked[:4]]
sample = "\n".join(sample_parts)
letters = len(re.findall(r"[A-Za-zÄÖÜäöüßſ]", sample))
nonspace = len(re.findall(r"\S", sample)) or 1
ratio = letters / nonspace
# whole words only — Google garbage rarely forms real DE/EN function words
hits = sum(
    1
    for w in [
        r"(?<![A-Za-zÄÖÜäöüßſ])und(?![A-Za-zÄÖÜäöüßſ])",
        r"(?<![A-Za-zÄÖÜäöüßſ])der(?![A-Za-zÄÖÜäöüßſ])",
        r"(?<![A-Za-zÄÖÜäöüßſ])die(?![A-Za-zÄÖÜäöüßſ])",
        r"(?<![A-Za-zÄÖÜäöüßſ])das(?![A-Za-zÄÖÜäöüßſ])",
        r"(?<![A-Za-zÄÖÜäöüßſ])den(?![A-Za-zÄÖÜäöüßſ])",
        r"(?<![A-Za-zÄÖÜäöüßſ])mit(?![A-Za-zÄÖÜäöüßſ])",
        r"(?<![A-Za-zÄÖÜäöüßſ])von(?![A-Za-zÄÖÜäöüßſ])",
        r"(?<![A-Za-zÄÖÜäöüßſ])ist(?![A-Za-zÄÖÜäöüßſ])",
        r"(?<![A-Za-zÄÖÜäöüßſ])nicht(?![A-Za-zÄÖÜäöüßſ])",
        r"(?<![A-Za-zÄÖÜäöüßſ])the(?![A-Za-zÄÖÜäöüßſ])",
        r"(?<![A-Za-zÄÖÜäöüßſ])and(?![A-Za-zÄÖÜäöüßſ])",
    ]
    if re.search(w, sample, re.I)
)
# one-token-per-line dumps are classic bad Google layers
lines = [ln.strip() for ln in sample.splitlines() if ln.strip()]
short_lines = sum(1 for ln in lines if len(ln) <= 3)
short_ratio = short_lines / max(1, len(lines))
# digit/punct salad
weird = len(re.findall(r"[©®@#*{}|\\<>]|\d\)[A-Za-z]|[2S]\)[a-zA-Z]|[A-Za-z]\d{2,}|\^[A-Za-z]", sample))
# score: letter ratio alone is NOT enough (mojibake is still "letters")
score = min(1.0, hits / 5) * 0.55 + ratio * 0.25 - min(0.35, short_ratio) - min(0.3, weird / 100)
score = max(0.0, min(1.0, score))
if not sample.strip():
    label = "empty"
elif hits >= 4 and short_ratio < 0.35 and score >= 0.45:
    label = "usable"
elif hits >= 2 and short_ratio < 0.15 and ratio >= 0.85:
    # born-digital EN/DE prose or papers: few function hits in dense science still OK
    label = "usable"
elif hits >= 2 and score >= 0.30:
    label = "mixed"
else:
    label = "garbled"
# --- Fraktur diplomatic / Antiqua-OCR signals (research cluster 2018; UnbrokenOCR 0.3.1) ---
long_s = sample.count("ſ")
soft_hyphen = sample.count("⸗") + sample.count("\u00ad")
# Archiscribe-style: Antiqua engines often destroy ſt clusters (e.g. *ist* / *dieſe*)
st_cluster = len(re.findall(r"ſt", sample))
# mangled st/ist tokens common in bad Fraktur digital layers
mangled_st = len(re.findall(r"\b[il1|][s5$]t\b|\b[il1|]ft\b|\bdief[ec]\b|\bdieie\b", sample, re.I))
letters_nz = max(1, letters)
long_s_per_1k = round(1000.0 * long_s / letters_nz, 2)
fraktur_signals = {
    "long_s_count": long_s,
    "long_s_per_1k_letters": long_s_per_1k,
    "soft_hyphen_count": soft_hyphen,
    "st_long_s_clusters": st_cluster,
    "mangled_st_hits": mangled_st,
    # diplomatic long-s present OR classic Antiqua-on-Fraktur mangling with weak function words
    "likely_fraktur_print": bool(long_s >= 3 or st_cluster >= 2 or (mangled_st >= 2 and hits <= 3)),
}
kind_density = "digital" if text_chars > 80 * max(1, len(doc) // 2) else "scan-or-image"
if kind_density == "digital" and label in ("garbled", "empty"):
    recommend = "ocr-fraktur-or-scan"
elif kind_density == "digital" and label == "mixed":
    recommend = "spot-check-then-ocr"
elif kind_density == "digital" and fraktur_signals["likely_fraktur_print"] and long_s >= 5 and label == "usable":
    # usable diplomatic Fraktur layer (rare) — still prefer Fraktur-aware search sidecar
    recommend = "digital-fraktur-keep-long-s"
elif kind_density == "digital":
    recommend = "digital"
else:
    recommend = "ocr"
# Plate / figure zone heuristic: embedded images + empty/thin text layer.
# Not a full layout model — operators still confirm with renders + vision.
plate_page_candidates = [
    pg["n"]
    for pg in pages
    if pg["images"] > 0 and pg["chars"] < 40
]
# Dense image pages with some OCR-ish noise still plate-like
plate_page_candidates += [
    pg["n"]
    for pg in pages
    if pg["images"] >= 1 and pg["chars"] < 120 and pg["n"] not in plate_page_candidates
]
print(json.dumps({
    "path": p,
    "pages": len(doc),
    "text_chars": text_chars,
    "kind": kind_density,
    "text_quality": {
        "score": round(score, 3),
        "label": label,
        "letter_ratio": round(ratio, 3),
        "function_word_hits": hits,
        "short_line_ratio": round(short_ratio, 3),
        "sample_pages": [i + 1 for _, i, _ in ranked[:4]],
    },
    "fraktur_signals": fraktur_signals,
    "recommend": recommend,
    "page_detail": pages[:8],
    "plate_page_candidates": plate_page_candidates[:80],
    "plate_page_candidate_count": len(plate_page_candidates),
}))
