# Fraktur glyph templates (clean references)

**Purpose:** human + agent visual ground truth for German blackletter / Fraktur OCR.  
**Not** training weights — specimen charts for reading confusable glyphs and for QA.

Source: user-supplied clean examples (2026-08-25). Canonical store:

`~/src/pdf-extract/references/fraktur-templates/`

Mirrored into house skill `references/fraktur-templates/` and book plates folder.

## Catalog

| # | File | What it is | Best for |
|---|------|------------|----------|
| 01 | `01_deutsches_alphabet_in_fraktur.jpg` | Labeled A–Z chart “Das deutsche Alphabet in Fraktur” + long‑s **ſ**, **ß**, numerals | **Primary** letter ID chart |
| 02 | `02_pragmatopro_fraktur_regular_bold_v1.2.jpg` | PragmatoPro Fraktur Regular vs Bold, full glyph grid | Weight / punctuation / extended set |
| 03 | `03_humboldt_fraktur.jpg` | Humboldt Fraktur A–Z, äöüß, 0–9 | Modern specimen + umlauts |
| 04 | `04_moderne_fraktur.jpg` | Moderne Fraktur A–Z, äöüß, 0–9 | Cleaner “modern” Fraktur shapes |
| 05 | `05_berthold_mainzer_fraktur.jpg` | Berthold Mainzer Fraktur A–Z, äöüß, 0–9 | Classic Mainzer family |
| 06 | `06_wienyt_fraktur.jpg` | Wienyt Fraktur A–Z, äöüß, 0–9 | Alternate foundry cut |
| 07 | `07_mainzer_fraktur_bauer_berthold_historic.jpg` | Historic Bauer & Co. / H. Berthold **Mainzer Fraktur** foundry sheet; samples *Amsterdam · Mandoline · Robinson · Commission* | Period-accurate print style (closest to 19th‑c. books) |
| 08 | `08_ornate_blackletter_full_charset_grid.jpg` | Dense labeled grid: letters, digits, punctuation, currency | Symbols / edge glyphs |

## How agents should use these

1. **Before arguing a bad OCR token** on Fraktur print: open `01_…` (and `07_…` for period shape).
2. **Confusable pairs** to check against templates:
   - long‑s **ſ** vs f / t
   - capital **I / J / T**
   - **B / V / P**, **N / R**, **K / R**
   - **A** open form vs **U**
   - **ß** vs **ſs** / B
   - umlauts **ä ö ü** vs a/o/u + mark noise
3. **Do not** feed these into Kurrent/kraken (hand) models — print Fraktur → tesseract `deu+frk`.
4. **Do not** treat modern display Fraktur (03–06) as identical to 1820s book type; prefer **01 + 07** for Dachdecker-class scans.
5. For searchable body text still prefer the **ſ→s sidecar**; templates explain *why* OCR saw ſ.

## Vision prompt snippet

```
Compare the unclear glyph on the book scan to fraktur-templates/01 and 07.
Identify letter using the labeled Antiqua key under each Fraktur form.
```

## License note

Specimens are third-party font/foundry materials used here as **personal OCR reference**.  
Do not rebundle into a commercial font package. Public Hermes skill may **link** to this folder or ship only if redistribution of each specimen is cleared; default public tarball can omit binaries and keep this INDEX.

## Related

- Skill: `pdf-extract-ocr` / portable `pdfx`
- Book plates: `Documents/papers/books/google/AQKAAAAIAAJ/extract/plates/`
- Engine: `pdfx --mode fraktur` (tesseract `frk`)
