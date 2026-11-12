# Why a translated PDF can look readable but fail a text search

A PDF page can render correctly while its extracted text differs. This exercise uses a fictional one-page Spanish reading brief written by Scanfile and the **actual English result from 25 October 2026**. It is one historical example, not a test of current translations, other files or providers. Scanfile's developer maintains this repository; the separate translation service uploads your document and may use credits. This guide was prepared with AI assistance.

- [Spanish original](https://scanfile.online/samples/pdf/es-en/reading-brief.es.pdf)
- [Uncorrected English output](https://scanfile.online/samples/pdf/es-en/reading-brief.en.pdf)

Open them to compare layout and meaning. Then download the English output and inspect its first page with the repository's existing Python dependency, `pypdf`. Use your local filename in the command:

```sh
python -c "import sys; from pypdf import PdfReader; t=PdfReader(sys.argv[1]).pages[0].extract_text(); print('U+0003 count:',t.count(chr(3))); print('phrase found:', 'An hour of reading' in t); print('phrase found after replacing U+0003 with spaces:', 'An hour of reading' in t.replace(chr(3),' '))" reading-brief.en.pdf
```

In our check with pypdf 5.8.0, it reported **130** U+0003 control characters, did not find the ordinary phrase, and found it after replacing that character with a space in memory. PDF.js 6.3.289 also returned 130 such characters in the extracted first-page text. The PDF's embedded ToUnicode map lacked an entry for glyph code `0003`; this observation alone is not a complete diagnosis of every PDF viewer. Four other published translated examples we sampled had no U+0003 in their first-page PDF.js text; this is not a representative test. Some software may handle the file differently.

The code above does not write or repair the PDF, and replacing a control character in extracted text is not a general PDF fix. Inspect a short copy/paste from **your** output in your intended reader or reference manager. [Zotero’s search documentation](https://www.zotero.org/support/preferences/search) also recommends checking copied text when troubleshooting the PDF text index. Compare it with the original before quoting; read the complete passage and verify numbers, negation, citations and context. If text extraction matters and is incorrect, retain the original and seek a suitable searchable copy or a qualified review. Visual appearance alone does not establish reliable copying, search, translation accuracy or accessibility.

The original and output are available as a disclosed [real example on Scanfile](https://scanfile.online/tools/pdf-translator#spanish-english-example). No personal or customer document is included.
