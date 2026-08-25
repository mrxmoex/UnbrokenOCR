# Kraken HTR — German historical handwriting (local)

## Environment
```bash
source /home/mrxmoex/src/pdf-extract/.venv-kraken/bin/activate
# kraken 7.1
```

## Models (offline after download)

| File | Source | Use |
|------|--------|-----|
| `kraken_german_finetuned.mlmodel` | MGJamJam/htr_german_kurrent_model | **Best for 19c German Kurrent** (finetuned; ~97% on train GT) |
| `kraken_catmus_finetuned.mlmodel` | same repo | CATMuS finetuned on Kurrent |
| `kraken_from_scratch.mlmodel` | same repo | trained from scratch on Kurrent |
| `german_handwriting.mlmodel` | zenodo.7933463 | Broader German manuscript HTR |
| `fanny_20250228.mlmodel` | zenodo.18207676 | 19c Fanny Mendelssohn letters (German hand) |
| `McCATMuS_nfd_nofix_V1.mlmodel` | zenodo.13788177 | Multilingual HTR/OCR 16c–21c (incl. German) |
| `blla.mlmodel` | zenodo.14602569 | Baseline/region segmentation |

Also cached under `~/.local/share/htrmopo/<uuid>/` after `kraken get`.

## Recognition one-liners

**Full page** (segment + OCR):
```bash
kraken -d cpu \
  -i page.png out.txt \
  segment -bl -i /home/mrxmoex/src/pdf-extract/models/kraken/blla.mlmodel \
  ocr -m /home/mrxmoex/src/pdf-extract/models/kraken/kraken_german_finetuned.mlmodel
```

**Single line image** (no layout):
```bash
kraken -d cpu \
  -i line.png out.txt \
  ocr -m /home/mrxmoex/src/pdf-extract/models/kraken/kraken_german_finetuned.mlmodel -s
```

**ALTO / PageXML output** (add flag before commands):
```bash
kraken -d cpu -a -i page.png out.xml segment -bl -i .../blla.mlmodel ocr -m .../kraken_german_finetuned.mlmodel
# or -x for PageXML, -h for hOCR
```

**GPU** (if CUDA works): `-d cuda:0` instead of `-d cpu`.

## Re-download from repo
```bash
kraken get 10.5281/zenodo.7933463   # german_handwriting
kraken get 10.5281/zenodo.18207676  # Fanny Mendelssohn
kraken get 10.5281/zenodo.13788177  # McCATMuS
kraken get 10.5281/zenodo.14602569  # blla segmentation
kraken list -l deu                  # browse German models
```

## Pitfalls
- Models are for **handwriting (Kurrent)**, not modern print/Fraktur. Synthetic print smoke tests will look garbled — expected.
- Prefer **pre-segmented line crops** for best accuracy; page segmentation quality varies.
- Default device is `auto`; force `-d cpu` if CUDA/driver mismatch.
- Torch pulls large NVIDIA CUDA wheels even for CPU use (~GBs in venv).
- `kraken get` installs under `~/.local/share/htrmopo/`; copies here are for stable project paths.
- No Transkribus account needed; all models offline after download.
