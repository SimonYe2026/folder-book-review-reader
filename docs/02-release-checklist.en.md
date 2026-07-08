# Release Checklist

This file records checks that should be completed or confirmed before release.

Chinese counterpart: `02-release-checklist.zh-CN.md`

## Build Checks

- Build the default Chinese reader:

```powershell
python build_reader.py config/workspace.config.md --overwrite
```

- Build the English UI reader:

```powershell
python build_reader.py config/workspace.en.config.md --overwrite
```

- Build the converter sample reader:

```powershell
python build_reader.py config/workspace.converted.config.md --overwrite
```

- Build the documentation status reader:

```powershell
python build_reader.py config/workspace.docs.config.md --overwrite
```

- Build the English UI documentation status reader:

```powershell
python build_reader.py config/workspace.docs.en.config.md --overwrite
```

- Refresh selected public demo HTML files:

```powershell
python tools/build_demos.py
```

## Automated Tests

- Run the smoke test:

```powershell
python tests/smoke_test.py
```

- Run the generated HTML quality check directly if needed:

```powershell
python tests/html_quality_check.py
```

- If the release changes frontend interaction, review dialogs, filtered navigation, or CSV row review, also run the dynamic browser check:

```powershell
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tests/browser_smoke_test.py
```

- GitHub Actions runs the same smoke test on push, pull request, or manual dispatch:

```text
.github/workflows/smoke.yml
```

The current smoke test covers:

- Config parsing.
- Basic Markdown/TXT rendering.
- CSV parsing, table rendering, dangerous-cell escaping, and row-level review anchors.
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
- Main reader, English reader, Chinese/English documentation readers, and converted reader builds.
- Root-level and `config/` centralized config template dry-runs.
- Basic DOCX converter quality.
- Recursive conversion without overwriting duplicate file names.
- Generated HTML page structure, embedded data, review hooks, navigation hooks, and safety patterns.
- Selected generated demo HTML files exist and do not contain local absolute paths or private review markers.
- README generated-demo links point to checked-in files.

## Manual Checks

- Three-column layout works on wide, half-width, and narrow screens.
- Contents and review panels do not cover the reader after collapsing.
- Previous/next navigation follows the current filter.
- Font size, reading width, theme, and panel widths persist after refresh.
- Review dialog can add review notes.
- When browser selection mini menus appear, such as in Edge, the floating review button still works as an alternative to the `R` shortcut.
- Review board can edit, delete, and clear review notes.
- CSV demo scrolls horizontally, search can match cells, and row-level review export shows `row N`.
- Copied and downloaded `review.md` is grouped by file.
- Downloaded `review.md` can be repackaged as a normal Markdown reader.
- Link placeholders, image display, and converted inline styles look correct in the browser.

## GitHub Pages Checks

If GitHub Pages is enabled, open these pages after pushing:

- Chinese basic demo: `https://simonye2026.github.io/folder-book-review-reader/examples/generated/basic-reader.demo.html`
- English basic demo: `https://simonye2026.github.io/folder-book-review-reader/examples/generated/basic-reader.en.demo.html`
- Chinese project docs demo: `https://simonye2026.github.io/folder-book-review-reader/examples/generated/project-docs.demo.html`
- English project docs demo: `https://simonye2026.github.io/folder-book-review-reader/examples/generated/project-docs.en.demo.html`

For each public demo, confirm:

- Search works.
- Previous/next follows the current filter.
- The review dialog opens.
- `review.md` can be copied or downloaded.

## Safety Checks

- The build process does not modify source files.
- The browser reader does not write back to source files.
- Markdown links do not generate clickable `<a href=...>` elements.
- TXT content is escaped as text and does not activate HTML or Markdown syntax.
- CSV cells are shown as table text, and HTML or formula-like values are not executed.
- Generated HTML contains source content, and README explains the sensitive-content risk.
- Optional converters read source documents and write converted outputs only.
- README and security notes warn against packaging Markdown/TXT/CSV from unknown sources or running optional converters on unknown Office documents.

## Known Current Limits

- The DOCX converter is suitable for basic text, headings, lists, tables, images, and some inline styles, but it does not guarantee complex layout fidelity.
- Exported `review.md` is review text, not a reversible structure file.
- Complex charts, ASCII diagrams, and flowcharts are displayed as content rather than automatically redrawn.
- Links are disabled by default as a safety tradeoff; this is not a Markdown site generator.

## Before Release

- Do not commit the entire routine `output/` build folder.
- If the repository needs browser-ready HTML examples, commit selected regenerated demo files under a deliberate location such as `examples/generated/`, and document the source config and build command.
- Keep `examples/generated/basic-reader.demo.html`, `examples/generated/basic-reader.en.demo.html`, `examples/generated/project-docs.demo.html`, and `examples/generated/project-docs.en.demo.html` refreshed together before release.
- Keep test fixtures small and readable.
- Keep README Chinese-first with English internationalization notes.
- Do not put development governance logs or personal work records into the open-source folder.
- Confirm the MIT `LICENSE` file is present.
- Run the smoke test again before publishing.
- After pushing, confirm the GitHub Actions `Smoke Test` passes.
