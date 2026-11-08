# Fonts

Self-hosted, SIL Open Font License 1.1 (license texts beside each family).

| File | Family | Source | Processing |
|---|---|---|---|
| Newsreader-Variable.woff2, Newsreader-Italic-Variable.woff2 | Newsreader (Production Type) | Google Fonts latin build, v26 | Variable axes narrowed with fontTools to the ranges the stylesheet uses: weight 400 to 700, optical size 16 to 72 (both axes kept, so `font-optical-sizing: auto` still works). Full-range files are 132 and 147 KB; these are 88 and 98 KB. |
| LibreFranklin-Variable.woff2, LibreFranklin-Italic-Variable.woff2 | Libre Franklin (Impallari Type) | Google Fonts latin build, v20 | As served (weight 300 to 900). |

Licenses: `OFL-Newsreader.txt` (Copyright 2020 The Newsreader Project Authors), `OFL-LibreFranklin.txt` (Copyright 2015 Impallari Type). Neither declares a Reserved Font Name in its copyright header; the font family names were left unchanged. To regenerate from the full files, download the latin woff2 from the Google Fonts CSS API and run fontTools `varLib.instancer` with `wght=400:700 opsz=16:72`.
