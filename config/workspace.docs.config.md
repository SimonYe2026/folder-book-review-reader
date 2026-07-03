---
title: Local Markdown/TXT Review Reader Docs
locale: zh-CN
workspace_root: ..
source_dir: .
recursive: true
flatten: true
include:
  - "README.md"
  - "README.zh-CN.md"
  - "docs/*.md"
exclude:
  - "examples/*"
  - "tools/*"
  - "tests/*"
  - "__pycache__/*"
  - "output/*"
order: natural
output: ./output/project-docs.html
overwrite: true
display:
  show_file_name: true
  show_word_count: true
  default_font_size: 18
  default_width: full
  theme: light
features:
  search: true
  next_prev: true
  keyboard_nav: true
  reverse_order: true
review:
  enabled: true
  shortcut: r
  actions:
    - 修改
    - 总结
    - 提取
    - 登记
  targets:
    - 原文段落
    - 审阅队列
    - 笔记
    - 待办清单
text:
  paragraph_mode: line
tables:
  enabled: true
  sticky_header: true
  horizontal_scroll: true
  copy_button: false
stats:
  enabled: false
---

# Documentation Reader Config

This config packages the project documentation files in `docs/` into one local reader.
