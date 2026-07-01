# Release Checklist

This file records checks that should be completed or confirmed before release.

Chinese counterpart: `02-release-checklist.zh-CN.md`

## Build Checks

- Build the default Chinese reader:

```powershell
python build_reader.py workspace.config.md --overwrite
```

- Build the English UI reader:

```powershell
python build_reader.py workspace.en.config.md --overwrite
```

- Build the converter sample reader:

```powershell
python build_reader.py workspace.converted.config.md --overwrite
```

- Build the documentation status reader:

```powershell
python build_reader.py workspace.docs.config.md --overwrite
```

## Automated Tests

- Run the smoke test:

```powershell
python tests/smoke_test.py
```

The current smoke test covers:

- Config parsing.
- Basic Markdown/TXT rendering.
- TXT rendering does not activate HTML, Markdown links, or image syntax.
- Disabled links and localized placeholders.
- Common raster image data URLs still render.
- SVG data images are disabled.
- Image data URLs not being corrupted by inline formatting.
- Invalid `docx-table` fallback to code blocks.
- Script-safe JSON escaping for embedded reader data.
- `dry-run` writing no files.
- `overwrite: false` preserving existing output.
- Clear errors for missing `source_dir`.
- Clear errors for empty or non-matching source folders.
- Main reader, English reader, documentation reader, and converted reader builds.
- Basic DOCX converter quality.
- Recursive conversion without overwriting duplicate file names.
- Selected generated demo HTML files exist and do not contain local absolute paths or private review markers.

## Manual Checks

- Three-column layout works on wide, half-width, and narrow screens.
- Contents and review panels do not cover the reader after collapsing.
- Previous/next navigation follows the current filter.
- Font size, reading width, theme, and panel widths persist after refresh.
- Review dialog can add review notes.
- Review board can edit, delete, and clear review notes.
- Copied and downloaded `review.md` is grouped by file.
- Downloaded `review.md` can be repackaged as a normal Markdown reader.
- Link placeholders, image display, and converted inline styles look correct in the browser.

## Safety Checks

- The build process does not modify source files.
- The browser reader does not write back to source files.
- Markdown links do not generate clickable `<a href=...>` elements.
- TXT content is escaped as text and does not activate HTML or Markdown syntax.
- Generated HTML contains source content, and README explains the sensitive-content risk.
- Optional converters read source documents and write converted outputs only.
- README and security notes warn against packaging Markdown/TXT from unknown sources or running optional converters on unknown Office documents.

## Known Current Limits

- The DOCX converter is suitable for basic text, headings, lists, tables, images, and some inline styles, but it does not guarantee complex layout fidelity.
- Exported `review.md` is review text, not a reversible structure file.
- Complex charts, ASCII diagrams, and flowcharts are displayed as content rather than automatically redrawn.
- Links are disabled by default as a safety tradeoff; this is not a Markdown site generator.

## Before Release

- Do not commit the entire routine `output/` build folder.
- If the repository needs browser-ready HTML examples, commit selected regenerated demo files under a deliberate location such as `examples/generated/`, and document the source config and build command.
- Keep test fixtures small and readable.
- Keep README Chinese-first with English internationalization notes.
- Do not put development governance logs or personal work records into the open-source folder.
- Confirm the MIT `LICENSE` file is present.
- Run the smoke test again before publishing.
