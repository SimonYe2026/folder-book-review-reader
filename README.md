# Local Markdown/TXT Review Reader

A small local-first reader for reviewing folders of Markdown and TXT files.

The default demo UI is Chinese (`locale: zh-CN`). English is available as an internationalized config through `workspace.en.config.md`.

It builds one self-contained `reader.html` that can be opened in a browser. The reader supports search, filtered navigation, adjustable layout, dark mode, and a local review board that exports grouped `review.md`.

## Quick Start

```powershell
python build_reader.py workspace.config.md
```

English UI example:

```powershell
python build_reader.py workspace.en.config.md
```

Open:

```text
output/reader.html
```

Optional local preview:

```powershell
python serve_reader.py
```

Run the smoke test:

```powershell
python tests/smoke_test.py
```

Build the documentation reader:

```powershell
python build_reader.py workspace.docs.config.md
```

Open:

```text
output/project-docs.html
```

Browser-ready demos are kept in `examples/generated/` for users who want to inspect the reader before running commands:

- `examples/generated/basic-reader.demo.html`
- `examples/generated/project-docs.demo.html`

## What It Does

- Reads `.md` and `.txt` files from a configured folder.
- Builds a single self-contained HTML reader.
- Keeps source files read-only.
- Lets you search title, file path, and content.
- Navigates within the current filtered result set.
- Supports font size, reading width, theme, and draggable side panel widths.
- Supports configurable TXT paragraph mode.
- Supports configurable UI labels.
- Lets you select text or a paragraph and add review notes.
- Saves review notes in `localStorage`.
- Exports grouped `review.md`.

## Expected Workflow

```text
create or collect files from any workflow
  -> build reader.html with this script
  -> read, filter, and review locally
  -> copy or download review.md
  -> send review.md to AI or use it as a manual checklist
  -> let AI or the user edit source files outside the reader
  -> build reader.html again to inspect the revised result
```

The reader itself does not call AI and does not modify source files. It creates a side-channel review file that is easy for AI tools or humans to process.

## Embed in Another Project

This repository can be used as a complete demo, but the core tool is intentionally small enough to copy into another project.

For a minimal integration, copy:

- `build_reader.py`
- a `workspace.config.md` adapted to your folder

Optional pieces:

- `serve_reader.py` for local preview
- `tools/convert_docs.py` if you need the DOCX conversion path
- `tests/smoke_test.py` if you want regression checks

The host project can keep its own documents, AI outputs, drafts, or review files. The reader only needs a configured source folder and an output path.

Recommended embedded flow:

```text
your project files
  -> build_reader.py
  -> local reader.html
  -> human review
  -> review.md
  -> AI-assisted edits outside the reader
  -> rebuild reader.html
```

## What It Does Not Do

- It does not call AI APIs.
- It does not edit source files from the browser.
- It does not merge AI results.
- It does not require React, Vue, npm, or a frontend build chain.
- It does not parse Office/PDF files in the browser.

## Optional Converters

The core reader intentionally accepts Markdown and TXT only.

For non-Markdown sources, use an optional converter first:

```text
source document -> converter -> md/txt -> build_reader.py -> reader.html
```

Current confidence levels:

- `.docx`: recommended optional conversion path.
- `.doc` / `.rtf` / `.pdf` / `.epub`: future directions, not current commitments.

Current converter command:

```powershell
python tools/convert_docs.py examples/conversion-fixtures/source -o examples/conversion-fixtures/converted
```

## Safety

The generated HTML contains the source text. Do not share `reader.html` publicly if the source files contain sensitive information.

The browser reader does not write back to source files.

The project includes protections such as disabled Markdown links, escaped TXT rendering, script-safe embedded JSON, and restricted image data URLs. Even so, do not package Markdown/TXT files from unknown sources, and do not run optional converters on unknown Office documents. Review unfamiliar text files in a plain text editor first.

## License

MIT License. See `LICENSE`.

## More Documentation

- `docs/01-project-status.en.md` / `docs/01-project-status.zh-CN.md`: project status, boundaries, and non-goals.
- `docs/02-release-checklist.en.md` / `docs/02-release-checklist.zh-CN.md`: release checks and test coverage.
- `docs/03-customization-guide.en.md` / `docs/03-customization-guide.zh-CN.md`: customization guide for contributors.
- `docs/04-user-manual.en.md` / `docs/04-user-manual.zh-CN.md`: user manual, shortcuts, review board, and export flow.
- `docs/05-security-notes.en.md` / `docs/05-security-notes.zh-CN.md`: security model, protections, and unsafe input guidance.
- `docs/06-developer-guide.en.md` / `docs/06-developer-guide.zh-CN.md`: code architecture, extension order, framework guidance, and regression requirements.
