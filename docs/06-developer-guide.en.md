# Developer Guide: Architecture and Extension Paths

This document is for people who want to modify, embed, or continue developing the project. It describes the current architecture, stable boundaries, and recommended extension order. It does not mean that every direction is on the release roadmap.

Chinese counterpart: `06-developer-guide.zh-CN.md`

## Current Stable Baseline

```text
config/workspace.config.md
  -> build_reader.py scans, parses, and packages files
  -> one self-contained reader.html
  -> the browser reads, filters, reviews, and exports review.md
```

Python owns file-system access and generation. The browser only handles data already packaged into the page. The reader does not use the network, write back to source files, or call AI directly.

## Main Code Boundaries

`build_reader.py` currently contains four kinds of responsibility:

1. configuration parsing and path safety checks;
2. file scanning, sorting, and chapter-data generation;
3. safe Markdown/TXT-to-HTML conversion;
4. assembly of the HTML, CSS, and JavaScript application.

The optional DOCX converter lives in `tools/convert_docs.py`. It is a preprocessing step, and Office parsing should not be moved into the browser.

## Recommended Extension Order

### 1. Extend configuration first

UI labels, review actions, review targets, filtering rules, and display defaults should be extended through configuration first. A capability that can be expressed in configuration does not require a new runtime dependency.

### 2. Extend structured data next

Before adding reading or review behavior, define the fields required in chapter and review data, then change the UI. File paths, block numbers, quoted source text, and creation times are foundational fields for locating a review.

### 3. Split generated assets into source modules

If `build_reader.py` keeps growing, first move the template, CSS, and JavaScript into separate source files, then inline them during the build. This improves maintainability while preserving the one-command workflow and single-file output.

Suggested structure:

```text
build_reader.py
reader_src/
  template.html
  reader.css
  reader.js
```

### 4. Evaluate a frontend framework last

The native `<dialog>` element is sufficient for the review dialog. It already provides modality, focus management, Escape handling, and form semantics. A framework is not justified for the dialog alone.

If the review board gains more state, components, and localized updates, evaluate the official Vue production runtime. This means the slim production runtime published by Vue, not a locally modified Vue source tree. Pin the version and distribute it locally or inline it at build time so the output remains offline and self-contained.

jQuery simplifies some DOM syntax but does not solve reactive state or component-boundary problems, so it is not the recommended evolution path. Evaluate a UI component library only when the project genuinely needs many consistent complex controls.

## Directions Worth Exploring

- clearer Python module boundaries and separated template assets;
- componentization and more granular state updates for the review board;
- pluggable input converters with Markdown/TXT or an explicit intermediate structure as the common output;
- stronger keyboard and accessibility support;
- search performance and incremental rendering for large file collections;
- export-format adapters so different AI or team workflows can reuse the same review data.

Table polish, small statistics, and additional visual components are UI increments. They remain lower priority than the reading, filtering, review, and export path.

## Directions Not Recommended as Direct Extensions

- silently scanning or writing local files from the browser;
- calling AI APIs from the default reader;
- automatically merging AI results;
- parsing DOCX/PDF/EPUB directly in the browser;
- guessing and redrawing complex diagrams from character art;
- adding a complete frontend toolchain for one control.

These directions change the security boundary or product role. They belong in a separate branch, plugin, or project.

## Minimum Verification After Changes

Run at least:

```powershell
python tests\smoke_test.py
python tests\html_quality_check.py
python build_reader.py config/workspace.config.md --dry-run
python build_reader.py config/workspace.config.md --overwrite
```

`html_quality_check.py` is a static page-quality check. It does not launch a browser or simulate clicks. It checks generated HTML for complete page structure, chapter data, review hooks, navigation hooks, and safety boundaries. Browser click-flow tests can be added later as a higher-level test layer.

For frontend interaction changes, also verify manually:

- previous/next navigation stays inside filtered results;
- collapsing the table of contents or review board does not collapse the reader;
- review-board updates do not interrupt Chinese IME composition;
- settings and reviews recover from localStorage after refresh;
- a downloaded `review.md` can be repackaged and read as ordinary Markdown;
- untrusted links stay disabled and text or embedded data cannot become executable script.

## Compatibility Principles

A good extension should preserve, where possible:

- one Python command for the build;
- self-contained HTML output;
- offline operation with no telemetry or network dependency by default;
- read-only source files and side-channel review export;
- correspondence between the default Chinese UI and English internationalization files;
- examples, documentation, and regression tests for new behavior.

Preserve these properties before adding technical layers. The value of this project is not the number of frameworks it uses, but the reliable small loop it creates between local documents, human judgment, and later AI-assisted work.
