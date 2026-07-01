# Customization Guide

This file explains how future contributors can modify the project and which boundaries should remain intact.

Chinese counterpart: `03-customization-guide.zh-CN.md`

## Minimal Mental Model

The project has only three layers:

```text
Config file
  -> Python build script
  -> self-contained HTML reader
```

The config decides where to read from, how to sort files, UI labels, and review options.

The Python script scans files, renders Markdown/TXT, and generates HTML.

The HTML reader handles browser-side reading, filtering, navigation, reviewing, and exporting.

## Embed in an Existing Project

This tool does not require users to adopt the full repository structure.

For a minimal integration into another project:

```text
copy build_reader.py
copy or create workspace.config.md
point source_dir to your md/txt folder
point output to your output folder
run python build_reader.py workspace.config.md
```

If you do not need DOCX conversion, you do not need to copy `tools/convert_docs.py`.

If you do not need local HTTP preview, you do not need to copy `serve_reader.py`.

Recommended embedded workflow:

```text
files from any source
  -> package as reader.html
  -> human review produces review.md
  -> AI edits or generates a new version based on review.md
  -> rebuild reader.html to inspect the result
```

## Common Customization Points

### Change Source Folder

Edit the config file:

```yaml
source_dir: ./examples/basic/drafts
recursive: true
include:
  - "*.md"
  - "*.txt"
exclude:
  - "*private*"
```

`source_dir` must stay inside the folder containing the config file.

### Change Output Path

```yaml
output: ./output/reader.html
overwrite: false
```

When `overwrite: false` and the target already exists, the script writes a timestamped file instead.

### Change UI Language

```yaml
locale: zh-CN
```

Or:

```yaml
locale: en
```

You can also override individual strings with `labels:`.

### Change Review Actions and Targets

```yaml
review:
  enabled: true
  actions:
    - revise
    - summarize
    - extract
    - register
  targets:
    - source paragraph
    - review queue
    - notes
    - todo list
```

The program does not need to interpret these fields as complex enums. They are exported into `review.md` for users or AI tools to understand.

### Change TXT Paragraph Mode

```yaml
text:
  paragraph_mode: line
```

Options:

- `line`: each non-empty line becomes a reviewable paragraph.
- `blank_line`: blank lines split paragraphs.

## Converter Extensions

The core reader only commits to `.md` / `.txt`.

For more formats, add independent converters:

```text
source.docx
  -> tools/convert_docs.py
  -> converted/source.docx.md
  -> build_reader.py
```

Do not make the browser parse local Office/PDF files directly.

## Rendering Rule Extensions

Markdown rendering rules can be extended in `build_reader.py`.

Prefer to keep:

- HTML output safe.
- Links disabled by default.
- Complex structures falling back to readable text.
- One bad file not breaking the whole project.

## Review Export Extensions

The exported `review.md` format can be adapted for team workflows.

The main logic lives in the embedded JavaScript `reviewMarkdown()` function.

Recommended fields to keep:

- File path.
- Title.
- Paragraph number.
- Action.
- Target.
- Original quote.
- User instruction.
- Created time.

These fields help AI tools or humans locate the context later.

## Boundaries Not Recommended for First Customizations

Avoid adding these to the default path in a first customization pass:

- Browser write-back to source files.
- Automatic AI API calls.
- Automatic merging of AI edits.
- Background service dependency.
- npm frontend build chain.
- Complex chart libraries.

These can be explored in separate branches, but they do not fit the default path of this small tool.

## What a Good Custom Version Looks Like

A good custom version should:

- Still build with one command.
- Still keep source files read-only.
- Still validate the core path with the smoke test.
- Explain its changes in README.
- Include examples that help strangers understand the use case quickly.
