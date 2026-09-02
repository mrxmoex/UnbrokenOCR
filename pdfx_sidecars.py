"""Working sidecars — not the UnbrokenOCR spine.

Spine (in pdfx.py): inspect, refuse garbled Google-Fraktur layers, digital
extract when usable, Fraktur/scan OCR when not, diplomatic ſ + search fold.

These stay in the tree and keep their CLI flags. They are extras:
  marker          — marker-pdf layout extract
  kurrent         — kraken HTR
  handwritten     — PNG dump for vision
  crawl           — folder listing
  index-paper     — write under papers/.../extract/
"""
from __future__ import annotations

import sys
from pathlib import Path

import pdfx as px


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
        if p.is_file() and p.suffix.lower() in px.PDF_EXT | px.IMAGE_EXT:
            files.append(p)
    return files


def extract_marker(path: Path, out_dir: Path | None, pages: str | None) -> str:
    if not px.MARKER.is_file():
        raise SystemExit(f"marker missing: {px.MARKER}")
    dest = out_dir or (px.ROOT / "smoke" / "marker" / path.stem)
    dest.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(px.MARKER),
        str(path),
        "--output_dir",
        str(dest),
        "--output_format",
        "markdown",
        "--mode",
        "fast",  # no Docker/nvidia OCI required on this box
    ]
    pr = px.parse_pages(pages)
    if pr is not None:
        first, last = pr
        cmd.extend(["--page_range", f"{first - 1}-{last - 1}"])
    r = px.run(cmd)
    if r.returncode != 0:
        raise SystemExit((r.stderr or "") + (r.stdout or "") or "marker failed")
    candidates = list(dest.rglob("*.md"))
    if not candidates:
        raise SystemExit(f"marker produced no markdown under {dest}")
    md = max(candidates, key=lambda p: p.stat().st_mtime)
    return md.read_text(encoding="utf-8", errors="replace")


def ocr_kurrent_image(path: Path) -> str:
    if not px.KRAKEN.is_file():
        raise SystemExit(f"kraken missing: {px.KRAKEN}")
    rec = px.first_existing(px.KURRENT_MODELS)
    if rec is None:
        raise SystemExit(
            "no Kurrent/hand model found. Expected under "
            f"{px.KRAKEN_MODELS} or ~/.local/share/htrmopo/"
        )
    seg = px.first_existing(px.SEG_MODELS)
    out_txt = path.with_suffix(".kurrent.txt")
    if seg is not None:
        cmd = [
            str(px.KRAKEN),
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
            str(px.KRAKEN),
            "-i",
            str(path),
            str(out_txt),
            "ocr",
            "-s",
            "-m",
            str(rec),
        ]
    r = px.run(cmd)
    if r.returncode != 0 or not out_txt.exists() or out_txt.stat().st_size == 0:
        cmd2 = [
            str(px.KRAKEN),
            "-i",
            str(path),
            str(out_txt),
            "ocr",
            "-s",
            "-m",
            str(rec),
        ]
        r2 = px.run(cmd2)
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
    if suf in px.IMAGE_EXT:
        return ocr_kurrent_image(path)
    if suf != ".pdf":
        raise SystemExit(f"kurrent needs pdf/image, got {suf}")
    pr = px.parse_pages(pages) or (1, 2)
    first, last = pr
    dest = render_dir or Path(f"/tmp/pdfx-kurrent/{path.stem}")
    imgs = px.render_pages(path, dest, first, last, dpi=300)
    chunks = []
    for im in imgs:
        chunks.append(f"--- {im.name} ---\n{ocr_kurrent_image(im)}")
    return "\n\n".join(chunks)


def write_index_paper(path: Path, text: str, name: str) -> Path | None:
    """Sidecar: write extract under papers/.../extract/ when that layout exists."""
    ped = paper_extract_dir(path)
    if ped:
        ped.mkdir(parents=True, exist_ok=True)
        dest = ped / name
        dest.write_text(text, encoding="utf-8")
        return dest
    return None


def run_crawl(path: Path) -> None:
    files = crawl(path)
    print(f"# pdfx {px.__version__} crawl {path} → {len(files)} files", file=sys.stderr)
    for f in files:
        print(f)


def run_handwritten(args, path: Path, suf: str, pages: str | None, edge_flags: list[str]) -> None:
    pr = px.parse_pages(pages) or (1, 2)
    first, last = pr
    dest = Path(args.render_dir or f"/tmp/pdfx-hand/{path.stem}")
    if suf == ".pdf":
        info = px.enrich_inspect(px.inspect_pdf(path))
        px.print_mode_header(
            mode_requested=args.mode,
            mode_effective="handwritten-vision",
            engine="render",
            info=info,
            path=path,
            pages=pages,
            dpi=args.dpi,
            edge_flags=edge_flags,
        )
        imgs = px.render_pages(path, dest, first, last)
    else:
        dest.mkdir(parents=True, exist_ok=True)
        imgs = [path]
        px.print_mode_header(
            mode_requested=args.mode,
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


def run_marker(args, path: Path, pages: str | None, edge_flags: list[str]) -> tuple[str, bool]:
    """Returns (text, done). done True: indexed without --out; caller returns."""
    px.print_mode_header(
        mode_requested=args.mode,
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
        dest = write_index_paper(path, text, "marker.md")
        if dest is not None:
            print(f"indexed {dest} ({len(text)} chars)")
            return text, True
    return text, False


def run_kurrent(args, path: Path, pages: str | None, edge_flags: list[str]) -> str:
    if px.first_existing(px.KURRENT_MODELS) is None:
        raise SystemExit(
            "no Kurrent/hand model found.\n"
            f"  Looked under: {px.KRAKEN_MODELS} and ~/.local/share/htrmopo/\n"
            "  Place kraken_german_finetuned.mlmodel (or set PDFX_KRAKEN_MODELS)."
        )
    px.print_mode_header(
        mode_requested=args.mode,
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
        write_index_paper(path, text, "kurrent.txt")
    return text
