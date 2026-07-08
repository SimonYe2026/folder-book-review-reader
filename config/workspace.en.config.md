---
title: Local Markdown/TXT/CSV Review Reader Demo
locale: en
workspace_root: ..
source_dir: ./examples/basic/drafts
recursive: true
flatten: true
include:
  - "*.md"
  - "*.txt"
  - "*.csv"
exclude:
  - "*draft-private*"
order: natural
output: ./output/reader.en.html
overwrite: true
display:
  default_font_size: 18
  default_width: full
  theme: light
review:
  enabled: true
  shortcut: r
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
text:
  paragraph_mode: line
---

# English UI Example

This config demonstrates the internationalized English labels. The default project config uses Chinese.
