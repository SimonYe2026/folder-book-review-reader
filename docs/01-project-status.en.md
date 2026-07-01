# Project Status

This file describes the current scope, completed capabilities, boundaries, and future directions of Local Markdown/TXT Review Reader.

Chinese counterpart: `01-project-status.zh-CN.md`

## Current Positioning

This project is a local-first Markdown/TXT review reader.

Its core use cases are:

- Package a folder of `.md` / `.txt` files into one readable HTML file.
- Search, filter, and move through files in the browser.
- Select text or paragraphs and create review notes for AI-assisted or manual follow-up work.
- Export a grouped `review.md`.

It is not:

- A Markdown editor.
- An online AI client.
- A file manager.
- A knowledge base system.
- A documentation site generator.
- A universal multi-format converter.

## Stable Main Flow

The main flow is complete:

```text
Local Markdown/TXT folder
  -> build_reader.py
  -> output/reader.html
  -> browser reading, filtering, reviewing
  -> exported review.md
```

Repackaging `review.md` has also been verified:

```text
review.md
  -> re-enters the reader as normal Markdown
  -> used for rereading, archiving, or second-pass review
```

## Completed Capabilities

- Recursive or non-recursive `.md` / `.txt` scanning.
- Natural order, descending order, and modified-time order.
- Relative path, file name, extension, word count, and modified time metadata.
- Full-text search across title, path, file name, and content.
- Filtered results work as a temporary reading list; previous/next follows the active filter.
- Persistent font size, reading width, dark mode, and side panel widths.
- Collapsible contents panel and review panel.
- Paragraph-level and selected-text review notes.
- Review board editing, deletion, clearing, copying, and downloading.
- File-grouped `review.md` export.
- Basic rendering for Markdown tables, code blocks, quotes, lists, and images.
- Markdown links are disabled by default and replaced with a source-file notice.
- `dry-run`, non-overwriting output behavior, and clear config errors.
- Optional `.docx -> .md` converter.

## Safety Boundaries

This project is intentionally conservative:

- No network access.
- No uploads.
- No AI API calls.
- No browser write-back to source files.
- No deleting, moving, or renaming source files.
- No active Markdown links.
- No Office/PDF/EPUB parsing in the browser.

The generated HTML contains source file content. Do not publicly share generated HTML if the source files contain sensitive content.

## Current Non-Goals

- No guarantee of perfect complex DOCX layout preservation.
- No current commitment to `.doc` / `.rtf` / `.pdf` / `.epub` support.
- No automatic redrawing of charts, flowcharts, or ASCII diagrams.
- No AI result merging.
- No multi-user collaboration or cloud sync.

## Customization-Friendly Directions

This project is designed to be easy to adapt:

- Change UI labels and language.
- Change review actions and targets.
- Change reading layout widths.
- Change the exported `review.md` format.
- Add new file converters.
- Add new Markdown rendering rules.
- Add internal config templates for a team or personal workflow.

When customizing, keep three boundaries first:

- Source files stay read-only.
- The browser does not gain unnecessary local privileges.
- Generated content remains readable by normal AI tools and humans.

## Current Conclusion

The current version is ready for a basic open-source release.

It is not a large platform. It is a small and clear tool: turn a local Markdown/TXT folder into a continuous, filterable, reviewable browser reader, then export AI-friendly follow-up tasks.
