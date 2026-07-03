# Security Notes

This file explains the project's security model, current protections, and remaining user responsibilities.

Chinese counterpart: `05-security-notes.zh-CN.md`

## Basic View

This tool is a local-first reader that keeps source files read-only.

It includes multiple protections, but users should not package and open Markdown/TXT files from unknown sources.

The reason is simple: the build process places input file content into a browser page. Even with escaping, disabled links, and image restrictions, unknown input can still cause display issues, performance pressure, misleading content, or untested edge cases.

## Current Protections

The current version includes these protections:

- Source files are read-only; the build process does not modify source chapters.
- `source_dir` and `output` are resolved from `workspace_root` and must stay inside it.
- Markdown links do not generate clickable `<a href=...>` elements by default.
- Links are replaced with a notice such as "Unknown link, check the source file".
- Image URLs reject protocols such as `javascript:`.
- `data:image/...` is limited to common raster image types: png, jpg, jpeg, gif, webp.
- JSON embedded inside `<script>` escapes `<`, `>`, and `&`, preventing `</script>` injection.
- Invalid `docx-table` blocks fall back to code blocks instead of breaking the build.
- `dry-run` lets users inspect the read scope before writing output.
- `overwrite: false` avoids replacing existing outputs.

## Protection Boundaries for MD, TXT, and DOCX

These protections are not limited to Markdown.

Content that enters the reader is protected by the final HTML packaging layer:

- `.md`: rendered by the basic Markdown renderer. Links are disabled, images are restricted, and embedded JSON is safely escaped.
- `.txt`: Markdown is not interpreted. Text is HTML-escaped directly. Even `<script>`, `[link](javascript:...)`, or image syntax is shown as plain text.
- `.docx`: not read directly by the browser. It must first be converted into `.md`, then it enters the same Markdown reader protections.

One important boundary remains: the DOCX converter is a conversion stage, not the browser reading stage.

The more accurate statement is:

```text
TXT is more conservative inside the reader;
MD is rendered with restrictions inside the reader;
DOCX receives the same reader protections after conversion to MD, but unknown Office files are still not recommended at the converter stage.
```

## Unknown Input Is Still Not Recommended

Prefer packaging Markdown/TXT that you created, downloaded from a verified source, or received from a trusted collaborator.

Avoid directly packaging:

- Markdown from unknown sources.
- TXT from unknown sources.
- Unreviewed bulk AI-generated files.
- DOCX or other Office documents from unknown sources.
- Large copied content from web pages, email, or chat tools.
- Files with extremely long lines, huge base64 payloads, or abnormal nested tables.
- Data that you do not want exposed inside a browser page.

Even if these inputs do not execute scripts, they may still cause:

- Oversized pages.
- Browser slowdown.
- Misleading content.
- Difficult search and review positioning.
- Unknown rendering edge cases.

## Generated HTML Contains Content

Generated `reader.html` is a packaged content file, not an empty index.

If source files contain sensitive information, the generated HTML also contains that information.

Do not upload sensitive generated HTML to public platforms, and do not send it to people who should not see the source content.

## localStorage Notes

Reading preferences and review notes are saved in browser `localStorage`.

This means:

- Review notes can survive page refresh.
- The same browser and page origin may retain previous review notes.
- If the local HTTP server is used, state is stored under that local address.

For sensitive content, clear review notes before publishing or demonstrating the page, or use a clean browser profile.

## Local Server Notes

`serve_reader.py` binds to:

```text
127.0.0.1
```

This is a local machine address.

Do not bind the server to a public or LAN-accessible address. The local server serves the project folder as its static file root.

## Converter Notes

The optional DOCX converter reads `.docx` files and generates Markdown.

The converter does not modify source files, but unknown Office documents are still not recommended. They may be large, malformed, or contain complex structures outside the current converter scope.

## Recommended Workflow

A safer workflow is:

```text
Confirm the source is trusted
  -> inspect read scope with dry-run
  -> build reader.html
  -> open locally
  -> export review.md
```

If you only want to inspect unfamiliar Markdown content, open it in a plain text editor first, then decide whether to package it into the reader.
