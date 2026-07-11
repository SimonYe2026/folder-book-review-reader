# User Manual

This file is for end users. It explains the reader interface, shortcuts, review board, and export flow.

Chinese counterpart: `04-user-manual.zh-CN.md`

## Build the Reader

Run this command in the project folder:

```powershell
python build_reader.py
```

Generated file:

```text
output/reader.html
```

You can also start the optional local preview server:

```powershell
python serve_reader.py
```

Default address:

```text
http://127.0.0.1:8766/output/reader.html
```

## Minimum Reviewer Requirements

The builder and central side run Python packaging, intake/merging, AI handling, source edits, and final acceptance. Reviewers only read, make judgments, leave review notes, and export returns; they do not need Python, project dependencies, access to the source folder, AI knowledge, or prompt-writing skills.

After receiving `reader.html`, they only need a modern browser to read, filter, add review notes, and export `review.md`. Notes are temporarily stored in the current browser, so reviewers should export `review.md` after a review round and return it to the coordinator or later maintenance process.

## Interface Layout

The reader has three main columns:

- Left: contents and bookmarks panel.
- Center: reading area.
- Right: review board.

The contents panel and review board can both be collapsed. Their widths can be resized by dragging and are saved in local browser state.

## Top Toolbar

The top toolbar contains:

- Search box.
- File type filter.
- Ascending/descending order toggle.
- Font size controls.
- Reading width controls.
- Dark/light mode toggle.
- Reset layout button.
- Contents panel toggle.
- Review board toggle.

Search matches:

- Title.
- File name.
- Relative path.
- Body content.

Filtered results become a temporary reading list. Previous and next navigation only move within the current filtered result set.

## Keyboard Shortcuts

Current shortcuts:

| Shortcut | Action |
| --- | --- |
| `A` | Previous file |
| `←` | Previous file |
| `D` | Next file |
| `→` | Next file |
| `B` | Add or remove the current-position bookmark |
| `R` | Open review dialog |

When focus is inside an input, select, or textarea, these shortcuts do not trigger navigation, bookmarking, or the review dialog.

In browsers such as Microsoft Edge, selecting text may show the browser's own mini menu. That menu can cover the page or capture key input, so pressing `R` after selecting text may not always open the review dialog. Firefox usually does not show this issue. If it happens, click the floating review button or the review button beside a paragraph.

## Reading Settings

You can adjust:

- Font size.
- Reading width.
- Dark/light mode.
- Contents panel width.
- Review board width.
- Whether the contents panel and review board are collapsed.

These settings are saved in browser `localStorage`. They are restored after refresh.

The reset layout button resets reading layout preferences but does not delete review notes or bookmarks.

## Bookmarks

Bookmarks are saved for the current content block, not for the whole file. You can bookmark headings, paragraphs, list items, blockquotes, code blocks, Markdown tables, converted DOCX tables, TXT lines, and CSV rows.

- Click **Add Bookmark** in the middle of the fixed bottom navigation to save the current position; click it again at the same position to remove the bookmark. You can also press `B`.
- After directly clicking a content block, adding a bookmark prioritizes that block. Without an explicit content-block click, the reader uses the center of the visible reading area to determine the current position.
- Scrolling the reading area clears the earlier content-block bookmark target, so adding a bookmark at a new position does not accidentally remove the old one.
- When no text is selected and no content-block button explicitly supplies a target, bookmarks and review notes use the content block nearest the center of the visible reading area. Scroll the intended position to the middle of the reader, then press `B` or `R`; CSV still prioritizes its active row.
- Switch between **Contents** and **Bookmarks** with the buttons in the left panel. This only changes the left-panel view; it does not change search terms, file-type filters, or saved bookmarks.
- Click a bookmark to return to its file and content block. The target is highlighted briefly.
- Each bookmark has its own **Delete** button. The top-right of the bookmarks view also provides **Clear bookmarks**, with a confirmation before every bookmark is removed.
- If the current search or file-type filter hides the target file, the reader clears those filters before navigating.

Bookmarks are stored only in the current browser's `localStorage`. They are not written to source files and are not included in exported `review.md` files.

## Locate and Recheck

Each review note records its file path, content-block position, original quote, action, target, and instruction. Selecting text or using a content-block **Review** button marks the scope as a precise object. Pressing `R` or the floating review button with no selected text marks the scope as a **reading viewport**, where the core quote is an anchor only. The review board and exported `review.md` include nearby context for that scope, with a range such as `Nearby blocks 2-4`. This lets a later human or AI use the instruction to identify the real work item without guessing the intent of an entire chapter. Click a review item in the review board to return to its file and briefly highlight the core target.

The reader can locate headings, ordinary paragraphs, list items, blockquotes, code blocks, Markdown tables, converted DOCX tables, TXT lines, and CSV rows. A CSV cell selection returns to its starting row. If a search or file-type filter hides the target file, the reader makes that file visible before navigating.

Use bookmarks to mark a location you want to revisit. Use review notes to record a judgment that should return to the central maintenance process. Both can lead back to the source from the left bookmarks panel or the right review board.

## Add Review Notes

There are two ways to add a review note:

- Select text and click the floating review button, or press `R`.
- Click the review button beside a content block.

If text is selected, the review dialog uses the selected text as the quote.

If no text is selected, the review dialog uses the current paragraph.

## CSV Tables

CSV files are shown as table chapters.

- The first row is used as the table header.
- Data rows are shown as HTML table rows.
- Tables can scroll horizontally.
- Search can match headers and cell content.
- Each data row can receive a review note.

When reviewing CSV content:

- If cell or row text is selected, the selected text is used as the quote.
- If a CSV cell range is selected, the position tries to include both row and column ranges.
- If no text is selected, the current row is used as the quote.
- The exported `review.md` shows the position as `row N`.

The reader does not edit CSV in the browser and does not write back to CSV source files. CSV edits still happen outside the reader, by the user or a later AI-assisted workflow.

The review dialog contains:

- Original quote.
- Action.
- Target.
- User instruction.

Actions and targets come from the config file and can be adapted to your workflow.

## Review Board

The review board shows all current review notes.

It supports:

- Clicking a review item to return to its file and paragraph, list item, blockquote, TXT line, or CSV row.
- Editing action.
- Editing target.
- Editing user instruction.
- Deleting one review note.
- Clearing all review notes.
- Copying `review.md`.
- Downloading `review.md`.

When editing a review note in the board, the original quote is not modified.

## Exported review.md

The exported `review.md` is grouped by file.

Each review note usually includes:

- File path.
- Title.
- Paragraph position or CSV row position.
- Action.
- Target.
- Time.
- Original quote.
- User instruction.

This file can be given to AI or used as a manual editing checklist.

Recommended usage:

```text
Copy or download review.md
  -> paste it into AI, or provide it to AI as a file
  -> ask AI to propose edits or generate a revised version
  -> confirm the result before editing source files
```

The reader does not perform these edits automatically.

The full loop can be:

```text
files from any source
  -> package reader.html
  -> human reading and review
  -> export review.md
  -> AI edits source files or generates a new version based on review notes
  -> package reader.html again
  -> human acceptance
```

## Repackage review.md

Downloaded `review.md` files can be placed in a folder and packaged by the reader again.

This is useful for:

- Rereading review notes.
- Archiving review notes.
- Second-pass review.
- Combining multiple review files into one searchable reader.

This flow does not promise reversible structure. It only promises that the file remains readable, searchable, and reviewable as normal Markdown.

## Links and Images

Markdown links are disabled by default.

The reader shows:

```text
(Unknown link, check the source file)
```

This prevents external or AI-generated Markdown from activating untrusted links in the browser.

Images have basic display support. Data URL images generated by converters can enter the reader, but image extraction quality from complex documents depends on the converter.

## FAQ

### Why does the page not change after I add source files?

Run the build command again.

The reader HTML is a packaged artifact. It does not watch the folder automatically.

### Why can the browser not read the current folder directly?

Browsers cannot silently scan local folders because of security restrictions.

The current design is:

```text
Python reads local files
  -> HTML handles reading and interaction
```

### Why not edit source files directly?

For safety and control.

The reader only creates side-channel review files. Source edits are left to the user or a later AI-assisted workflow.
