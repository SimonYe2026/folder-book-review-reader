---
title: 我的 Markdown/TXT/CSV 审阅阅读器
locale: zh-CN
workspace_root: .
source_dir: ./docs
recursive: true
flatten: true
include:
  - "*.md"
  - "*.txt"
  - "*.csv"
exclude:
  - "*private*"
  - "*secret*"
  - "review*.md"
order: natural
output: ./output/reader.html
overwrite: false
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

# 配置模板

这个文件是给其他 Markdown/TXT/CSV 项目复制使用的模板，不绑定本仓库的 demo 目录。

最小使用方式：

```powershell
Copy-Item workspace.template.config.md workspace.config.md
python build_reader.py workspace.config.md
```

复制到自己的项目后，通常只需要改：

- `title`：阅读器标题；
- `source_dir`：你的 Markdown/TXT/CSV 文件夹；
- `output`：生成的 HTML 路径；
- `review.actions` 和 `review.targets`：你的批复动作和目标。

默认 `workspace_root: .` 表示配置文件所在目录就是项目根目录。如果你把配置文件放在 `config/` 这样的子目录里，可以改成：

```yaml
workspace_root: ..
```

`source_dir` 和 `output` 都必须留在 `workspace_root` 内。

## English

This is a portable config template for other Markdown/TXT/CSV projects. It is not tied to this repository's demo folders.

Copy it to `workspace.config.md`, then adjust `title`, `source_dir`, `output`, review actions, and review targets.
