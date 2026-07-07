# Local Markdown/TXT Review Reader

[中文说明](README.zh-CN.md)

A small local-first tool for reading and reviewing folders of Markdown/TXT files.

It turns a folder into one self-contained `reader.html`. Open that file in a browser, read across many files like a book, filter the current reading set, mark passages, and export a grouped `review.md` for AI-assisted or manual follow-up.

The default UI is Chinese (`locale: zh-CN`). English is available through `config/workspace.en.config.md`.

## Why Use It

This tool is useful when you have many local Markdown/TXT files from drafts, AI outputs, notes, converted documents, or project docs, and you want to:

- read them continuously without changing the source files;
- search and navigate within a temporary filtered reading list;
- collect review notes while reading;
- hand `review.md` to an AI assistant or use it as a manual checklist;
- rebuild the reader after the source files are edited elsewhere.

The reader itself does not call AI, edit source files, or merge AI results.

## Requirements

- Python 3.10 or newer.
- No `pip` install.
- No npm.
- No frontend framework.

The core reader uses only the Python standard library.

## Quick Start

Build the default Chinese demo:

```powershell
python build_reader.py
```

Open:

```text
output/reader.html
```

The default command uses `config/workspace.config.md`.

You can also keep a config beside the script and pass it explicitly:

```powershell
python build_reader.py workspace.config.md
```

This repository includes both patterns: `workspace.config.md` at the root as a simple single-config example, and `config/` for the multi-config demo setup.

Build the English demo:

```powershell
python build_reader.py config/workspace.en.config.md
```

Optional local preview:

```powershell
python serve_reader.py
```

## Configuration Paths

Paths are resolved from `workspace_root`.

If `workspace_root` is not set, it defaults to the folder containing the config file.

Both config layouts are valid.

Simple single-config layout:

```yaml
workspace_root: .
source_dir: ./examples/basic/drafts
output: ./output/reader.html
```

Centralized config folder layout:

```yaml
workspace_root: ..
source_dir: ./examples/basic/drafts
output: ./output/reader.html
```

Both `source_dir` and `output` must stay inside `workspace_root`. This keeps the build scope clear when the script is copied into another project.

This repository uses the centralized layout because it keeps several demo and documentation configs in `config/`. For a small project with only one config, keeping `workspace.config.md` beside `build_reader.py` is still fine.

## Expected Workflow

```text
collect or generate Markdown/TXT files
  -> build reader.html
  -> read, filter, and review locally
  -> copy or download review.md
  -> send review.md to AI or use it as a manual checklist
  -> edit source files outside the reader
  -> rebuild reader.html to inspect the revised result
```

## What It Does

- Reads `.md` and `.txt` files from a configured folder.
- Builds a single self-contained HTML reader.
- Keeps source files read-only.
- Searches title, file name, relative path, and content.
- Navigates previous/next within the current filtered result set.
- Supports font size, reading width, theme, and draggable side panel widths.
- Supports configurable TXT paragraph mode.
- Supports configurable UI labels.
- Lets you select text or a paragraph and add review notes.
- Saves review notes in `localStorage`.
- Exports grouped `review.md`.

## What It Does Not Do

- It does not call AI APIs.
- It does not write back to source files from the browser.
- It does not merge AI results.
- It does not require React, Vue, npm, or a frontend build chain.
- It does not parse Office/PDF files in the browser.

## Online Demos

GitHub Pages demos:

- Chinese basic demo: `https://simonye2026.github.io/folder-book-review-reader/examples/generated/basic-reader.demo.html`
- English basic demo: `https://simonye2026.github.io/folder-book-review-reader/examples/generated/basic-reader.en.demo.html`
- Chinese project docs demo: `https://simonye2026.github.io/folder-book-review-reader/examples/generated/project-docs.demo.html`
- English project docs demo: `https://simonye2026.github.io/folder-book-review-reader/examples/generated/project-docs.en.demo.html`

The same browser-ready demo files are checked into `examples/generated/`.

## Embed in Another Project

For a minimal integration, copy:

- `build_reader.py`

Then choose one config layout:

- Single-config layout: copy `workspace.template.config.md`, then rename it to `workspace.config.md`.
- Centralized config layout: copy `config/workspace.template.config.md`, then rename it to `config/workspace.config.md`.

Optional pieces:

- `serve_reader.py` for local preview
- `tools/convert_docs.py` for the optional DOCX conversion path
- `tests/smoke_test.py` for regression checks

Recommended embedded flow:

```text
your project files
  -> build_reader.py
  -> workspace.config.md or config/workspace.config.md
  -> local reader.html
  -> human review
  -> review.md
  -> AI-assisted edits outside the reader
  -> rebuild reader.html
```

## Optional Converters

The core reader intentionally accepts Markdown and TXT only.

For non-Markdown sources, convert first:

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

## Development

Run the smoke test before changing or publishing the project:

```powershell
python tests/smoke_test.py
```

Check generated HTML page quality directly:

```powershell
python tests/html_quality_check.py
```

Refresh checked-in demo HTML files:

```powershell
python tools/build_demos.py
```

Routine files under `output/` are local build outputs and should stay uncommitted. Public demo HTML belongs in `examples/generated/`.

GitHub Actions runs the smoke test on push and pull request.

## Safety

Generated HTML contains the source text. Do not share `reader.html` publicly if the source files contain sensitive information.

The browser reader does not write back to source files.

Markdown links are disabled by default. TXT content is escaped. Embedded JSON is script-safe. Image data URLs are restricted to common raster formats.

Even with these protections, do not package Markdown/TXT files from unknown sources, and do not run optional converters on unknown Office documents. Review unfamiliar text files in a plain text editor first.

## License

MIT License. See `LICENSE`.

## More Documentation

- `docs/01-project-status.en.md` / `docs/01-project-status.zh-CN.md`: project status, boundaries, and non-goals.
- `docs/02-release-checklist.en.md` / `docs/02-release-checklist.zh-CN.md`: release checks and test coverage.
- `docs/03-customization-guide.en.md` / `docs/03-customization-guide.zh-CN.md`: customization guide.
- `docs/04-user-manual.en.md` / `docs/04-user-manual.zh-CN.md`: user manual, shortcuts, review board, and export flow.
- `docs/05-security-notes.en.md` / `docs/05-security-notes.zh-CN.md`: security model and unsafe input guidance.
- `docs/06-developer-guide.en.md` / `docs/06-developer-guide.zh-CN.md`: code architecture and extension guidance.
