# Review Handoff Workflow

This document explains how to organize a file-review handoff with the current Reader. It is for workflow owners, coordinators, and review participants. Review participants do not need Python, AI, source folders, or source code access.

Chinese counterpart: `07-review-handoff-workflow.zh-CN.md`

## When to Use It

When one review round involves dozens, or even ninety-plus, Markdown, TXT, or CSV materials, sending a zip archive or shared folder leaves reviewers to understand the directory, open files one by one, and describe locations through chat messages.

Reader packages a selected scope into a self-contained `reader.html`. Reviewers can read, search, filter, and leave notes in a browser, then return located feedback through `review.md`.

## Two Roles

### Workflow Owner or Coordinator

The central side is responsible for:

- choosing the material scope for a review round;
- generating one or more `reader.html` files from configuration files;
- distributing packages by batch, role, topic, round, or viewing scope;
- collecting returned `review.md` files;
- organizing feedback, maintaining source files, and deciding whether to send material to an external AI workflow;
- generating the next review round when needed.

### Review Participant

Review participants only need to:

- open the received `reader.html` in a modern browser;
- read, search, and filter the material assigned to them;
- leave judgments on specific content blocks;
- export `review.md` and return it as agreed.

They do not need Python, project dependencies, access to source folders, or responsibility for merging notes or editing source files.

## Basic Handoff Flow

```text
Central side chooses the material scope
  -> generates reader.html
  -> distributes the review package

Review participants read, judge, and leave notes
  -> export review.md
  -> return it to the central side

Central side organizes feedback
  -> maintains source files or sends material to an external AI workflow
  -> generates the next reader.html when needed
```

## Package Scopes with Config Files

One configuration file can define the source, matching scope, and output location for one review package. Different configs can represent different batches or viewing scopes:

```yaml
workspace_root: ..
source_dir: ./review-batches/batch-a
include:
  - "*.md"
  - "*.txt"
  - "*.csv"
output: ./output/batch-a.reader.html
```

Folder organization and matching rules can also produce packages for different topics, roles, or rounds. A config decides not only which files enter a package, but also the material combination and reading order a reviewer receives.

Once a static HTML package is distributed, the recipient can read its embedded content. Confirm the scope before building and include only material that reviewer is allowed to hold as a copy.

## Precise Notes and Rechecking

Reviewers can leave notes on paragraphs, list items, blockquotes, TXT lines, and CSV rows. Each exported note retains:

- file path;
- content-block position;
- original quote;
- action;
- target;
- instruction.

Review-board items can return to the original position and briefly highlight it. Bookmarks can mark a content block for later rechecking. The central side therefore receives a judgment that can be located again, rather than a chat message saying only that something is wrong.

## Multi-Party Review Conventions

Several reviewers or a small team can review separate packages in parallel. To keep returns clear, agree before distribution on:

- the batch or round for each package;
- the scope assigned to each reviewer;
- return-file naming;
- the return deadline;
- who organizes and accepts feedback on the central side.

For example, a reviewer can rename a downloaded `review.md` according to the current agreement:

```text
review_round-01_batch-A_reviewer-zhangsan.md
```

Reviewer, batch, and round names in file names are workflow conventions; Reader does not automatically write them into the export.

## After a Review Round

Review participants should export `review.md` before finishing. The browser temporarily stores notes in local `localStorage`, but the exported return is the transferable, backupable handoff artifact.

After receiving returns, the central side can organize them by file and issue, then maintain source files or enter its own follow-up process. The browser never writes back to source files directly.
