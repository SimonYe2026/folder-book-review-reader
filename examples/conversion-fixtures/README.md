# Conversion Fixtures

Put complex source documents here when testing optional converters.

Suggested layout:

```text
examples/conversion-fixtures/
  source/
    sample.docx
  converted/
    sample.docx.md
```

Do not commit private or sensitive documents.

The core reader does not read this directory directly. Converter tests can use it to verify extraction, paragraph repair, table handling, and desensitization behavior.

## Current Fixtures

```text
source/
  complex_layout_review_reader_test.docx
converted/
  complex_layout_review_reader_test.docx.md
```

This fixture is intended to test the current recommended DOCX conversion path. It should be used to test:

- paragraph extraction;
- table preservation;
- heading detection;
- reviewable block boundaries;
- optional desensitization behavior.

Regenerate converted outputs with:

```powershell
python tools/convert_docs.py examples/conversion-fixtures/source -o examples/conversion-fixtures/converted
```

Build a reader for the converted outputs with:

```powershell
python build_reader.py workspace.converted.config.md
```

The generated file is:

```text
output/reader.converted.html
```
