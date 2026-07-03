---
title: 本地 Markdown/TXT 审阅阅读器 Demo
locale: zh-CN
workspace_root: ..
source_dir: ./examples/basic/drafts
recursive: true
flatten: true
include:
  - "*.md"
  - "*.txt"
exclude:
  - "*draft-private*"
order: natural
output: ./output/reader.html
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
labels:
  search_placeholder: 搜索标题、路径或正文
  toc: 目录
  review_panel: 审阅板
  previous: 上一篇
  next: 下一篇
  add_review: 加入批复
  review: 批复
  copy_review: 复制 review.md
  clear: 清空
  download: 下载
tables:
  enabled: true
  sticky_header: true
  horizontal_scroll: true
  copy_button: false
stats:
  enabled: false
  show_file_count: true
  show_word_count: true
  show_folder_distribution: false
  show_ext_distribution: false
---

# 本地 Markdown/TXT 审阅阅读器 Demo

这是默认中文配置模板，适合直接复制后修改。

备注：

- `source_dir` 必须指向当前项目目录内的文件夹。
- 本仓库把配置集中放在 `config/` 下，所以这里使用 `workspace_root: ..` 指回项目根目录。
- `include` / `exclude` 支持多行列表，也支持 `exclude: []` 这种空列表写法。
- `order` 可选：`natural`、`natural_desc`、`modified_desc`。
- `text.paragraph_mode` 可选：`line` 表示一行一段，`blank_line` 表示空行分段。
- `locale: zh-CN` 是默认中文界面；英文示例见 `config/workspace.en.config.md`。
- `.docx` 来源请先用 `tools/convert_docs.py` 转成 `.md`，再用阅读器打包。
- `.doc`、`.rtf`、`.pdf`、`.epub` 不属于当前开源承诺。
