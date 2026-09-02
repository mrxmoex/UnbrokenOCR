import sys

kind = sys.argv[1]
if kind == "markdown_full":
    # full-doc markdown: pymupdf4llm (same as former -c when pages is None)
    import pymupdf4llm

    print(pymupdf4llm.to_markdown(sys.argv[2]))
elif kind == "markdown_pages":
    import pymupdf

    src, a, b = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    doc = pymupdf.open(src)
    parts = []
    for i in range(a - 1, b):
        if i < 0 or i >= len(doc):
            continue
        parts.append(f"## Page {i+1}\n\n")
        parts.append(doc[i].get_text("text") or "")
    print("".join(parts))
elif kind == "text_full":
    import pymupdf

    d = pymupdf.open(sys.argv[2])
    print("\n\n".join(p.get_text("text") or "" for p in d))
elif kind == "text_pages":
    import pymupdf

    src, a, b = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    doc = pymupdf.open(src)
    chunks = []
    for i in range(a - 1, b):
        if 0 <= i < len(doc):
            chunks.append(doc[i].get_text("text") or "")
    print("\n\n".join(chunks))
else:
    raise SystemExit(f"unknown digital extract kind: {kind}")
