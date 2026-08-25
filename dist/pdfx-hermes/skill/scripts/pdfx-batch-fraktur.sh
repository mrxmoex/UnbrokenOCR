#!/usr/bin/env bash
# pdfx-batch-fraktur.sh — chunked Fraktur OCR for Google-style scans
# Default engine after Gate B 2026-08-25: ocrmypdf (images = QA).
set -euo pipefail

# Prefer installed pdfx; optional local venv next to PDFX_HOME
PDFX_HOME="${PDFX_HOME:-${PDFX_ROOT:-}}"
if [[ -n "${PDFX_HOME}" ]]; then
  export PATH="${HOME}/.local/bin:${PDFX_HOME}/.venv/bin:${PATH}"
else
  export PATH="${HOME}/.local/bin:${PATH}"
fi
# Tessdata *directory* (not parent). Leave unset if pdfx discovers it.
if [[ -z "${TESSDATA_PREFIX:-}" && -d "${HOME}/.local/share/tessdata" ]]; then
  export TESSDATA_PREFIX="${HOME}/.local/share/tessdata"
fi

PDF="${1:?usage: $0 PDF [out_dir] [chunk_pages] [engine] [start] [end]}"
OUT_DIR="${2:-$(dirname "$PDF")/../extract/fraktur}"
CHUNK="${3:-20}"
ENGINE="${4:-ocrmypdf}"   # default after Gate B: ocrmypdf (images = QA)
START="${5:-1}"
END="${6:-}"
DPI="${PDFX_DPI:-300}"
LOG="${OUT_DIR}/batch.log"

if ! command -v pdfx >/dev/null 2>&1; then
  echo "error: pdfx not on PATH (run INSTALL.sh or: ln -sf \$PWD/pdfx.py ~/.local/bin/pdfx)" >&2
  exit 127
fi

mkdir -p "$OUT_DIR"
# page count
PAGES=$(pdfx "$PDF" --inspect 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['pages'])")
if [[ -z "$END" ]]; then END="$PAGES"; fi
END=$(( END > PAGES ? PAGES : END ))

echo "# batch start $(date -Iseconds) pdf=$PDF pages=${START}-${END} chunk=$CHUNK engine=$ENGINE dpi=$DPI" | tee -a "$LOG"

a="$START"
while (( a <= END )); do
  b=$(( a + CHUNK - 1 ))
  (( b > END )) && b=$END
  tag=$(printf '%03d-%03d' "$a" "$b")
  out="${OUT_DIR}/chunk_${tag}.txt"
  meta="${OUT_DIR}/chunk_${tag}.meta.json"
  if [[ -s "$out" ]]; then
    echo "# skip existing $out" | tee -a "$LOG"
    a=$(( b + 1 ))
    continue
  fi
  render="${TMPDIR:-/tmp}/pdfx-batch-$$-${tag}"
  t0=$(date +%s)
  set +e
  pdfx "$PDF" --mode fraktur --pages "${a}-${b}" --engine "$ENGINE" --dpi "$DPI" \
    --out "$out" --render-dir "$render" >>"$LOG" 2>&1
  ec=$?
  set -e
  t1=$(date +%s)
  wall=$(( t1 - t0 ))
  rm -rf "$render" 2>/dev/null || true
  chars=0
  [[ -f "$out" ]] && chars=$(wc -c <"$out" | tr -d ' ')
  # craft hits (generic DE craft lexicon; override via PDFX_CRAFT_TERMS later if needed)
  python3 - "$out" "$meta" "$a" "$b" "$wall" "$ec" "$ENGINE" <<'PY'
import json, re, sys
from pathlib import Path
path, meta, a, b, wall, ec, eng = sys.argv[1:8]
text = Path(path).read_text(encoding="utf-8", errors="replace") if Path(path).is_file() else ""
terms = ["Dach","Schiefer","Ziegel","Latte","Matthaey","Blech","Stroh","Bauherr","Seil","Leiter","Fahrstuhl","Lenkhaken","Vorwort"]
counts = {t: len(re.findall(re.escape(t), text, re.I)) for t in terms}
distinct = sum(1 for v in counts.values() if v > 0)
total = sum(counts.values())
warn = distinct < 3 or total < 5
obj = {
  "pages": [int(a), int(b)],
  "wall_sec": int(wall),
  "exit_code": int(ec),
  "chars": len(text),
  "engine": eng,
  "craft_counts": counts,
  "craft_distinct": distinct,
  "craft_total": total,
  "warn_low_craft": warn,
}
Path(meta).write_text(json.dumps(obj, indent=2), encoding="utf-8")
print(json.dumps({"tag": f"{a}-{b}", **{k: obj[k] for k in ("wall_sec","chars","craft_distinct","craft_total","warn_low_craft","exit_code")}}))
PY
  if [[ $ec -ne 0 ]]; then
    echo "# FAIL chunk $tag exit=$ec — stopping" | tee -a "$LOG"
    exit $ec
  fi
  a=$(( b + 1 ))
done

echo "# batch done $(date -Iseconds)" | tee -a "$LOG"
# optional concat
cat_out="${OUT_DIR}/full_fraktur_concat.txt"
: > "$cat_out"
for f in $(ls "$OUT_DIR"/chunk_*.txt 2>/dev/null | sort); do
  echo -e "\n\n##### FILE $(basename "$f") #####\n" >>"$cat_out"
  cat "$f" >>"$cat_out"
done
echo "# concat -> $cat_out ($(wc -c <"$cat_out") bytes)" | tee -a "$LOG"
