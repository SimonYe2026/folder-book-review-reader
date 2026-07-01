# Optional Tools

This directory is reserved for optional preprocessors.

The core reader does not require any converter. It reads Markdown and TXT files directly.

Potential future tools:

- `convert_docs.py`: recommended `.docx` to Markdown conversion.
- Desensitization before packaging.
- Paragraph normalization for converted documents.

Keep these tools separate from the reader core so the main project remains easy to run.

## Convert Fixtures

```powershell
python tools/convert_docs.py examples/conversion-fixtures/source -o examples/conversion-fixtures/converted
```

Quality note:

- `.docx` is the current recommended path.
- The converter preserves headings, lists, paragraph breaks, tables, code blocks, character art, common inline formatting, and embedded images where the DOCX structure exposes them.
- Embedded images are written as data URLs so the generated reader can remain self-contained.
- It does not reproduce Word pagination, floating-object placement, or every Word style.
- `.doc`, `.rtf`, PDF, and EPUB are not part of the current OSS converter.
