---
title: 本地 Markdown/TXT/CSV 审阅阅读器 Demo
locale: zh-CN
workspace_root: .
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

# 单配置示例

这个文件演示最简单的配置摆放方式：把 `workspace.config.md` 放在 `build_reader.py` 旁边，并使用：

```powershell
python build_reader.py workspace.config.md
```

本仓库的默认命令仍然使用 `config/workspace.config.md`，因为仓库本身有多个 demo 和文档配置需要集中管理。

两种方式都有效：

- 单配置项目：可以把 `workspace.config.md` 放在项目根目录。
- 多配置项目：可以把多个配置集中放进 `config/`，并使用 `workspace_root: ..` 指回项目根目录。
