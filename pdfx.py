#!/usr/bin/env python3
"""Local PDF / image extract + crawl. No cloud.

Routes:
  digital text layer  -> pymupdf / pymupdf4llm
  complex layout      -> marker-pdf (--mode fast; no Docker)
  scan / photocopy    -> ocrmypdf + tesseract deu+eng
  old German print    -> tesseract deu+frk (Fraktur) via render
  Kurrent / hand HTR  -> kraken + local mlmodel
  few-page mystery    -> render pages for Hermes vision

2026-08-24 fine-tune (post 3-agent Dachdecker compare):
  - TESSDATA_PREFIX = tessdata dir (not parent)
  - --pages honored on digital + OCR paths
  - Fraktur / forced OCR uses --force-ocr or image OCR (not --skip-text)
  - inspect reports text_quality; auto refuses garbled Google layers
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

__version__ = "0.3.0"


def _discover_root() -> Path:
    """Install / checkout root. Override with PDFX_HOME or PDFX_ROOT."""
    for key in ("PDFX_HOME", "PDFX_ROOT"):
        env = os.environ.get(key)
        if env:
            return Path(env).expanduser().resolve()
    return Path(__file__).resolve().parent


def _discover_tessdata() -> Path:
    """Tessdata *directory* (not parent). Override with TESSDATA_PREFIX."""
    env = os.environ.get("TESSDATA_PREFIX")
    if env:
        p = Path(env).expanduser()
        # Mis-set parent of tessdata → correct to child if needed
        if (p / "tessdata").is_dir() and not any(p.glob("*.traineddata")):
            return p / "tessdata"
        return p
    home = Path.home()
    candidates = [
        home / ".local" / "share" / "tessdata",
        Path("/usr/share/tesseract-ocr/5/tessdata"),
        Path("/usr/share/tesseract-ocr/4.00/tessdata"),
        Path("/usr/share/tessdata"),
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def _which_or(*candidates: Path) -> Path:
    for c in candidates:
        if c is None:
            continue
        if isinstance(c, Path) and c.is_file():
            return c
        name = str(c)
        found = shutil.which(name)
        if found:
            return Path(found)
    return candidates[0] if candidates else Path("missing")


ROOT = _discover_root()


def _python_for_pymupdf() -> Path:
    """Prefer $PDFX_HOME/.venv if it has pymupdf; else current interpreter."""
    candidates = [
        ROOT / ".venv" / "bin" / "python",
        Path(sys.executable),
        Path(shutil.which("python3") or "python3"),
    ]
    for py in candidates:
        if not py or not Path(py).exists():
            continue
        r = subprocess.run(
            [str(py), "-c", "import fitz"],
            capture_output=True,
            text=True,
            check=False,
        )
        if r.returncode == 0:
            return Path(py)
    # Last resort: current interpreter (import will fail later with a clear error)
    return Path(sys.executable)


VENV_PY = _python_for_pymupdf()
MARKER = _which_or(ROOT / ".venv" / "bin" / "marker_single", Path("marker_single"))
KRAKEN = _which_or(ROOT / ".venv-kraken" / "bin" / "kraken", Path("kraken"))
KRAKEN_MODELS = Path(
    os.environ.get("PDFX_KRAKEN_MODELS", str(ROOT / "models" / "kraken"))
).expanduser()
# tesseract/ocrmypdf want the tessdata *directory* itself (not its parent).
TESSDATA = _discover_tessdata()
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}
PDF_EXT = {".pdf"}

def _glob_models(root: Path, pattern: str) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(root.glob(pattern))


# Preferred recognition models (first existing wins)
_HTRMOPO = Path.home() / ".local" / "share" / "htrmopo"
KURRENT_MODELS = [
    KRAKEN_MODELS / "kraken_german_finetuned.mlmodel",
    KRAKEN_MODELS / "german_handwriting.mlmodel",
    KRAKEN_MODELS / "fanny_20250228.mlmodel",
    *_glob_models(_HTRMOPO, "*/german_handwriting.mlmodel"),
    *_glob_models(_HTRMOPO, "*/fanny_*.mlmodel"),
]
SEG_MODELS = [
    KRAKEN_MODELS / "blla.mlmodel",
    *_glob_models(ROOT / ".venv-kraken" / "lib", "python*/site-packages/kraken/blla.mlmodel"),
]


def env_ocr() -> dict:
    """Env for tesseract + ocrmypdf. TESSDATA_PREFIX must be the tessdata dir here."""
    e = os.environ.copy()
    e["TESSDATA_PREFIX"] = str(TESSDATA)
    # Also clear poisoned parent-style prefix if any caller exported the wrong one
    return e


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=False, text=True, capture_output=True, **kw)


def first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.is_file():
            return p
    return None


def parse_pages(pages: str | None) -> tuple[int, int] | None:
    """Return 1-based inclusive (first, last), or None if full document."""
    if pages is None or str(pages).strip() in ("", "all", "*"):
        return None
    pages = str(pages).strip()
    if "-" in pages:
        a, b = pages.split("-", 1)
        return int(a), int(b)
    n = int(pages)
    return n, n


def text_quality(sample: str) -> dict:
    """Heuristic: is this embedded layer usable German/Latin, or Google Fraktur garbage?"""
    s = sample or ""
    if not s.strip():
        return {"score": 0.0, "label": "empty", "chars": 0}
    # letters (incl. German) vs total non-space
    letters = len(re.findall(r"[A-Za-zÄÖÜäöüßſ]", s))
    nonspace = len(re.findall(r"\S", s))
    ratio = letters / max(1, nonspace)
    # common German function words (modern + Fraktur long-s variants lightly)
    hits = 0
    for w in (
        r"\bund\b",
        r"\bder\b",
        r"\bdie\b",
        r"\bdas\b",
        r"\bden\b",
        r"\bmit\b",
        r"\bvon\b",
        r"\bzu\b",
        r"\bist\b",
        r"\bnicht\b",
        r"\bthe\b",
        r"\band\b",
    ):
        if re.search(w, s, re.I):
            hits += 1
    # garbage markers often seen in bad Google layers
    garbage = len(re.findall(r"[©®@#*{}|\\<>]|\d\)[a-zA-Z]|2\)[a-zA-Z]", s))
    score = ratio * 0.7 + min(1.0, hits / 6) * 0.3 - min(0.4, garbage / 80)
    score = max(0.0, min(1.0, score))
    if score >= 0.55 and hits >= 3:
        label = "usable"
    elif score >= 0.35:
        label = "mixed"
    else:
        label = "garbled"
    return {
        "score": round(score, 3),
        "label": label,
        "chars": len(s),
        "letter_ratio": round(ratio, 3),
        "function_word_hits": hits,
    }


def inspect_pdf(path: Path) -> dict:
    code = r"""
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
kind_density = "digital" if text_chars > 80 * max(1, len(doc) // 2) else "scan-or-image"
if kind_density == "digital" and label in ("garbled", "empty"):
    recommend = "ocr-fraktur-or-scan"
elif kind_density == "digital" and label == "mixed":
    recommend = "spot-check-then-ocr"
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
    "recommend": recommend,
    "page_detail": pages[:8],
    "plate_page_candidates": plate_page_candidates[:80],
    "plate_page_candidate_count": len(plate_page_candidates),
}))
"""
    r = run([str(VENV_PY), "-c", code, str(path)])
    if r.returncode != 0:
        raise SystemExit(r.stderr or r.stdout or "inspect failed")
    return json.loads(r.stdout)


def slice_pdf(path: Path, first: int, last: int, dest: Path) -> Path:
    """Write 1-based inclusive page slice to dest (PDF)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    code = r"""
import sys
import pymupdf
src, out, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
doc = pymupdf.open(src)
# pymupdf from_page/to_page are 0-based inclusive
nd = pymupdf.open()
nd.insert_pdf(doc, from_page=a - 1, to_page=b - 1)
nd.save(out)
nd.close()
doc.close()
"""
    r = run([str(VENV_PY), "-c", code, str(path), str(dest), str(first), str(last)])
    if r.returncode != 0 or not dest.is_file():
        raise SystemExit((r.stderr or "") + (r.stdout or "") or "slice_pdf failed")
    return dest


def extract_digital(path: Path, markdown: bool, pages: str | None = None) -> str:
    pr = parse_pages(pages)
    if markdown:
        # pymupdf4llm can OCR images — avoid for pure digital; use get_text path when pages set
        # For full-doc markdown without pages, keep pymupdf4llm but warn via stderr if slow
        if pr is None:
            code = "import sys, pymupdf4llm; print(pymupdf4llm.to_markdown(sys.argv[1]))"
            r = run([str(VENV_PY), "-c", code, str(path)])
        else:
            first, last = pr
            code = r"""
import sys, pymupdf
src, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
doc = pymupdf.open(src)
parts = []
for i in range(a - 1, b):
    if i < 0 or i >= len(doc):
        continue
    parts.append(f"## Page {i+1}\n\n")
    parts.append(doc[i].get_text("text") or "")
print("".join(parts))
"""
            r = run([str(VENV_PY), "-c", code, str(path), str(first), str(last)])
    else:
        if pr is None:
            code = (
                "import sys, pymupdf\n"
                "d=pymupdf.open(sys.argv[1])\n"
                "print('\\n\\n'.join(p.get_text('text') or '' for p in d))\n"
            )
            r = run([str(VENV_PY), "-c", code, str(path)])
        else:
            first, last = pr
            code = r"""
import sys, pymupdf
src, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
doc = pymupdf.open(src)
chunks = []
for i in range(a - 1, b):
    if 0 <= i < len(doc):
        chunks.append(doc[i].get_text("text") or "")
print("\n\n".join(chunks))
"""
            r = run([str(VENV_PY), "-c", code, str(path), str(first), str(last)])
    if r.returncode != 0:
        raise SystemExit(r.stderr or "extract failed")
    return r.stdout


def extract_marker(path: Path, out_dir: Path | None, pages: str | None) -> str:
    if not MARKER.is_file():
        raise SystemExit(f"marker missing: {MARKER}")
    dest = out_dir or (ROOT / "smoke" / "marker" / path.stem)
    dest.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(MARKER),
        str(path),
        "--output_dir",
        str(dest),
        "--output_format",
        "markdown",
        "--mode",
        "fast",  # no Docker/nvidia OCI required on this box
    ]
    pr = parse_pages(pages)
    if pr is not None:
        first, last = pr
        cmd.extend(["--page_range", f"{first - 1}-{last - 1}"])
    r = run(cmd)
    if r.returncode != 0:
        raise SystemExit((r.stderr or "") + (r.stdout or "") or "marker failed")
    candidates = list(dest.rglob("*.md"))
    if not candidates:
        raise SystemExit(f"marker produced no markdown under {dest}")
    md = max(candidates, key=lambda p: p.stat().st_mtime)
    return md.read_text(encoding="utf-8", errors="replace")


def langs_for(mode: str) -> str:
    if mode in ("fraktur", "old-german", "old"):
        return "deu+frk+eng"
    return "deu+eng"


def ocr_image(path: Path, mode: str, psm: int = 6) -> str:
    lang = langs_for(mode)
    r = run(
        [
            "tesseract",
            "--tessdata-dir",
            str(TESSDATA),
            str(path),
            "stdout",
            "-l",
            lang,
            "--psm",
            str(psm),
        ],
        env=env_ocr(),
    )
    if r.returncode != 0:
        raise SystemExit(r.stderr or "tesseract failed")
    return r.stdout


def render_pages(path: Path, dest: Path, first: int, last: int, dpi: int = 300) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    # clean old pages in dest to avoid stale globs
    for old in dest.glob("page*.png"):
        try:
            old.unlink()
        except OSError:
            pass
    prefix = dest / "page"
    r = run(
        [
            "pdftoppm",
            "-png",
            "-r",
            str(dpi),
            "-f",
            str(first),
            "-l",
            str(last),
            str(path),
            str(prefix),
        ]
    )
    if r.returncode != 0:
        raise SystemExit(r.stderr or "pdftoppm failed")
    return sorted(dest.glob("page*.png"))


def ocr_pdf_via_images(
    path: Path,
    mode: str,
    pages: str | None,
    render_dir: Path | None,
    dpi: int = 300,
) -> str:
    """Reliable Fraktur/scan path: pdftoppm → tesseract (honors pages)."""
    info_pages = inspect_pdf(path)["pages"]
    pr = parse_pages(pages)
    if pr is None:
        first, last = 1, info_pages
    else:
        first, last = pr
        first = max(1, first)
        last = min(info_pages, last)
    dest = render_dir or Path(tempfile.mkdtemp(prefix=f"pdfx-ocr-{path.stem}-"))
    imgs = render_pages(path, dest, first, last, dpi=dpi)
    if not imgs:
        raise SystemExit("no pages rendered")
    chunks: list[str] = []
    for im in imgs:
        # page-001.png → label
        chunks.append(f"===== {im.name} =====\n{ocr_image(im, mode)}")
    return "\n\n".join(chunks)


def ocr_pdf_ocrmypdf(
    path: Path,
    mode: str,
    pages: str | None,
    out_pdf: Path | None,
    force: bool,
) -> str:
    """ocrmypdf path with correct tessdata + optional page slice + force-ocr."""
    lang = langs_for(mode)
    work = Path(tempfile.mkdtemp(prefix="pdfx-ocrmypdf-"))
    src = path
    pr = parse_pages(pages)
    if pr is not None:
        first, last = pr
        src = slice_pdf(path, first, last, work / f"slice_{first}-{last}.pdf")
    sidecar = work / "sidecar.txt"
    searchable = out_pdf or (work / "searchable.pdf")
    cmd = [
        "ocrmypdf",
        "-l",
        lang,
        "--sidecar",
        str(sidecar),
        "--optimize",
        "0",
    ]
    if force:
        cmd.append("--force-ocr")
    else:
        cmd.append("--skip-text")
    cmd.extend([str(src), str(searchable)])
    r = run(cmd, env=env_ocr())
    if r.returncode != 0:
        err = (r.stderr or "") + (r.stdout or "")
        if not force and ("PriorOcrFoundError" in err or "page already has text" in err.lower()):
            # caller asked soft path; fall back to digital of slice/full
            return extract_digital(src, markdown=False, pages=None)
        raise SystemExit(err or "ocrmypdf failed")
    return sidecar.read_text(encoding="utf-8", errors="replace") if sidecar.exists() else ""


def ocr_pdf(
    path: Path,
    mode: str,
    pages: str | None,
    out_pdf: Path | None,
    force: bool,
    render_dir: Path | None = None,
    engine: str = "auto",
    dpi: int = 300,
) -> str:
    """
    engine:
      auto     — fraktur/old-german → ocrmypdf (Gate B 2026-08-25); else ocrmypdf
      images   — always pdftoppm+tesseract (QA / debug)
      ocrmypdf — always ocrmypdf force-ocr on slice
    """
    frakturish = mode in ("fraktur", "old-german", "old")
    if engine == "images":
        return ocr_pdf_via_images(
            path, mode if frakturish else mode, pages, render_dir, dpi=dpi
        )
    # auto + ocrmypdf: force when user asked --ocr or fraktur or force flag
    return ocr_pdf_ocrmypdf(path, mode, pages, out_pdf, force=force or frakturish)


def ocr_kurrent_image(path: Path) -> str:
    if not KRAKEN.is_file():
        raise SystemExit(f"kraken missing: {KRAKEN}")
    rec = first_existing(KURRENT_MODELS)
    if rec is None:
        raise SystemExit(
            "no Kurrent/hand model found. Expected under "
            f"{KRAKEN_MODELS} or ~/.local/share/htrmopo/"
        )
    seg = first_existing(SEG_MODELS)
    out_txt = path.with_suffix(".kurrent.txt")
    if seg is not None:
        cmd = [
            str(KRAKEN),
            "-i",
            str(path),
            str(out_txt),
            "binarize",
            "segment",
            "-bl",
            "-i",
            str(seg),
            "ocr",
            "-m",
            str(rec),
        ]
    else:
        cmd = [
            str(KRAKEN),
            "-i",
            str(path),
            str(out_txt),
            "ocr",
            "-s",
            "-m",
            str(rec),
        ]
    r = run(cmd)
    if r.returncode != 0 or not out_txt.exists() or out_txt.stat().st_size == 0:
        cmd2 = [
            str(KRAKEN),
            "-i",
            str(path),
            str(out_txt),
            "ocr",
            "-s",
            "-m",
            str(rec),
        ]
        r2 = run(cmd2)
        if r2.returncode != 0 and not out_txt.exists():
            raise SystemExit(
                (r.stderr or "")
                + (r.stdout or "")
                + (r2.stderr or "")
                + (r2.stdout or "")
                or "kraken ocr failed"
            )
    return out_txt.read_text(encoding="utf-8", errors="replace") if out_txt.exists() else (r.stdout or "")


def ocr_kurrent(path: Path, pages: str, render_dir: Path | None) -> str:
    suf = path.suffix.lower()
    if suf in IMAGE_EXT:
        return ocr_kurrent_image(path)
    if suf != ".pdf":
        raise SystemExit(f"kurrent needs pdf/image, got {suf}")
    pr = parse_pages(pages) or (1, 2)
    first, last = pr
    dest = render_dir or Path(f"/tmp/pdfx-kurrent/{path.stem}")
    imgs = render_pages(path, dest, first, last, dpi=300)
    chunks = []
    for im in imgs:
        chunks.append(f"--- {im.name} ---\n{ocr_kurrent_image(im)}")
    return "\n\n".join(chunks)


def paper_extract_dir(pdf: Path) -> Path | None:
    """If PDF lives under Documents/papers/.../<id>/, return .../<id>/extract/."""
    parts = pdf.resolve().parts
    try:
        parts.index("papers")
    except ValueError:
        return None
    parent = pdf.parent
    # parts/ sibling of extract for google books layout
    if parent.name == "parts":
        return parent.parent / "extract"
    if parent.name in ("inbox", "papers"):
        return parent / "extract" / pdf.stem
    return parent / "extract"


def crawl(root: Path) -> list[Path]:
    files = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in PDF_EXT | IMAGE_EXT:
            files.append(p)
    return files


def dependency_status() -> dict:
    frk = TESSDATA / "frk.traineddata"
    deu = TESSDATA / "deu.traineddata"
    return {
        "pdfx_version": __version__,
        "pdfx_home": str(ROOT),
        "python": str(VENV_PY),
        "tessdata": str(TESSDATA),
        "frk": frk.is_file(),
        "deu": deu.is_file(),
        "tesseract": bool(shutil.which("tesseract")),
        "ocrmypdf": bool(shutil.which("ocrmypdf")),
        "pdftoppm": bool(shutil.which("pdftoppm")),
        "marker": Path(MARKER).is_file() if MARKER else False,
        "kraken": Path(KRAKEN).is_file() if KRAKEN else False,
    }


def print_mode_header(
    *,
    mode_requested: str,
    mode_effective: str,
    engine: str,
    info: dict | None,
    path: Path,
    pages: str | None,
    dpi: int,
    edge_flags: list[str] | None = None,
) -> None:
    """Machine-readable MODE DETECTION HEADER on stderr (every extract)."""
    tq = (info or {}).get("text_quality") or {}
    deps = dependency_status()
    lines = [
        f"# pdfx {__version__}",
        f"# mode_requested={mode_requested} mode_effective={mode_effective} engine={engine}",
        f"# kind={(info or {}).get('kind', '?')} text_quality={tq.get('label', '?')} "
        f"recommend={(info or {}).get('recommend', '?')}",
        f"# pages={pages or 'all'} dpi={dpi} tessdata={TESSDATA} frk={'yes' if deps['frk'] else 'no'}",
        f"# path={path}",
    ]
    if edge_flags:
        lines.append(f"# edge_flags={','.join(edge_flags)}")
    plates = (info or {}).get("plate_page_candidate_count")
    if plates is not None:
        lines.append(f"# plate_page_candidates={plates}")
    print("\n".join(lines), file=sys.stderr)


def require_frk(mode: str) -> None:
    if mode not in ("fraktur", "old-german", "old"):
        return
    if not (TESSDATA / "frk.traineddata").is_file():
        raise SystemExit(
            "missing frk.traineddata for Fraktur OCR.\n"
            f"  Expected under: {TESSDATA}/\n"
            "  Install: distro package tesseract-ocr-frk, or copy frk.traineddata\n"
            "  from tessdata_best/fast into that directory.\n"
            "  export TESSDATA_PREFIX to the tessdata *directory* (not its parent)."
        )


def resolve_engine(mode: str, engine: str, edge_flags: list[str]) -> str:
    frakturish = mode in ("fraktur", "old-german", "old")
    if engine == "auto":
        eff = "ocrmypdf" if frakturish or mode == "scan" else "ocrmypdf"
    else:
        eff = engine
    if eff == "ocrmypdf" and not shutil.which("ocrmypdf"):
        edge_flags.append("ocrmypdf_missing_fallback_images")
        print("# warn: ocrmypdf not on PATH → falling back to engine=images", file=sys.stderr)
        eff = "images"
    if eff == "images" and not shutil.which("pdftoppm"):
        raise SystemExit(
            "pdftoppm missing (Poppler). Install poppler-utils / poppler package,\n"
            "or install ocrmypdf and use --engine ocrmypdf."
        )
    if eff == "ocrmypdf" and not shutil.which("tesseract"):
        raise SystemExit("tesseract missing on PATH (required by ocrmypdf)")
    return eff


def enrich_inspect(info: dict) -> dict:
    info = dict(info)
    info["pdfx_version"] = __version__
    info["dependencies"] = dependency_status()
    edge: list[str] = []
    tq = (info.get("text_quality") or {}).get("label")
    if info.get("kind") == "digital" and tq == "garbled":
        edge.append("google_fraktur_trap")
    if info.get("plate_page_candidate_count", 0) > 0:
        edge.append("plate_zone_present")
    if not info["dependencies"].get("frk"):
        edge.append("frk_missing")
    info["edge_flags"] = edge
    info["mode_effective_hint"] = (
        "fraktur"
        if info.get("recommend") in ("ocr-fraktur-or-scan", "spot-check-then-ocr")
        else info.get("recommend") or "digital"
    )
    return info


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Local PDF/image extract + folder crawl (pdfx)",
        epilog="Infographics/plates: see skill/references/INFOGRAPHICS.md — "
        "inspect plate_page_candidates, render, body Fig/Taf index, vision QA.",
    )
    ap.add_argument("--version", action="version", version=f"pdfx {__version__}")
    ap.add_argument("path", nargs="?", help="PDF, image, or directory")
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument(
        "--ocr",
        action="store_true",
        help="force OCR even if a text layer exists (uses --force-ocr / image path)",
    )
    ap.add_argument(
        "--mode",
        default="auto",
        choices=[
            "auto",
            "digital",
            "scan",
            "fraktur",
            "old-german",
            "marker",
            "kurrent",
            "handwritten",
        ],
    )
    ap.add_argument("--out", help="write text/markdown here")
    ap.add_argument("--index-paper", action="store_true", help="also write under papers/.../extract/")
    ap.add_argument("--crawl", action="store_true")
    ap.add_argument("--render-dir", help="page image dump dir")
    ap.add_argument(
        "--pages",
        default=None,
        help="1-based inclusive page range (e.g. 8-20). Default: all pages (digital/scan) or 1-2 (kurrent/handwritten)",
    )
    ap.add_argument(
        "--engine",
        default="auto",
        choices=["auto", "images", "ocrmypdf"],
        help="OCR engine: auto (fraktur→ocrmypdf), images (pdftoppm+tesseract QA), ocrmypdf",
    )
    ap.add_argument("--dpi", type=int, default=300, help="render DPI for image OCR (default 300)")
    ap.add_argument(
        "--plates-sidecar",
        action="store_true",
        help="with --out, also write *.plates.json from inspect plate_page_candidates",
    )
    args = ap.parse_args()

    if args.path is None:
        ap.print_help()
        raise SystemExit(2)

    path = Path(args.path).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"missing: {path}")

    edge_flags: list[str] = []

    if args.crawl or path.is_dir():
        files = crawl(path)
        print(f"# pdfx {__version__} crawl {path} → {len(files)} files", file=sys.stderr)
        for f in files:
            print(f)
        return

    suf = path.suffix.lower()
    if suf not in PDF_EXT | IMAGE_EXT and not args.crawl:
        raise SystemExit(f"unsupported type: {suf or '(none)'} — need PDF or image {sorted(PDF_EXT | IMAGE_EXT)}")

    if args.inspect:
        if suf != ".pdf":
            raise SystemExit("--inspect requires a PDF")
        try:
            info = enrich_inspect(inspect_pdf(path))
        except Exception as e:
            msg = str(e).lower()
            if "password" in msg or "encrypted" in msg:
                raise SystemExit("PDF is password-protected / encrypted — unlock first, then retry") from e
            raise
        print(json.dumps(info, indent=2))
        return

    # defaults for page ranges on hand modes
    pages = args.pages
    if args.mode in ("kurrent", "handwritten") and pages is None:
        pages = "1-2"
        edge_flags.append("default_pages_1-2")

    info: dict | None = None
    mode_requested = args.mode
    mode = args.mode
    engine_eff = args.engine

    if args.mode == "handwritten":
        pr = parse_pages(pages) or (1, 2)
        first, last = pr
        dest = Path(args.render_dir or f"/tmp/pdfx-hand/{path.stem}")
        if suf == ".pdf":
            info = enrich_inspect(inspect_pdf(path))
            print_mode_header(
                mode_requested=mode_requested,
                mode_effective="handwritten-vision",
                engine="render",
                info=info,
                path=path,
                pages=pages,
                dpi=args.dpi,
                edge_flags=edge_flags,
            )
            imgs = render_pages(path, dest, first, last)
        else:
            dest.mkdir(parents=True, exist_ok=True)
            imgs = [path]
            print_mode_header(
                mode_requested=mode_requested,
                mode_effective="handwritten-vision",
                engine="render",
                info=None,
                path=path,
                pages=pages,
                dpi=args.dpi,
                edge_flags=edge_flags,
            )
        print("HANDWRITTEN fallback (vision)")
        print("For Kurrent engine use: pdfx FILE --mode kurrent")
        print("Vision PNGs:")
        for im in imgs:
            print(im)
        return

    if args.mode == "marker":
        print_mode_header(
            mode_requested=mode_requested,
            mode_effective="marker",
            engine="marker_single",
            info=None,
            path=path,
            pages=pages,
            dpi=args.dpi,
            edge_flags=edge_flags,
        )
        out_dir = None
        if args.index_paper:
            ped = paper_extract_dir(path)
            if ped:
                out_dir = ped / "marker_raw"
        text = extract_marker(path, out_dir, pages)
        if args.out is None and args.index_paper:
            ped = paper_extract_dir(path)
            if ped:
                ped.mkdir(parents=True, exist_ok=True)
                (ped / "marker.md").write_text(text, encoding="utf-8")
                print(f"indexed {ped / 'marker.md'} ({len(text)} chars)")
                return
    elif args.mode in ("kurrent",):
        if first_existing(KURRENT_MODELS) is None:
            raise SystemExit(
                "no Kurrent/hand model found.\n"
                f"  Looked under: {KRAKEN_MODELS} and ~/.local/share/htrmopo/\n"
                "  Place kraken_german_finetuned.mlmodel (or set PDFX_KRAKEN_MODELS)."
            )
        print_mode_header(
            mode_requested=mode_requested,
            mode_effective="kurrent",
            engine="kraken",
            info=None,
            path=path,
            pages=pages or "1-2",
            dpi=args.dpi,
            edge_flags=edge_flags,
        )
        text = ocr_kurrent(path, pages or "1-2", Path(args.render_dir) if args.render_dir else None)
        if args.index_paper:
            ped = paper_extract_dir(path)
            if ped:
                ped.mkdir(parents=True, exist_ok=True)
                (ped / "kurrent.txt").write_text(text, encoding="utf-8")
    elif suf in IMAGE_EXT:
        if mode_requested == "digital":
            edge_flags.append("image_forced_ocr")
            print("# warn: image has no digital text layer → OCR", file=sys.stderr)
        mode = "fraktur" if mode_requested in ("fraktur", "old-german", "auto") else "scan"
        if mode_requested == "auto":
            mode = "scan"
        require_frk(mode)
        engine_eff = "tesseract-image"
        print_mode_header(
            mode_requested=mode_requested,
            mode_effective=mode,
            engine=engine_eff,
            info=None,
            path=path,
            pages="1",
            dpi=args.dpi,
            edge_flags=edge_flags,
        )
        text = ocr_image(path, "fraktur" if mode == "fraktur" else "scan")
    elif suf == ".pdf":
        try:
            info = enrich_inspect(inspect_pdf(path))
        except Exception as e:
            msg = str(e).lower()
            if "password" in msg or "encrypted" in msg:
                raise SystemExit("PDF is password-protected / encrypted — unlock first, then retry") from e
            raise
        edge_flags.extend(info.get("edge_flags") or [])
        n_pages = int(info.get("pages") or 0)
        if n_pages == 0:
            raise SystemExit("PDF has 0 pages")
        # page range validation
        pr = parse_pages(pages)
        if pr is not None:
            a, b = pr
            if a > n_pages or b < 1:
                raise SystemExit(f"--pages {pages} outside document (1–{n_pages})")
            if a < 1 or b > n_pages:
                edge_flags.append("pages_clamped")
                print(f"# warn: clamping --pages to 1–{n_pages}", file=sys.stderr)
                a, b = max(1, a), min(n_pages, b)
                pages = f"{a}-{b}"

        mode = args.mode
        if mode == "auto":
            rec = info.get("recommend") or "digital"
            tq = (info.get("text_quality") or {}).get("label")
            if args.ocr:
                mode = "fraktur" if tq in ("garbled", "mixed", "empty") else "scan"
            elif rec == "digital":
                mode = "digital"
            elif rec in ("ocr-fraktur-or-scan", "spot-check-then-ocr"):
                mode = "fraktur"
            else:
                mode = "scan"

        if mode == "digital" and (info.get("text_quality") or {}).get("label") == "garbled":
            if args.mode == "digital":
                edge_flags.append("forced_digital_on_garbled")
                print(
                    "# warn: forced --mode digital on garbled layer (Google Fraktur trap). "
                    "Prefer --mode fraktur.",
                    file=sys.stderr,
                )
            elif args.mode == "auto":
                pass  # already routed

        if mode in ("fraktur", "old-german", "scan") and pages is None and n_pages > 40:
            edge_flags.append("large_pdf_no_pages")
            print(
                f"# warn: {n_pages} pages without --pages — consider chunks "
                f"(pdfx-batch-fraktur, 15–20 pp).",
                file=sys.stderr,
            )

        require_frk(mode)
        if mode == "digital" and not args.ocr:
            engine_eff = "pymupdf"
        else:
            engine_eff = resolve_engine(mode, args.engine, edge_flags)

        print_mode_header(
            mode_requested=mode_requested,
            mode_effective=mode,
            engine=engine_eff,
            info=info,
            path=path,
            pages=pages,
            dpi=args.dpi,
            edge_flags=edge_flags,
        )

        if mode == "digital" and not args.ocr:
            text = extract_digital(path, markdown=args.markdown, pages=pages)
            tq = text_quality(text[:4000])
            if tq["label"] == "garbled":
                print(
                    f"# warn: digital extract looks {tq['label']} "
                    f"(score={tq['score']}). Prefer: pdfx FILE --mode fraktur --pages …",
                    file=sys.stderr,
                )
            if args.index_paper and args.markdown:
                ped = paper_extract_dir(path)
                if ped:
                    ped.mkdir(parents=True, exist_ok=True)
                    (ped / "pymupdf.md").write_text(text, encoding="utf-8")
        else:
            force = bool(args.ocr) or mode in ("fraktur", "old-german", "scan")
            text = ocr_pdf(
                path,
                mode,
                pages,
                None,
                force=force,
                render_dir=Path(args.render_dir) if args.render_dir else None,
                engine=engine_eff if engine_eff in ("auto", "images", "ocrmypdf") else "ocrmypdf",
                dpi=args.dpi,
            )
            if args.index_paper:
                ped = paper_extract_dir(path)
                if ped:
                    ped.mkdir(parents=True, exist_ok=True)
                    name = "fraktur.txt" if mode in ("fraktur", "old-german") else "ocr.txt"
                    (ped / name).write_text(text, encoding="utf-8")
    else:
        raise SystemExit(f"unsupported: {suf}")

    if args.out:
        outp = Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({len(text)} chars)")
        if args.plates_sidecar and info is not None:
            side = outp.with_suffix(outp.suffix + ".plates.json")
            side.write_text(
                json.dumps(
                    {
                        "pdfx_version": __version__,
                        "source": str(path),
                        "plate_page_candidates": info.get("plate_page_candidates"),
                        "plate_page_candidate_count": info.get("plate_page_candidate_count"),
                        "guide": "references/INFOGRAPHICS.md",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            print(f"wrote plates sidecar {side}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()