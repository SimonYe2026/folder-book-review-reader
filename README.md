# Local Markdown/TXT/CSV Review Reader

[中文说明](README.zh-CN.md)

A small local-first tool for reading and reviewing folders of Markdown/TXT/CSV files.

It turns a folder into one self-contained `reader.html`. Open that file in a browser, read across many files like a book, filter the current reading set, mark passages, and export a grouped `review.md` for AI-assisted or manual follow-up.

The default UI is Chinese (`locale: zh-CN`). English is available through `config/workspace.en.config.md`.

## Why Use It

This tool is useful when you have many local Markdown/TXT/CSV files from drafts, AI outputs, notes, tabular checklists, converted documents, or project docs, and you want to:

- read them continuously without changing the source files;
- search and navigate within a temporary filtered reading list;
- collect review notes while reading;
- hand `review.md` to an AI assistant or use it as a manual checklist;
- rebuild the reader after the source files are edited elsewhere.

The reader itself does not call AI, edit source files, or merge AI results.

## Review Handoff Packages

When one review round involves dozens, or even ninety-plus, files, a zip archive or shared folder only delivers files. Reviewers still need to understand the directory, open files one by one, remember locations, and send fragmented feedback. `reader.html` turns that collection into one browser-ready review space: continuous reading, filtering, block-level review notes, and review-board follow-up all live in the same package.

The exported `review.md` is more than a general comment list. It retains the file path, content-block position, original quote, action, target, and instruction, so a central owner can return each note to the right context for manual maintenance or an external AI workflow. The flow solves four practical problems: distribute a large file set; inspect it in one place; leave precise notes on specific locations; and return structured feedback.

This is also the foundation for multi-party review collaboration: a coordinator packages separate `reader.html` files for different batches, roles, or viewing scopes; reviewers return their own `review.md` files; and a central owner or later AI process consolidates the feedback and decides on changes. The collaboration unit is a located review note, not shared source editing or synchronized browser state.

Several reviewers or a small team can use this flow directly. As reviewer count, batches, and rounds grow, assignment scope, file naming, reviewer identity, deadlines, and centralized collection keep the handoff clear. These can be handled with a simple table and agreed conventions. The reader provides the packaging, location, and return layer; source files and final acceptance remain with the central owner.

The builder needs Python to create a review package, but review participants do not. Review participants only read, make judgments, leave notes, and export `review.md`; packaging, intake/merging, AI handling, source edits, and final acceptance remain on the central side. They do not need AI knowledge, prompt-writing skill, Python, a code repository, source folders, or project dependencies. After receiving the file, they only need a modern browser to open `reader.html`. This lowers participation from operating a text-processing toolchain to opening a browser and contributing judgment.

## Requirements

- Python 3.10 or newer.
- No `pip` install.
- No npm.
- No frontend framework.

The core reader uses only the Python standard library.

The Python requirement applies to builders only. Reviewers who receive a generated `reader.html` only need a modern browser.

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

Multiple configs are useful not only for different source folders, but also for preparing separate review packages for different batches or viewing scopes within one project. Each config can have its own `source_dir`, matching rules, and `output`. This lets a coordinator distribute separate review views by topic, role, round, or delivery scope. Sensitive content should never be packaged into an HTML file sent to a reviewer; hiding content in the browser is not access control.

## Expected Workflow

```text
collect or generate Markdown/TXT/CSV files
  -> build reader.html
  -> read, filter, and review locally
  -> copy or download review.md
  -> send review.md to AI or use it as a manual checklist
  -> edit source files outside the reader
  -> rebuild reader.html to inspect the revised result
```

## What It Does

- Reads `.md`, `.txt`, and `.csv` files from a configured folder.
- Builds a single self-contained HTML reader.
- Keeps source files read-only.
- Searches title, file name, relative path, and content.
- Renders CSV files as HTML tables and supports row-level review notes.
- Navigates previous/next within the current filtered result set.
- Supports font size, reading width, theme, and draggable side panel widths.
- Supports configurable TXT paragraph mode.
- Supports configurable UI labels.
- Lets you select text or a paragraph and add review notes.
- With no selected text, bookmarks and review notes target the content block nearest the visible reader center; CSV keeps its active-row priority.
- Supports content-block bookmarks, including return navigation and removal from the bookmarks view.
- Distinguishes precise selected/block review from viewport review, and exports bounded nearby context so later human or AI recheck does not have to infer an entire chapter from one anchor quote.
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

The core reader intentionally accepts Markdown, TXT, and CSV.

For other source formats, convert first:

```text
source document -> converter -> md/txt/csv -> build_reader.py -> reader.html
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

When changing frontend interaction, install the development dependency and run the real browser click-flow check:

```powershell
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tests/browser_smoke_test.py
```

This dynamic script opens the Chinese and English public demos in Chromium and checks filtering and sorting, CSV-row and ordinary-block review, no-selection visual-center targeting for bookmarks and review notes, nearby-context export, review-board editing/copying/downloading/deleting/clearing, review and bookmark return navigation, localStorage recovery, reading preferences, side panels, and basic narrow-screen behavior. It is a development check, not a runtime dependency for ordinary reader use.

Refresh checked-in demo HTML files:

```powershell
python tools/build_demos.py
```

Routine files under `output/` are local build outputs and should stay uncommitted. Public demo HTML belongs in `examples/generated/`.

GitHub Actions runs the smoke test on push and pull request.

## Safety

Generated HTML contains the source text. Do not share `reader.html` publicly if the source files contain sensitive information.

The browser reader does not write back to source files.

Markdown links are disabled by default. TXT content is escaped. CSV cells are escaped as plain table text, and formula-like values are not executed. Embedded JSON is script-safe. Image data URLs are restricted to common raster formats.

Even with these protections, do not package Markdown/TXT/CSV files from unknown sources, and do not run optional converters on unknown Office documents. Review unfamiliar text files in a plain text editor first.

## License

MIT License. See `LICENSE`.

## More Documentation

- `docs/01-project-status.en.md` / `docs/01-project-status.zh-CN.md`: project status, boundaries, and non-goals.
- `docs/02-release-checklist.en.md` / `docs/02-release-checklist.zh-CN.md`: release checks and test coverage.
- `docs/03-customization-guide.en.md` / `docs/03-customization-guide.zh-CN.md`: customization guide.
- `docs/04-user-manual.en.md` / `docs/04-user-manual.zh-CN.md`: user manual, shortcuts, review board, and export flow.
- `docs/05-security-notes.en.md` / `docs/05-security-notes.zh-CN.md`: security model and unsafe input guidance.
- `docs/06-developer-guide.en.md` / `docs/06-developer-guide.zh-CN.md`: code architecture and extension guidance.
- `docs/07-review-handoff-workflow.en.md` / `docs/07-review-handoff-workflow.zh-CN.md`: review handoff, package scopes, and multi-party return workflow.
